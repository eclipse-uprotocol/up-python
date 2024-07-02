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
from uprotocol.communication.inmemorysubscriber import InMemorySubscriber
from uprotocol.communication.notifier import Notifier
from uprotocol.communication.publisher import Publisher
from uprotocol.communication.rpcclient import RpcClient
from uprotocol.communication.rpcserver import RpcServer
from uprotocol.communication.simplenotifier import SimpleNotifier
from uprotocol.communication.simplepublisher import SimplePublisher
from uprotocol.communication.subscriber import Subscriber
from uprotocol.communication.upayload import UPayload
from uprotocol.core.usubscription.v3.usubscription_pb2 import (
    SubscriptionResponse,
)
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class UClient(RpcServer, Subscriber, Notifier, Publisher, RpcClient):
    def __init__(self, transport: UTransport):
        self.transport = transport
        if transport is None:
            raise ValueError(UTransport.TRANSPORT_NULL_ERROR)
        elif not isinstance(transport, UTransport):
            raise ValueError(UTransport.TRANSPORT_NOT_INSTANCE_ERROR)

        self.rpcServer = InMemoryRpcServer(self.transport)
        self.publisher = SimplePublisher(self.transport)
        self.notifier = SimpleNotifier(self.transport)
        self.rpcClient = InMemoryRpcClient(self.transport)
        self.subscriber = InMemorySubscriber(self.transport, self.rpcClient)

    async def subscribe(self, topic: UUri, listener: UListener, options: CallOptions) -> SubscriptionResponse:
        return await self.subscriber.subscribe(topic, listener, options)

    def unsubscribe(self, topic: UUri, listener: UListener, options: CallOptions) -> UStatus:
        return self.subscriber.unsubscribe(topic, listener, options)

    def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        return self.subscriber.unregister_listener(topic, listener)

    def notify(self, topic: UUri, destination: UUri, payload: UPayload) -> UStatus:
        return self.notifier.notify(topic, destination, payload)

    def register_notification_listener(self, topic: UUri, listener: UListener) -> UStatus:
        return self.notifier.register_notification_listener(topic, listener)

    def unregister_notification_listener(self, topic: UUri, listener: UListener) -> UStatus:
        return self.notifier.unregister_notification_listener(topic, listener)

    def publish(self, topic: UUri, payload: UPayload) -> UStatus:
        return self.publisher.publish(topic, payload)

    def register_request_handler(self, method: UUri, handler):
        return self.rpcServer.register_request_handler(method, handler)

    def unregister_request_handler(self, method: UUri, handler):
        return self.rpcServer.unregister_request_handler(method, handler)

    async def invoke_method(
        self, method_uri: UUri, request_payload: UPayload, options: Optional[CallOptions] = None
    ) -> UPayload:
        return await self.rpcClient.invoke_method(method_uri, request_payload, options)
