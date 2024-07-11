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

import pytest

from tests.test_communication.mock_utransport import MockUTransport
from uprotocol.communication.inmemoryrpcclient import InMemoryRpcClient
from uprotocol.communication.rpcmapper import RpcMapper
from uprotocol.communication.upayload import UPayload
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class TestRpcMapper(unittest.IsolatedAsyncioTestCase):
    async def test_map_response(self):
        uri = UUri(authority_name="Neelam")
        payload = UPayload.pack(uri)

        rpc_client = InMemoryRpcClient(MockUTransport())
        future_result = rpc_client.invoke_method(self.create_method_uri(), payload)
        result = await RpcMapper.map_response(future_result, UUri)
        assert result == uri

    async def test_map_response_to_result_with_empty_request(self):
        rpc_client = InMemoryRpcClient(MockUTransport())
        future_result = rpc_client.invoke_method(self.create_method_uri(), None, None)
        result = await RpcMapper.map_response_to_result(future_result, UUri)
        assert result.is_success()
        assert result.success_value() == UUri()

    async def test_map_response_with_exception(self):
        class RpcClientWithException:
            async def invoke_method(self, uri, payload, options):
                raise RuntimeError("Error")

        rpc_client = RpcClientWithException()
        future_result = rpc_client.invoke_method(self.create_method_uri(), None, None)

        with pytest.raises(RuntimeError):
            await RpcMapper.map_response(future_result, UUri)

    async def test_map_response_with_empty_payload(self):
        class RpcClientWithEmptyPayload:
            async def invoke_method(self, uri, payload, options):
                return UPayload.EMPTY

        rpc_client = RpcClientWithEmptyPayload()
        future_result = rpc_client.invoke_method(self.create_method_uri(), UPayload.EMPTY, None)
        result = await RpcMapper.map_response(future_result, UUri)
        assert result == UUri()

    async def test_map_response_with_null_payload(self):
        class RpcClientWithNullPayload:
            async def invoke_method(self, uri, payload, options):
                return None

        rpc_client = RpcClientWithNullPayload()
        future_result = rpc_client.invoke_method(self.create_method_uri(), UPayload.EMPTY, None)

        with pytest.raises(Exception) as exc_info:
            await RpcMapper.map_response(future_result, UUri)
        assert str(exc_info.value) == f"Unknown payload. Expected [{UUri.__name__}]"

    async def test_map_response_to_result_with_non_empty_payload(self):
        uri = UUri(authority_name="Neelam")
        payload = UPayload.pack(uri)

        class RpcClientWithNonEmptyPayload:
            async def invoke_method(self, uri, payload, options):
                return payload

        rpc_client = RpcClientWithNonEmptyPayload()
        future_result = rpc_client.invoke_method(self.create_method_uri(), payload, None)
        result = await RpcMapper.map_response_to_result(future_result, UUri)
        assert result.is_success()
        assert result.success_value() == uri

    async def test_map_response_to_result_with_null_payload(self):
        class RpcClientWithNullPayload:
            async def invoke_method(self, uri, payload, options):
                return None

        rpc_client = RpcClientWithNullPayload()
        future_result = rpc_client.invoke_method(self.create_method_uri(), UPayload.EMPTY, None)
        result = await RpcMapper.map_response_to_result(future_result, UUri)
        assert result.is_failure()

    async def test_map_response_to_result_with_empty_payload(self):
        class RpcClientWithEmptyPayload:
            async def invoke_method(self, uri, payload, options):
                return UPayload.EMPTY

        rpc_client = RpcClientWithEmptyPayload()
        future_result = rpc_client.invoke_method(self.create_method_uri(), UPayload.EMPTY, None)
        result = await RpcMapper.map_response_to_result(future_result, UUri)
        assert result.is_success()
        assert result.success_value() == UUri()

    async def test_map_response_to_result_with_exception(self):
        class RpcClientWithException:
            async def invoke_method(self, uri, payload, options):
                status = UStatus(code=UCode.FAILED_PRECONDITION, message="Error")
                raise UStatusError(status)

        rpc_client = RpcClientWithException()
        future_result = rpc_client.invoke_method(self.create_method_uri(), UPayload.EMPTY, None)
        result = await RpcMapper.map_response_to_result(future_result, UUri)
        assert result.is_failure()
        assert result.failure_value().code == UCode.FAILED_PRECONDITION
        assert result.failure_value().message == "Error"

    async def test_map_response_to_result_with_timeout_exception(self):
        class RpcClientWithTimeoutException:
            async def invoke_method(self, uri, payload, options):
                raise UStatusError.from_code_message(code=UCode.DEADLINE_EXCEEDED, message="Request timed out")

        rpc_client = RpcClientWithTimeoutException()
        future_result = rpc_client.invoke_method(self.create_method_uri(), UPayload.EMPTY, None)
        result = await RpcMapper.map_response_to_result(future_result, UUri)
        assert result.is_failure()
        assert result.failure_value().code == UCode.DEADLINE_EXCEEDED
        assert result.failure_value().message == "Request timed out"

    async def test_map_response_to_result_with_invalid_arguments_exception(self):
        class RpcClientWithInvalidArgumentsException:
            async def invoke_method(self, uri, payload, options):
                raise ValueError()

        rpc_client = RpcClientWithInvalidArgumentsException()
        future_result = rpc_client.invoke_method(self.create_method_uri(), UPayload.EMPTY, None)
        result = await RpcMapper.map_response_to_result(future_result, UUri)
        assert result.is_failure()
        assert result.failure_value().code == UCode.INVALID_ARGUMENT
        assert result.failure_value().message == ""

    def create_method_uri(self):
        return UUri(authority_name="Neelam", ue_id=10, ue_version_major=1, resource_id=3)


if __name__ == '__main__':
    unittest.main()
