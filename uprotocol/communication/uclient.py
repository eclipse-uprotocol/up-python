"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.inmemoryrpcclient import InMemoryRpcClient
from uprotocol.communication.inmemoryrpcserver import InMemoryRpcServer
from uprotocol.communication.notifier import Notifier
from uprotocol.communication.publisher import Publisher
from uprotocol.communication.rpcclient import RpcClient
from uprotocol.communication.rpcserver import RpcServer
from uprotocol.communication.simplenotifier import SimpleNotifier
from uprotocol.communication.simplepublisher import SimplePublisher
from uprotocol.communication.upayload import UPayload
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class UClient(RpcServer, Notifier, Publisher, RpcClient):
    """
    UClient provides a unified interface for various communication patterns over a UTransport instance,
    including RPC, subscriptions, notifications, and message publishing. It combines functionalities
    from RpcServer, Subscriber, Notifier, Publisher, and RpcClient, allowing for comprehensive and
    asynchronous operations such as subscribing to topics, publishing messages, sending notifications,
    and invoking remote methods.

    Attributes:
        transport (UTransport): The underlying transport mechanism.
        rpc_server (InMemoryRpcServer): Handles incoming RPC requests.
        publisher (SimplePublisher): Sends messages to topics.
        notifier (SimpleNotifier): Sends notifications to destinations.
        rpc_client (InMemoryRpcClient): Invokes remote methods.
        subscriber (InMemorySubscriber): Manages topic subscriptions.
    """

    def __init__(self, transport: UTransport):
        self.transport = transport
        if transport is None:
            raise ValueError(UTransport.TRANSPORT_NULL_ERROR)
        elif not isinstance(transport, UTransport):
            raise ValueError(UTransport.TRANSPORT_NOT_INSTANCE_ERROR)

        self.rpc_server = InMemoryRpcServer(self.transport)
        self.publisher = SimplePublisher(self.transport)
        self.notifier = SimpleNotifier(self.transport)
        self.rpc_client = InMemoryRpcClient(self.transport)

    async def notify(
        self, topic: UUri, destination: UUri, options: Optional[CallOptions] = None, payload: Optional[UPayload] = None
    ) -> UStatus:
        """
        Send a notification to a given topic.

        :param topic: The topic to send the notification to.
        :param destination: The destination to send the notification to.
        :param options: Call options for the notification.
        :param payload: The payload to send with the notification.
        :return: Returns the UStatus with the status of the notification.
        """
        return await self.notifier.notify(topic, destination, options, payload)

    async def register_notification_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Register a listener for a notification topic.

        :param topic: The topic to register the listener to.
        :param listener: The listener to be called when a message is received on the topic.
        :return: Returns the UStatus with the status of the listener registration.
        """
        return await self.notifier.register_notification_listener(topic, listener)

    async def unregister_notification_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Unregister a listener from a notification topic.

        :param topic: The topic to unregister the listener from.
        :param listener: The listener to be unregistered from the topic.
        :return: Returns the UStatus with the status of the listener that was unregistered.
        """
        return await self.notifier.unregister_notification_listener(topic, listener)

    async def publish(
        self, topic: UUri, options: Optional[CallOptions] = None, payload: Optional[UPayload] = None
    ) -> UStatus:
        """
        Publishes a message to a topic using the provided payload.

        :param topic: The topic to publish the message to.
        :param options: Call options for the publish.
        :param payload: The payload to be published.
        :return: An instance of UStatus indicating the status of the publish operation.
        """
        return await self.publisher.publish(topic, options, payload)

    async def register_request_handler(self, method_uri: UUri, handler):
        """
        Register a handler that will be invoked when requests come in from clients for the given method.

        Note: Only one handler is allowed to be registered per method URI.

        :param method_uri: The URI for the method to register the listener for.
        :param handler: The handler that will process the request for the client.
        :return: Returns the status of registering the RpcListener.
        """
        return await self.rpc_server.register_request_handler(method_uri, handler)

    async def unregister_request_handler(self, method_uri: UUri, handler):
        """
        Unregister a handler that will be invoked when requests come in from clients for the given method.

        :param method_uri: The resolved UUri where the listener was registered to receive messages from.
        :param handler: The handler for processing requests.
        :return: Returns the status of unregistering the RpcListener.
        """
        return await self.rpc_server.unregister_request_handler(method_uri, handler)

    async def invoke_method(
        self, method_uri: UUri, request_payload: UPayload, options: Optional[CallOptions] = None
    ) -> UPayload:
        """
        Invoke a method (send an RPC request) and receive the response asynchronously.
        Ensures that the listener is registered before proceeding with the method invocation.
        If the listener is not registered, it attempts to register it and raises an exception
        if the registration fails.

        :param method_uri: The method URI to be invoked.
        :param request_payload: The request message to be sent to the server.
        :param options: RPC method invocation call options. Defaults to None.
        :return: Returns the asyncio Future with the response payload or raises an exception
                 with the failure reason as UStatus.
        """
        return await self.rpc_client.invoke_method(method_uri, request_payload, options)

    def close(self):
        if self.rpc_client:
            self.rpc_client.close()
