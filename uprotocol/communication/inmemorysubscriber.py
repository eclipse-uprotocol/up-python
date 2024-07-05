"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import asyncio

from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.rpcclient import RpcClient
from uprotocol.communication.rpcmapper import RpcMapper
from uprotocol.communication.subscriber import Subscriber
from uprotocol.communication.upayload import UPayload
from uprotocol.core.usubscription.v3 import usubscription_pb2
from uprotocol.core.usubscription.v3.usubscription_pb2 import (
    SubscriberInfo,
    SubscriptionRequest,
    SubscriptionResponse,
    UnsubscribeRequest,
    UnsubscribeResponse,
)
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.uri.factory.uri_factory import UriFactory
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class InMemorySubscriber(Subscriber):
    """
    The following is an example implementation of the Subscriber interface that
    wraps the UTransport for implementing the Subscriber-side of the pub/sub
    messaging pattern to allow developers to subscribe and unsubscribe to topics.
    This implementation uses the InMemoryRpcClient to send the subscription request
    to the uSubscription service.

    NOTE: Developers are not required to use these APIs, they can implement their own
          or directly use the UTransport to communicate with the uSubscription
          services and register their publish message listener.
    """

    METHOD_SUBSCRIBE = 1  # TODO: Fetch this from proto generated code
    METHOD_UNSUBSCRIBE = 2  # TODO: Fetch this from proto generated code

    def __init__(self, transport: UTransport, rpc_client: RpcClient):
        """
        Constructor for the DefaultSubscriber.

        :param transport: The transport to use for sending the notifications
        :param rpc_client: The RPC client to use for sending the RPC requests
        """
        if not transport:
            raise ValueError(UTransport.TRANSPORT_NULL_ERROR)
        elif not isinstance(transport, UTransport):
            raise ValueError(UTransport.TRANSPORT_NOT_INSTANCE_ERROR)
        elif not rpc_client:
            raise ValueError("RpcClient missing")
        self.transport = transport
        self.rpc_client = rpc_client

    async def subscribe(self, topic: UUri, listener: UListener, options: CallOptions) -> SubscriptionResponse:
        """
        Subscribe to a given topic.

        The API will return a future with the response SubscriptionResponse or exception
        with the failure if the subscription was not successful. The API will also register the listener to be
        called when messages are received.

        :param topic: The topic to subscribe to.
        :param listener: The listener to be called when a message is received on the topic.
        :param options: The call options for the subscription.
        :return: Returns the future with the response SubscriptionResponse or
        exception with the failure reason as UStatus.
        """
        if not topic:
            raise ValueError("Subscribe topic missing")
        if not listener:
            raise ValueError("Request listener missing")
        service_descriptor = usubscription_pb2.DESCRIPTOR.services_by_name["uSubscription"]

        subscribe_uri = UriFactory.from_proto(service_descriptor, self.METHOD_SUBSCRIBE, None)
        request = SubscriptionRequest(topic=topic, subscriber=SubscriberInfo(uri=self.transport.get_source()))
        future_result = asyncio.ensure_future(
            self.rpc_client.invoke_method(subscribe_uri, UPayload.pack(request), options)
        )

        response_future = RpcMapper.map_response(future_result, SubscriptionResponse)

        response = await response_future
        await self.transport.register_listener(topic, listener)
        return response

    async def unsubscribe(self, topic: UUri, listener: UListener, options: CallOptions) -> UStatus:
        """
        Unsubscribe to a given topic.

        The subscriber no longer wishes to be subscribed to said topic so we issue an unsubscribe
        request to the USubscription service.

        :param topic: The topic to unsubscribe to.
        :param listener: The listener to be called when a message is received on the topic.
        :param options: The call options for the subscription.
        :return: Returns UStatus with the result from the unsubscribe request.
        """
        if not topic:
            raise ValueError("Unsubscribe topic missing")
        if not listener:
            raise ValueError("Listener missing")
        service_descriptor = usubscription_pb2.DESCRIPTOR.services_by_name["uSubscription"]
        unsubscribe_uri = UriFactory.from_proto(service_descriptor, self.METHOD_UNSUBSCRIBE, None)
        unsubscribe_request = UnsubscribeRequest(topic=topic)
        future_result = asyncio.ensure_future(
            self.rpc_client.invoke_method(unsubscribe_uri, UPayload.pack(unsubscribe_request), options)
        )
        response_future = RpcMapper.map_response_to_result(future_result, UnsubscribeResponse)
        response = await response_future
        if response.is_success():
            await self.transport.unregister_listener(topic, listener)
            return UStatus(code=UCode.OK)
        return response.failure_value()

    async def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Unregister a listener from a topic.

        This method will only unregister the listener for a given subscription thus allowing a uE to stay
        subscribed even if the listener is removed.

        :param topic: The topic to subscribe to.
        :param listener: The listener to be called when a message is received on the topic.
        :return: Returns UStatus with the status of the listener unregister request.
        """
        if not topic:
            raise ValueError("Unsubscribe topic missing")
        if not listener:
            raise ValueError("Request listener missing")
        return await self.transport.unregister_listener(topic, listener)
