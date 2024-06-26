"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import unittest

from tests.test_communication.mock_utransport import CommStatusTransport, MockUTransport, TimeoutUTransport
from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.inmemoryrpcclient import InMemoryRpcClient
from uprotocol.communication.inmemorysubscriber import InMemorySubscriber
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
        pass


class TestInMemorySubscriber(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.listener = MyListener()

    def create_topic(self):
        return UUri(authority_name="neelam", ue_id=3, ue_version_major=1, resource_id=0x8000)

    async def test_subscribe_happy_path(self):
        topic = self.create_topic()
        transport = HappySubscribeUTransport()
        subscriber = InMemorySubscriber(transport, InMemoryRpcClient(transport))

        subscription_response = await subscriber.subscribe(topic, self.listener, None)
        self.assertFalse(subscription_response is None)

    async def test_unsubscribe_happy_path(self):
        topic = self.create_topic()
        transport = HappyUnSubscribeUTransport()
        subscriber = InMemorySubscriber(transport, InMemoryRpcClient(transport))

        response = await subscriber.unsubscribe(topic, self.listener, None)
        self.assertEqual(response.message, "")
        self.assertEqual(response.code, UCode.OK)

    async def test_unregister_listener(self):
        topic = self.create_topic()

        transport = HappySubscribeUTransport()
        subscriber = InMemorySubscriber(transport, InMemoryRpcClient(transport))

        subscription_response = await subscriber.subscribe(topic, self.listener, CallOptions())
        self.assertFalse(subscription_response is None)

        status = subscriber.unregister_listener(topic, self.listener)
        self.assertEqual(status.code, UCode.OK)

    async def test_unsubscribe_with_commstatus_error(self):
        topic = UUri(authority_name="neelam", ue_id=4, ue_version_major=1, resource_id=0x8000)
        transport = CommStatusTransport()
        subscriber = InMemorySubscriber(transport, InMemoryRpcClient(transport))

        response = await subscriber.unsubscribe(topic, self.listener, None)
        self.assertEqual(response.message, "Communication error [FAILED_PRECONDITION]")
        self.assertEqual(response.code, UCode.FAILED_PRECONDITION)

    async def test_unsubscribe_with_exception(self):
        topic = self.create_topic()
        transport = TimeoutUTransport()
        subscriber = InMemorySubscriber(transport, InMemoryRpcClient(transport))

        response = await subscriber.unsubscribe(topic, self.listener, CallOptions(1))
        self.assertEqual(response.message, "Request timed out")
        self.assertEqual(response.code, UCode.DEADLINE_EXCEEDED)


class HappySubscribeUTransport(MockUTransport):
    def build_response(self, request):
        return UMessageBuilder.response_for_request(request.attributes).build_from_upayload(
            UPayload.pack(
                SubscriptionResponse(
                    status=SubscriptionStatus(
                        state=SubscriptionStatus.State.SUBSCRIBED, message="Successfully Subscribed"
                    ),
                    topic=TestInMemorySubscriber().create_topic(),
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
