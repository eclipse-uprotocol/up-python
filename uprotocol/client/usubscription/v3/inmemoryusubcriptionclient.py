""" SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

from uprotocol.client.usubscription.v3.subscriptionchangehandler import SubscriptionChangeHandler
from uprotocol.client.usubscription.v3.usubscriptionclient import USubscriptionClient
from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.rpcmapper import RpcMapper
from uprotocol.communication.inmemoryrpcclient import InMemoryRpcClient
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.core.usubscription.v3 import usubscription_pb2
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.v1 import ucode_pb2 as UCode
from uprotocol.v1 import ustatus_pb2 as UStatusModule
from uprotocol.v1 import uri_pb2 as UUri


class InMemoryUSubscriptionClient(USubscriptionClient):
    def __init__(self, transport: UTransport, rpc_client: InMemoryRpcClient):
        self.transport = transport
        self.rpc_client = rpc_client
        self.notification_uri = None
        self.notification_handler = None
        self.notifier = None
        self.is_listener_registered = False

    async def subscribe(self, topic: UUri, listener: UListener, options: CallOptions = CallOptions.DEFAULT,
                        handler: Optional[SubscriptionChangeHandler] = None) -> usubscription_pb2.SubscriptionResponse:
        if not topic:
            raise ValueError("Subscribe topic missing")
        if not listener:
            raise ValueError("Request listener missing")
        if not options:
            raise ValueError("CallOptions missing")

        if not self.is_listener_registered and self.notifier:
            status = await self.notifier.register_notification_listener(self.notification_uri, self.notification_handler)
            if status.code != UCode.OK:
                raise UStatusError(status, "Failed to register notification listener")

            self.is_listener_registered = True

        request = usubscription_pb2.SubscriptionRequest(topic=topic)
        response = await RpcMapper.map_response(
            self.rpc_client.invoke_method("usubscription.Subscribe", request, options),
            usubscription_pb2.SubscriptionResponse
        )
        return response

    async def unsubscribe(self, topic: UUri, listener: UListener,
                          options: CallOptions = CallOptions.DEFAULT) -> UStatusModule.UStatus:
        if not topic:
            raise ValueError("Unsubscribe topic missing")
        if not listener:
            raise ValueError("Listener missing")
        if not options:
            raise ValueError("CallOptions missing")

        request = usubscription_pb2.UnsubscribeRequest(topic=topic)
        response = await RpcMapper.map_response(
            self.rpc_client.invoke_method("usubscription.Unsubscribe", request, options),
            UStatusModule.UStatus
        )
        return response

    async def register_for_notifications(self, topic: UUri, handler: SubscriptionChangeHandler,
                                         options: Optional[CallOptions] = CallOptions.DEFAULT) -> UStatusModule.UStatus:
        if not topic:
            raise ValueError("Topic missing")
        if not handler:
            raise ValueError("Handler missing")
        if not options:
            raise ValueError("CallOptions missing")

        request = usubscription_pb2.NotificationsRequest(topic=topic)
        response = await RpcMapper.map_response(
            self.rpc_client.invoke_method("usubscription.RegisterForNotifications", request, options),
            UStatusModule.UStatus
        )
        return response

    async def unregister_for_notifications(self, topic: UUri, handler: SubscriptionChangeHandler,
                                           options: Optional[CallOptions] = CallOptions.DEFAULT) -> UStatusModule.UStatus:
        if not topic:
            raise ValueError("Topic missing")
        if not handler:
            raise ValueError("Handler missing")
        if not options:
            raise ValueError("CallOptions missing")

        request = usubscription_pb2.NotificationsRequest(topic=topic)
        response = await RpcMapper.map_response(
            self.rpc_client.invoke_method("usubscription.UnregisterForNotifications", request, options),
            UStatusModule.UStatus
        )
        return response

    async def fetch_subscribers(self, topic: UUri,
                                options: Optional[CallOptions] = CallOptions.DEFAULT) -> usubscription_pb2.FetchSubscribersResponse:
        if not topic:
            raise ValueError("Topic missing")
        if not options:
            raise ValueError("CallOptions missing")

        request = usubscription_pb2.FetchSubscribersRequest(topic=topic)
        response = await RpcMapper.map_response(
            self.rpc_client.invoke_method("usubscription.FetchSubscribers", request, options),
            usubscription_pb2.FetchSubscribersResponse
        )
        return response

    async def fetch_subscriptions(self, request: usubscription_pb2.FetchSubscriptionsRequest,
                                  options: Optional[CallOptions] = CallOptions.DEFAULT) -> usubscription_pb2.FetchSubscriptionsResponse:
        if not request:
            raise ValueError("Request missing")
        if not options:
            raise ValueError("CallOptions missing")

        response = await RpcMapper.map_response(
            self.rpc_client.invoke_method("usubscription.FetchSubscriptions", request, options),
            usubscription_pb2.FetchSubscriptionsResponse
        )
        return response
    
    async def unregister_listener(self, topic: UUri, listener: UListener) -> UStatusModule.UStatus:
        """
        Unregisters a listener and removes any registered SubscriptionChangeHandler for the topic.
        """
        if not topic:
            raise ValueError("Unsubscribe topic missing")
        if not listener:
            raise ValueError("Request listener missing")
        status = await self.transport.unregister_listener(topic, listener)
        return status

