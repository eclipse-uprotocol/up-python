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
import asyncio

from unittest.mock import MagicMock

from tests.test_communication.mock_utransport import (
    CommStatusTransport,
    CommStatusUCodeOKTransport,
    MockUTransport,
    TimeoutUTransport,
)

from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.inmemoryrpcclient import InMemoryRpcClient, HandleResponsesListener
from uprotocol.communication.upayload import UPayload
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.transport.utransport import UTransport
from uprotocol.uuid.serializer.uuidserializer import UuidSerializer
from uprotocol.v1.uattributes_pb2 import UPriority, UAttributes, UMessageType
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class TestInMemoryRpcClient(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    def create_method_uri():
        return UUri(authority_name="neelam", ue_id=10, ue_version_major=1, resource_id=3)

    def test_constructor_transport_none(self):
        with self.assertRaises(ValueError) as context:
            InMemoryRpcClient(None)
        self.assertEqual(str(context.exception), UTransport.TRANSPORT_NULL_ERROR)

    def test_constructor_transport_not_instance(self):
        with self.assertRaises(ValueError) as context:
            InMemoryRpcClient("Invalid Transport")
        self.assertEqual(str(context.exception), UTransport.TRANSPORT_NOT_INSTANCE_ERROR)

    async def test_invoke_method_with_payload(self):
        payload = UPayload.pack_to_any(UUri())
        rpc_client = InMemoryRpcClient(MockUTransport())
        response = await rpc_client.invoke_method(self.create_method_uri(), payload, None)
        self.assertIsNotNone(response)
        self.assertEqual(response, payload)

    async def test_invoke_method_with_payload_and_call_options(self):
        payload = UPayload.pack_to_any(UUri())
        options = CallOptions(2000, UPriority.UPRIORITY_CS5)
        rpc_client = InMemoryRpcClient(MockUTransport())
        response = await rpc_client.invoke_method(self.create_method_uri(), payload, options)
        self.assertIsNotNone(response)
        self.assertEqual(response, payload)

    async def test_invoke_method_with_null_payload(self):
        rpc_client = InMemoryRpcClient(MockUTransport())
        response = await rpc_client.invoke_method(self.create_method_uri(), None, CallOptions.DEFAULT)
        self.assertIsNotNone(response)
        self.assertEqual(response, UPayload.EMPTY)

    async def test_invoke_method_with_timeout_transport(self):
        payload = UPayload.pack_to_any(UUri())
        options = CallOptions(100, UPriority.UPRIORITY_CS5, "token")
        rpc_client = InMemoryRpcClient(TimeoutUTransport())
        with self.assertRaises(UStatusError) as context:
            await rpc_client.invoke_method(self.create_method_uri(), payload, options)
        self.assertEqual(UCode.DEADLINE_EXCEEDED, context.exception.status.code)
        self.assertEqual("Request timed out", context.exception.status.message)

    async def test_invoke_method_with_multi_invoke_transport(self):
        rpc_client = InMemoryRpcClient(MockUTransport())
        payload = UPayload.pack_to_any(UUri())
        response1 = await rpc_client.invoke_method(self.create_method_uri(), payload, None)
        response2 = await rpc_client.invoke_method(self.create_method_uri(), payload, None)
        self.assertIsNotNone(response1)
        self.assertIsNotNone(response2)
        self.assertEqual(payload, response1)
        self.assertEqual(payload, response2)

    async def test_close_with_multiple_listeners(self):
        rpc_client = InMemoryRpcClient(MockUTransport())
        payload = UPayload.pack_to_any(UUri())

        response1 = await rpc_client.invoke_method(self.create_method_uri(), payload, None)
        response2 = await rpc_client.invoke_method(self.create_method_uri(), payload, None)
        self.assertIsNotNone(response1)
        self.assertIsNotNone(response2)
        self.assertEqual(payload, response1)
        self.assertEqual(payload, response2)
        rpc_client.close()

    async def test_invoke_method_with_comm_status_transport_error(self):
        rpc_client = InMemoryRpcClient(CommStatusTransport())
        payload = UPayload.pack_to_any(UUri())
        with self.assertRaises(UStatusError) as context:
            await rpc_client.invoke_method(self.create_method_uri(), payload, None)
        self.assertEqual(UCode.FAILED_PRECONDITION, context.exception.status.code)
        self.assertEqual("Communication error [FAILED_PRECONDITION]", context.exception.status.message)

    async def test_invoke_method_with_comm_status_transport_ok(self):
        rpc_client = InMemoryRpcClient(CommStatusUCodeOKTransport())
        payload = UPayload.pack_to_any(UUri())
        response = await rpc_client.invoke_method(self.create_method_uri(), payload, None)
        self.assertEqual(UCode.OK, UPayload.unpack(response, UStatus).code)

    async def test_invoke_method_with_error_transport(self):
        class ErrorUTransport(MockUTransport):
            async def send(self, message):
                return UStatus(code=UCode.FAILED_PRECONDITION)

        rpc_client = InMemoryRpcClient(ErrorUTransport())
        payload = UPayload.pack_to_any(UUri())
        with self.assertRaises(UStatusError) as context:
            await rpc_client.invoke_method(self.create_method_uri(), payload, None)
        self.assertEqual(UCode.FAILED_PRECONDITION, context.exception.status.code)


class TestHandleResponsesListener(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.future = asyncio.Future()
        from uprotocol.v1.uuid_pb2 import UUID
        self.reqid = UUID(msb=0x1234567890ABCDEF, lsb=0xFEDCBA0987654321)
        self.serialized_reqid = UuidSerializer.serialize(self.reqid)
        self.requests = {self.serialized_reqid: self.future}
        self.listener = HandleResponsesListener(self.requests)

    async def test_on_receive_ignores_non_response_type(self):
        umsg = UMessage(
            attributes=UAttributes(
                type=UMessageType.UMESSAGE_TYPE_REQUEST,
                reqid=self.reqid
            )
        )
        await self.listener.on_receive(umsg)
        self.assertFalse(self.future.done())

    async def test_on_receive_sets_result_on_successful_response(self):
        umsg = UMessage(
            attributes=UAttributes(
                type=UMessageType.UMESSAGE_TYPE_RESPONSE,
                reqid=self.reqid,
                commstatus=UCode.OK
            )
        )
        await self.listener.on_receive(umsg)
        self.assertTrue(self.future.done())
        self.assertEqual(self.future.result(), umsg)

    async def test_on_receive_sets_exception_on_commstatus_error(self):
        umsg = UMessage(
            attributes=UAttributes(
                type=UMessageType.UMESSAGE_TYPE_RESPONSE,
                reqid=self.reqid,
                commstatus=UCode.FAILED_PRECONDITION
            )
        )
        await self.listener.on_receive(umsg)
        self.assertTrue(self.future.done())
        with self.assertRaises(UStatusError) as cm:
            self.future.result()
        self.assertEqual(cm.exception.status.code, UCode.FAILED_PRECONDITION)
        self.assertIn("Communication error [FAILED_PRECONDITION]", cm.exception.status.message)

    async def test_on_receive_handles_missing_future_gracefully(self):
        listener = HandleResponsesListener({})
        umsg = UMessage(
            attributes=UAttributes(
                type=UMessageType.UMESSAGE_TYPE_RESPONSE,
                reqid=self.reqid
            )
        )
        await listener.on_receive(umsg)
        # Should complete without exceptions even though future is missing


if __name__ == '__main__':
    unittest.main()
