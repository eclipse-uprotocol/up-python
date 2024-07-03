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
from unittest.mock import MagicMock, create_autospec

from tests.test_communication.mock_utransport import EchoUTransport, ErrorUTransport, MockUTransport, TimeoutUTransport
from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.requesthandler import RequestHandler
from uprotocol.communication.uclient import UClient
from uprotocol.communication.upayload import UPayload
from uprotocol.communication.ustatuserror import UStatusError
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
from uprotocol.v1.ustatus_pb2 import UStatus


class MyListener(UListener):
    def on_receive(self, umsg: UMessage) -> None:
        # Handle receiving subscriptions here
        assert umsg is not None


class UPClientTest(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.listener = MyListener()

    def test_create_upclient_with_null_transport(self):
        with self.assertRaises(ValueError):
            UClient(None)

    def test_create_upclient_with_error_transport(self):
        with self.assertRaises(UStatusError):
            UClient(ErrorUTransport())

    def test_send_notification(self):
        status = UClient(MockUTransport()).notify(create_topic(), create_destination_uri(), None)
        self.assertEqual(status.code, UCode.OK)

    def test_send_notification_with_payload(self):
        uri = UUri(authority_name="neelam")
        status = UClient(MockUTransport()).notify(create_topic(), create_destination_uri(), UPayload.pack(uri))
        self.assertEqual(status.code, UCode.OK)

    def test_register_listener(self):
        listener = create_autospec(UListener, instance=True)
        listener.on_receive = MagicMock()

        status = UClient(MockUTransport()).register_notification_listener(create_topic(), listener)
        self.assertEqual(status.code, UCode.OK)

    def test_unregister_notification_listener(self):
        listener = create_autospec(UListener, instance=True)
        listener.on_receive = MagicMock()

        notifier = UClient(MockUTransport())
        status = notifier.register_notification_listener(create_topic(), listener)
        self.assertEqual(status.code, UCode.OK)

        status = notifier.unregister_notification_listener(create_topic(), listener)
        self.assertEqual(status.code, UCode.OK)

    def test_unregister_listener_not_registered(self):
        listener = create_autospec(UListener, instance=True)
        listener.on_receive = MagicMock()

        status = UClient(MockUTransport()).unregister_notification_listener(create_topic(), listener)
        self.assertEqual(status.code, UCode.INVALID_ARGUMENT)

    def test_send_publish(self):
        status = UClient(MockUTransport()).publish(create_topic(), None)
        self.assertEqual(status.code, UCode.OK)

    def test_send_publish_with_stuffed_payload(self):
        uri = UUri(authority_name="neelam")
        status = UClient(MockUTransport()).publish(create_topic(), UPayload.pack_to_any(uri))
        self.assertEqual(status.code, UCode.OK)

    async def test_invoke_method_with_payload(self):
        payload = UPayload.pack_to_any(UUri())
        future_result = asyncio.ensure_future(
            UClient(MockUTransport()).invoke_method(create_method_uri(), payload, None)
        )
        response = await future_result
        self.assertIsNotNone(response)
        self.assertFalse(future_result.exception())

    async def test_invoke_method_with_payload_and_call_options(self):
        payload = UPayload.pack_to_any(UUri())
        options = CallOptions(3000, "UPRIORITY_CS5")
        future_result = asyncio.ensure_future(
            UClient(MockUTransport()).invoke_method(create_method_uri(), payload, options)
        )
        response = await future_result
        self.assertIsNotNone(response)
        self.assertFalse(future_result.exception())

    async def test_invoke_method_with_null_payload(self):
        future_result = asyncio.ensure_future(
            UClient(MockUTransport()).invoke_method(create_method_uri(), None, CallOptions.DEFAULT)
        )
        response = await future_result
        self.assertIsNotNone(response)
        self.assertFalse(future_result.exception())

    async def test_invoke_method_with_timeout_transport(self):
        payload = UPayload.pack_to_any(UUri())
        options = CallOptions(10, "UPRIORITY_CS5", "token")
        with self.assertRaises(UStatusError) as context:
            await UClient(TimeoutUTransport()).invoke_method(create_method_uri(), payload, options)
        self.assertEqual(UCode.DEADLINE_EXCEEDED, context.exception.status.code)
        self.assertEqual("Request timed out", context.exception.status.message)

    async def test_invoke_method_with_multi_invoke_transport(self):
        rpc_client = UClient(MockUTransport())
        payload = UPayload.pack_to_any(UUri())

        future_result1 = asyncio.ensure_future(rpc_client.invoke_method(create_method_uri(), payload, None))
        response = await future_result1
        self.assertIsNotNone(response)
        future_result2 = asyncio.ensure_future(rpc_client.invoke_method(create_method_uri(), payload, None))
        response2 = await future_result2

        self.assertIsNotNone(response2)

        self.assertFalse(future_result1.exception())
        self.assertFalse(future_result2.exception())

    async def test_subscribe_happy_path(self):
        topic = UUri(ue_id=4, ue_version_major=1, resource_id=0x8000)
        transport = HappySubscribeUTransport()
        upclient = UClient(transport)
        subscription_response = await upclient.subscribe(topic, self.listener, CallOptions(timeout=5000))
        # check for successfully subscribed
        self.assertTrue(subscription_response.status.state == SubscriptionStatus.State.SUBSCRIBED)

    async def test_unsubscribe(self):
        topic = UUri(ue_id=6, ue_version_major=1, resource_id=0x8000)
        transport = HappyUnSubscribeUTransport()
        upclient = UClient(transport)
        status = await upclient.unsubscribe(topic, self.listener, None)
        # check for successfully unsubscribed
        self.assertEqual(status.code, UCode.OK)

    async def test_unregister_listener(self):
        topic = create_topic()
        my_listener = create_autospec(UListener, instance=True)

        subscriber = UClient(HappySubscribeUTransport())
        subscription_response = await subscriber.subscribe(topic, my_listener, CallOptions.DEFAULT)
        self.assertTrue(subscription_response.status.state == SubscriptionStatus.State.SUBSCRIBED)
        status = subscriber.unregister_listener(topic, my_listener)
        self.assertEqual(status.code, UCode.OK)

    def test_registering_request_listener(self):
        handler = create_autospec(RequestHandler, instance=True)
        server = UClient(MockUTransport())
        status = server.register_request_handler(create_method_uri(), handler)
        self.assertEqual(status.code, UCode.OK)

    def test_registering_twice_the_same_request_handler(self):
        handler = create_autospec(RequestHandler, instance=True)
        server = UClient(MockUTransport())
        status = server.register_request_handler(create_method_uri(), handler)
        self.assertEqual(status.code, UCode.OK)
        status = server.register_request_handler(create_method_uri(), handler)
        self.assertEqual(status.code, UCode.ALREADY_EXISTS)

    def test_unregistering_non_registered_request_handler(self):
        handler = create_autospec(RequestHandler, instance=True)
        server = UClient(MockUTransport())
        status = server.unregister_request_handler(create_method_uri(), handler)
        self.assertEqual(status.code, UCode.NOT_FOUND)

    def test_request_handler_for_notification(self):
        transport = EchoUTransport()
        client = UClient(transport)
        handler = create_autospec(RequestHandler, instance=True)

        client.register_request_handler(create_method_uri(), handler)
        self.assertEqual(client.notify(create_topic(), transport.get_source(), None), UStatus(code=UCode.OK))


def create_topic():
    return UUri(authority_name="neelam", ue_id=4, ue_version_major=1, resource_id=0x8000)


def create_destination_uri():
    return UUri(ue_id=4, ue_version_major=1)


def create_method_uri():
    return UUri(authority_name="neelam", ue_id=4, ue_version_major=1, resource_id=3)


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


class CommStatusTransport(MockUTransport):
    def build_response(self, request):
        status = UStatus(UCode.FAILED_PRECONDITION, "CommStatus Error")
        return UMessage.response(request.attributes).with_comm_status(status.code).build(UPayload.pack(status))
