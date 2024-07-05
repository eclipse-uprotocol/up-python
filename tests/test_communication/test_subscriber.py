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
import unittest
from unittest.mock import MagicMock

from tests.test_communication.mock_utransport import MockUTransport
from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.uclient import UClient
from uprotocol.communication.upayload import UPayload
from uprotocol.core.usubscription.v3.usubscription_pb2 import (
    SubscriptionResponse,
    SubscriptionStatus,
    UnsubscribeResponse,
)
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri


class MyListener(UListener):
    def on_receive(self, umsg: UMessage) -> None:
        # Handle receiving subscriptions here
        assert umsg is not None


class TestSubscriber(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.listener = MyListener()

    async def test_subscribe(self):
        topic = UUri(ue_id=4, ue_version_major=1, resource_id=0x8000)
        transport = HappySubscribeUTransport()
        upclient = UClient(transport)
        subscription_response = await upclient.subscribe(topic, self.listener, CallOptions(timeout=5000))
        # check for successfully subscribed
        self.assertTrue(subscription_response.status.state == SubscriptionStatus.State.SUBSCRIBED)

    async def test_publish_notify_subscribe_listener(self):
        topic = UUri(ue_id=5, ue_version_major=1, resource_id=0x8000)
        transport = HappySubscribeUTransport()
        upclient = UClient(transport)
        subscription_response = await upclient.subscribe(topic, self.listener, CallOptions(timeout=5000))
        self.assertTrue(subscription_response.status.state == SubscriptionStatus.State.SUBSCRIBED)

        # Create a mock for MyListener's on_receive method
        self.listener.on_receive = MagicMock(side_effect=self.listener.on_receive)
        status = await upclient.publish(topic, None)
        self.assertEqual(status.code, UCode.OK)
        # Wait for a short time to ensure on_receive can be called
        await asyncio.sleep(1)
        # Verify that on_receive was called
        self.listener.on_receive.assert_called_once()

    async def test_unsubscribe(self):
        topic = UUri(ue_id=6, ue_version_major=1, resource_id=0x8000)
        transport = HappyUnSubscribeUTransport()
        upclient = UClient(transport)
        status = await upclient.unsubscribe(topic, self.listener, None)
        # check for successfully unsubscribed
        self.assertEqual(status.code, UCode.OK)

    async def test_subscribe_unsubscribe(self):
        transport = HappySubscribeUTransport()
        upclient = UClient(transport)
        topic = UUri(ue_id=7, ue_version_major=1, resource_id=0x8000)
        subscription_response = await upclient.subscribe(topic, self.listener, None)
        self.assertTrue(subscription_response.status.state == SubscriptionStatus.State.SUBSCRIBED)

        status2 = await upclient.unsubscribe(topic, self.listener, None)
        # check for successfully unsubscribed
        self.assertEqual(status2.code, UCode.OK)


class HappySubscribeUTransport(MockUTransport):
    def build_response(self, request):
        return UMessageBuilder.response_for_request(request.attributes).build_from_upayload(
            UPayload.pack(
                SubscriptionResponse(
                    status=SubscriptionStatus(
                        state=SubscriptionStatus.State.SUBSCRIBED, message="Successfully Subscribed"
                    )
                )
            )
        )


class HappyUnSubscribeUTransport(MockUTransport):
    def build_response(self, request):
        return UMessageBuilder.response_for_request(request.attributes).build_from_upayload(
            UPayload.pack(UnsubscribeResponse())
        )


if __name__ == '__main__':
    unittest.main()
