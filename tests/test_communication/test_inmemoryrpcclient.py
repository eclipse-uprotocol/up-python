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

from tests.test_communication.mock_utransport import CommStatusTransport, MockUTransport, TimeoutUTransport
from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.inmemoryrpcclient import InMemoryRpcClient
from uprotocol.communication.rpcmapper import RpcMapper
from uprotocol.communication.upayload import UPayload
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.v1.uattributes_pb2 import UPriority
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class TestInMemoryRpcClient(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    def create_method_uri():
        return UUri(authority_name="neelam", ue_id=10, ue_version_major=1, resource_id=3)

    async def test_invoke_method_with_payload(self):
        payload = UPayload.pack_to_any(UUri())
        rpc_client = InMemoryRpcClient(MockUTransport())
        future_result = asyncio.ensure_future(rpc_client.invoke_method(self.create_method_uri(), payload, None))
        response = await future_result
        self.assertIsNotNone(response)
        self.assertFalse(future_result.done() and future_result.exception() is not None)
        print("test case 1")

    async def test_invoke_method_with_payload_and_call_options(self):
        payload = UPayload.pack_to_any(UUri())
        options = CallOptions(2000, UPriority.UPRIORITY_CS5)
        rpc_client = InMemoryRpcClient(MockUTransport())
        future_result = asyncio.ensure_future(rpc_client.invoke_method(self.create_method_uri(), payload, options))
        response = await future_result
        self.assertIsNotNone(response)
        self.assertFalse(future_result.done() and future_result.exception() is not None)
        print("test case 2")

    async def test_invoke_method_with_null_payload(self):
        rpc_client = InMemoryRpcClient(MockUTransport())
        future_result = asyncio.ensure_future(
            rpc_client.invoke_method(self.create_method_uri(), None, CallOptions.DEFAULT)
        )
        response = await future_result
        self.assertIsNotNone(response)
        self.assertFalse(future_result.done() and future_result.exception() is not None)
        print("test case 3")

    async def test_invoke_method_with_timeout_transport(self):
        payload = UPayload.pack_to_any(UUri())
        options = CallOptions(100, UPriority.UPRIORITY_CS5, "token")
        rpc_client = InMemoryRpcClient(TimeoutUTransport())
        future_result = asyncio.ensure_future(rpc_client.invoke_method(self.create_method_uri(), payload, options))
        result = await RpcMapper.map_response_to_result(future_result, UUri)
        assert result.is_failure()
        assert result.failure_value().code == UCode.DEADLINE_EXCEEDED
        assert result.failure_value().message == "Request timed out"

    async def test_invoke_method_with_multi_invoke_transport(self):
        rpc_client = InMemoryRpcClient(MockUTransport())
        payload = UPayload.pack_to_any(UUri())
        future_result1 = asyncio.ensure_future(rpc_client.invoke_method(self.create_method_uri(), payload, None))
        future_result2 = asyncio.ensure_future(rpc_client.invoke_method(self.create_method_uri(), payload, None))
        response1 = await future_result1
        response2 = await future_result2

        self.assertIsNotNone(response1)
        self.assertIsNotNone(response2)

        self.assertFalse(future_result1.done() and future_result1.exception() is not None)
        self.assertFalse(future_result2.done() and future_result2.exception() is not None)
        print("test case 5")

    async def test_close_with_multiple_listeners(self):
        rpc_client = InMemoryRpcClient(MockUTransport())
        payload = UPayload.pack_to_any(UUri())
        future_result1 = asyncio.ensure_future(rpc_client.invoke_method(self.create_method_uri(), payload, None))
        future_result2 = asyncio.ensure_future(rpc_client.invoke_method(self.create_method_uri(), payload, None))
        response1 = await future_result1

        response2 = await future_result2

        self.assertIsNotNone(response1)
        self.assertIsNotNone(response2)
        rpc_client.close()
        print("test case 6")

    async def test_invoke_method_with_comm_status_transport(self):
        rpc_client = InMemoryRpcClient(CommStatusTransport())
        payload = UPayload.pack_to_any(UUri())
        future_result = asyncio.ensure_future(rpc_client.invoke_method(self.create_method_uri(), payload, None))
        with self.assertRaises(Exception) as context:
            await future_result

        self.assertTrue(future_result.done() and future_result.exception() is not None)
        self.assertIn("Communication error [FAILED_PRECONDITION]", str(context.exception))
        print("test case 7")

    async def test_invoke_method_with_error_transport(self):
        class ErrorUTransport(MockUTransport):
            def send(self, message):
                return UStatus(code=UCode.FAILED_PRECONDITION)

        rpc_client = InMemoryRpcClient(ErrorUTransport())
        payload = UPayload.pack_to_any(UUri())
        future_result = asyncio.ensure_future(rpc_client.invoke_method(self.create_method_uri(), payload, None))
        with self.assertRaises(Exception) as context:
            await future_result
            print("test case 8")

        self.assertTrue(future_result.done() and future_result.exception() is not None)
        self.assertTrue(isinstance(context.exception,UStatusError))
        print("test case 8  1")


if __name__ == '__main__':
    unittest.main()
