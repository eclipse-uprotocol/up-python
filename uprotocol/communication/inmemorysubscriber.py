"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from typing import Dict, Optional

from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.notifier import Notifier
from uprotocol.communication.rpcclient import RpcClient
from uprotocol.communication.rpcmapper import RpcMapper
from uprotocol.communication.subscriber import Subscriber
from uprotocol.communication.subscriptionchangehandler import SubscriptionChangeHandler
from uprotocol.communication.upayload import UPayload
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.core.usubscription.v3 import usubscription_pb2
from uprotocol.core.usubscription.v3.usubscription_pb2 import (
    SubscriberInfo,
    SubscriptionRequest,
    SubscriptionResponse,
    SubscriptionStatus,
    UnsubscribeRequest,
    UnsubscribeResponse,
    Update,
)
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.uri.factory.uri_factory import UriFactory
from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.v1.uattributes_pb2 import UMessageType
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class MyNotificationListener(UListener):
    def __init__(self, handlers):
        self.handlers = handlers

    def on_receive(self, message: UMessage) -> None:
        """
        Handles incoming notifications from the USubscription service.

        :param message: The notification message from the USubscription service.
        """
        if message.attributes.type != UMessageType.UMESSAGE_TYPE_NOTIFICATION:
            return

        subscription_update = UPayload.unpack_data_format(message.payload, message.attributes.payload_format, Update)

        if subscription_update:
            handler = self.handlers.get(UriSerializer.serialize(subscription_update.topic))
            # Check if we have a handler registered for the subscription change notification
            # for the specific topic that triggered the subscription change notification.
            # It is possible that the client did not register one initially (i.e., they don't care to receive it).
            if handler:
                try:
                    handler.handle_subscription_change(subscription_update.topic, subscription_update.status)
                except Exception:
                    pass


class InMemorySubscriber(Subscriber):
    """
    The following is an in-memory implementation of the Subscriber interface that
    wraps the UTransport for implementing the Subscriber-side of the pub/sub
    messaging pattern to allow developers to subscribe and unsubscribe to topics.
    This implementation uses the InMemoryRpcClient and SimpleNotifier interfaces
    to invoke the subscription request message to the usubscription service, and register
    to receive notifications for changes from the uSubscription service.
    """

    def __init__(self, transport: UTransport, rpc_client: RpcClient, notifier: Notifier):
        """
        Creates a new subscriber for existing Communication Layer client implementations.

        :param transport: The transport to use for sending the notifications
        :param rpc_client: The RPC client to use for sending the RPC requests
        :param notifier: The notifier to register notification listeners
        """
        if not transport:
            raise ValueError(UTransport.TRANSPORT_NULL_ERROR)
        elif not isinstance(transport, UTransport):
            raise ValueError(UTransport.TRANSPORT_NOT_INSTANCE_ERROR)
        elif not rpc_client:
            raise ValueError("RpcClient missing")
        elif not notifier:
            raise ValueError("Notifier missing")
        self.transport = transport
        self.rpc_client = rpc_client
        self.notifier = notifier
        self.handlers: Dict[str, SubscriptionChangeHandler] = {}
        self.notification_handler: UListener = MyNotificationListener(self.handlers)
        self.is_listener_registered = False
        service_descriptor = usubscription_pb2.DESCRIPTOR.services_by_name["uSubscription"]
        self.notification_uri = UriFactory.from_proto(service_descriptor, 0x8000)
        self.subscribe_uri = UriFactory.from_proto(service_descriptor, 1)
        self.unsubscribe_uri = UriFactory.from_proto(service_descriptor, 2)

    async def subscribe(
        self,
        topic: UUri,
        listener: UListener,
        options: CallOptions = None,
        handler: Optional[SubscriptionChangeHandler] = None,
    ) -> SubscriptionResponse:
        """
        Subscribes to a given topic.

        This method subscribes to the specified topic and returns an async operation (typically a coroutine) that
        yields a SubscriptionResponse upon successful subscription or raises an exception if the subscription fails.
        The optional handler parameter, if provided, handles notifications of changes in subscription states,
        such as from SubscriptionStatus.State.SUBSCRIBE_PENDING to SubscriptionStatus.State.SUBSCRIBED, which occurs
        when we subscribe to remote topics that the device we are on has not yet a subscriber that has subscribed
        to said topic.

        NOTE: Calling this method multiple times with different handlers will result in UCode.ALREADY_EXISTS being
        returned.

        :param topic: The topic to subscribe to.
        :param listener: The listener function to be called when a message is received on the topic.
        :param options: Optional call options for the subscription.
        :param handler: Optional handler function for handling subscription state changes.
        :return: An async operation that yields a SubscriptionResponse upon success or raises an exception with
                 the failure reason as UStatus. UCode.ALREADY_EXISTS will be returned if called multiple times
                 with different handlers.
        """
        if not topic:
            raise ValueError("Subscribe topic missing")
        if not listener:
            raise ValueError("Request listener missing")

        if not self.is_listener_registered:
            # Ensure listener is registered before proceeding
            status = await self.notifier.register_notification_listener(
                self.notification_uri, self.notification_handler
            )
            if status.code != UCode.OK:
                raise UStatusError.from_code_message(status.code, "Failed to register listener for rpc client")
            self.is_listener_registered = True

        request = SubscriptionRequest(topic=topic, subscriber=SubscriberInfo(uri=self.transport.get_source()))
        # Send the subscription request and handle the response

        future_result = self.rpc_client.invoke_method(self.subscribe_uri, UPayload.pack(request), options)

        response = await RpcMapper.map_response(future_result, SubscriptionResponse)
        if (
            response.status.state == SubscriptionStatus.State.SUBSCRIBED
            or response.status.state == SubscriptionStatus.State.SUBSCRIBE_PENDING
        ):
            # If registering the listener fails, we end up in a situation where we have
            # successfully (logically) subscribed to the topic via the USubscription service,
            # but we have not been able to register the listener with the local transport.
            # This means that events might start getting forwarded to the local authority
            # but are not being consumed. Apart from this inefficiency, this does not pose
            # a real problem. Since we return a failed future, the client might be inclined
            # to try again and (eventually) succeed in registering the listener as well.
            await self.transport.register_listener(topic, listener)

        if handler:
            topic_str = UriSerializer.serialize(topic)
            if topic_str in self.handlers and self.handlers[topic_str] != handler:
                raise UStatusError.from_code_message(UCode.ALREADY_EXISTS, "Handler already registered")
            self.handlers[topic_str] = handler
        return response

    async def unsubscribe(self, topic: UUri, listener: UListener, options: CallOptions = None) -> UStatus:
        """
        Unsubscribes from a given topic.

        This method unsubscribes from the specified topic. It sends an unsubscribe request to the USubscription service
        and returns an async operation (typically a coroutine) that yields a UStatus indicating the result of the
        unsubscribe operation. If the unsubscribe operation fails with the USubscription service, the listener and
        handler (if any) will remain registered.

        :param topic: The topic to unsubscribe from.
        :param listener: The listener function associated with the topic.
        :param options: Optional call options for the subscription.
        :return: An async operation that yields a UStatus indicating the result of the unsubscribe request.
        """
        if not topic:
            raise ValueError("Unsubscribe topic missing")
        if not listener:
            raise ValueError("Listener missing")
        unsubscribe_request = UnsubscribeRequest(topic=topic)
        future_result = self.rpc_client.invoke_method(self.unsubscribe_uri, UPayload.pack(unsubscribe_request), options)

        response = await RpcMapper.map_response_to_result(future_result, UnsubscribeResponse)
        if response.is_success():
            self.handlers.pop(UriSerializer.serialize(topic), None)
            return await self.transport.unregister_listener(topic, listener)
        return response.failure_value()

    async def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Unregisters a listener and removes any registered SubscriptionChangeHandler for the topic.

        This method removes the specified listener and any associated SubscriptionChangeHandler without
        notifying the uSubscription service. This allows persistent subscription even when the uE (micro E)
        is not running.

        :param topic: The topic to unregister from.
        :param listener: The listener function associated with the topic.
        :return: An async operation that yields a UStatus indicating the status of the listener unregister request.
        """
        if not topic:
            raise ValueError("Unsubscribe topic missing")
        if not listener:
            raise ValueError("Request listener missing")
        return await self.transport.unregister_listener(topic, listener)

    def close(self):
        """
        Close the InMemoryRpcClient by clearing stored requests and unregistering the listener.
        """
        self.handlers.clear()
        self.notifier.unregister_notification_listener(self.notification_uri, self.notification_handler)
