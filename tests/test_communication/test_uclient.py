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

from tests.test_communication.mock_utransport import EchoUTransport, MockUTransport, TimeoutUTransport
from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.requesthandler import RequestHandler
from uprotocol.communication.uclient import UClient
from uprotocol.communication.upayload import UPayload
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.transport.ulistener import UListener
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class MyListener(UListener):
    def on_receive(self, umsg: UMessage) -> None:
        # Handle receiving subscriptions here
        assert umsg is not None


async def register_and_unregister_request_handler(client, handler):
    await client.register_request_handler(create_method_uri(), handler)
    await client.unregister_request_handler(create_method_uri(), handler)


async def unregister_listener_not_registered(client, listener):
    result = await client.unregister_listener(create_topic(), listener)
    assert result.code == UCode.NOT_FOUND


class UClientTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.listener = MyListener()

    def test_create_upclient_with_null_transport(self):
        with self.assertRaises(ValueError):
            UClient(None)

    async def test_send_notification(self):
        status = await UClient(MockUTransport()).notify(create_topic(), create_destination_uri())
        self.assertEqual(status.code, UCode.OK)

    async def test_send_notification_with_payload(self):
        uri = UUri(authority_name="neelam")
        status = await UClient(MockUTransport()).notify(
            create_topic(), create_destination_uri(), payload=UPayload.pack(uri)
        )
        self.assertEqual(status.code, UCode.OK)

    async def test_register_listener(self):
        listener = create_autospec(UListener, instance=True)
        listener.on_receive = MagicMock()

        status = await UClient(MockUTransport()).register_notification_listener(create_topic(), listener)
        self.assertEqual(status.code, UCode.OK)

    async def test_unregister_notification_listener(self):
        listener = create_autospec(UListener, instance=True)
        listener.on_receive = MagicMock()

        notifier = UClient(MockUTransport())
        status = await notifier.register_notification_listener(create_topic(), listener)
        self.assertEqual(status.code, UCode.OK)

        status = await notifier.unregister_notification_listener(create_topic(), listener)
        self.assertEqual(status.code, UCode.OK)

    async def test_unregister_listener_not_registered(self):
        listener = create_autospec(UListener, instance=True)
        listener.on_receive = MagicMock()

        status = await UClient(MockUTransport()).unregister_notification_listener(create_topic(), listener)
        self.assertEqual(status.code, UCode.NOT_FOUND)

    async def test_send_publish(self):
        status = await UClient(MockUTransport()).publish(create_topic())
        self.assertEqual(status.code, UCode.OK)

    async def test_send_publish_with_stuffed_payload(self):
        uri = UUri(authority_name="neelam")
        status = await UClient(MockUTransport()).publish(create_topic(), payload=UPayload.pack_to_any(uri))
        self.assertEqual(status.code, UCode.OK)

    async def test_send_publish_with_stuffed_payload_and_calloptions(self):
        uri = UUri(authority_name="neelam")
        status = await UClient(MockUTransport()).publish(
            create_topic(), CallOptions(token="134"), payload=UPayload.pack_to_any(uri)
        )
        self.assertEqual(status.code, UCode.OK)

    async def test_invoke_method_with_payload(self):
        payload = UPayload.pack_to_any(UUri())
        future_result = asyncio.ensure_future(UClient(MockUTransport()).invoke_method(create_method_uri(), payload))
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

        future_result1 = asyncio.ensure_future(rpc_client.invoke_method(create_method_uri(), payload))
        response = await future_result1
        self.assertIsNotNone(response)
        future_result2 = asyncio.ensure_future(rpc_client.invoke_method(create_method_uri(), payload))
        response2 = await future_result2

        self.assertIsNotNone(response2)

        self.assertFalse(future_result1.exception())
        self.assertFalse(future_result2.exception())

    async def test_registering_request_listener(self):
        handler = create_autospec(RequestHandler, instance=True)
        server = UClient(MockUTransport())
        status = await server.register_request_handler(create_method_uri(), handler)
        self.assertEqual(status.code, UCode.OK)

    async def test_registering_twice_the_same_request_handler(self):
        handler = create_autospec(RequestHandler, instance=True)
        server = UClient(MockUTransport())
        status = await server.register_request_handler(create_method_uri(), handler)
        self.assertEqual(status.code, UCode.OK)
        status = await server.register_request_handler(create_method_uri(), handler)
        self.assertEqual(status.code, UCode.ALREADY_EXISTS)

    async def test_unregistering_non_registered_request_handler(self):
        handler = create_autospec(RequestHandler, instance=True)
        server = UClient(MockUTransport())
        status = await server.unregister_request_handler(create_method_uri(), handler)
        self.assertEqual(status.code, UCode.NOT_FOUND)

    async def test_request_handler_for_notification(self):
        transport = EchoUTransport()
        client = UClient(transport)
        handler = create_autospec(RequestHandler, instance=True)

        await client.register_request_handler(create_method_uri(), handler)
        self.assertEqual(await client.notify(create_topic(), transport.get_source()), UStatus(code=UCode.OK))

    async def test_happy_path_for_all_apis_async(self):
        client = UClient(MockUTransport())

        class MyUListener(UListener):
            def on_receive(self, umsg: UMessage) -> None:
                pass

        class MyRequestHandler(RequestHandler):
            def handle_request(self, message: UMessage) -> UPayload:
                pass

        async def run_tests():
            listener = MyUListener()
            handler = MyRequestHandler()
            listener.on_receive = MagicMock()

            tasks = [
                client.notify(create_topic(), create_destination_uri()),
                client.publish(create_topic()),
                client.invoke_method(create_method_uri(), UPayload.pack(None), CallOptions.DEFAULT),
                client.register_notification_listener(create_topic(), listener),
                client.unregister_notification_listener(create_topic(), listener),
                register_and_unregister_request_handler(client, handler),
            ]

            await asyncio.gather(*tasks)
            client.close()

        await run_tests()


def create_topic():
    return UUri(authority_name="neelam", ue_id=4, ue_version_major=1, resource_id=0x8000)


def create_destination_uri():
    return UUri(ue_id=4, ue_version_major=1)


def create_method_uri():
    return UUri(authority_name="neelam", ue_id=4, ue_version_major=1, resource_id=3)


class CommStatusTransport(MockUTransport):
    def build_response(self, request):
        status = UStatus(UCode.FAILED_PRECONDITION, "CommStatus Error")
        return UMessage.response(request.attributes).with_comm_status(status.code).build(UPayload.pack(status))
