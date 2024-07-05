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

    async def test_invoke_method_with_comm_status_transport(self):
        rpc_client = InMemoryRpcClient(CommStatusTransport())
        payload = UPayload.pack_to_any(UUri())
        with self.assertRaises(UStatusError) as context:
            await rpc_client.invoke_method(self.create_method_uri(), payload, None)
        self.assertEqual(UCode.FAILED_PRECONDITION, context.exception.status.code)
        self.assertEqual("Communication error [FAILED_PRECONDITION]", context.exception.status.message)

    async def test_invoke_method_with_error_transport(self):
        class ErrorUTransport(MockUTransport):
            async def send(self, message):
                return UStatus(code=UCode.FAILED_PRECONDITION)

        rpc_client = InMemoryRpcClient(ErrorUTransport())
        payload = UPayload.pack_to_any(UUri())
        with self.assertRaises(UStatusError) as context:
            await rpc_client.invoke_method(self.create_method_uri(), payload, None)

        self.assertEqual(UCode.FAILED_PRECONDITION, context.exception.status.code)


if __name__ == '__main__':
    unittest.main()
