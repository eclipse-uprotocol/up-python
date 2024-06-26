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

from uprotocol.communication.rpcresult import RpcResult
from uprotocol.communication.upayload import UPayload
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.v1.ucode_pb2 import UCode


class RpcMapper:
    """
    RPC Wrapper is a class that provides static methods to wrap an RPC request
    with an RPC Response (uP-L2). APIs returning Message assume the message is
    protobuf serialized com.google.protobuf.Any (UMessageFormat.PROTOBUF), and will
    raise an error if anything else is passed.
    """

    @staticmethod
    async def map_response(response_coro: asyncio.Future, expected_cls):
        """
        Map a response from invoking a method on a uTransport service into a result
        containing the declared expected return type of the RPC method.

        :param response_coro: Coroutine response from uTransport.
        :param expected_cls: The class name of the declared expected return type of the RPC method.
        :return: Returns the declared expected return type of the RPC method or raises an exception.
        """
        try:
            payload = await response_coro
        except Exception as e:
            raise RuntimeError(f"Unexpected exception: {str(e)}") from e

        if payload is not None :
            if not payload.data:
                return expected_cls()
            else:
                result = UPayload.unpack(payload, expected_cls)
                if result:
                    return result

        raise RuntimeError(f"Unknown payload. Expected [{expected_cls.__name__}]")

    @staticmethod
    async def map_response_to_result(response_coro: asyncio.Future, expected_cls) -> RpcResult:
        """
        Map a response from method invocation to an RpcResult containing the declared expected
        return type of the RPC method.

        This function handles the asynchronous response from invoking a method on a uTransport
        service. It converts the response into a result containing the expected return type or
        an error status.

        :param response_coro: An asyncio.Future representing the asynchronous response from uTransport.
        :param expected_cls: The class of the expected return type of the RPC method.
        :return: Returns an RpcResult containing the expected return type T, or an error status.
        :rtype: RpcResult[T]
        :raises: Raises appropriate exceptions if there is an error during response handling.
        """
        try:
            payload = await response_coro
        except Exception as e:
            if isinstance(e, UStatusError):
                return RpcResult.failure(value=e.status)
            elif isinstance(e, TimeoutError) or isinstance(e, asyncio.TimeoutError):
                return RpcResult.failure(code=UCode.DEADLINE_EXCEEDED, message="Request timed out")
            else:
                return RpcResult.failure(code=UCode.INVALID_ARGUMENT, message=str(e))

        if payload is not None:
            if not payload.data:
                return RpcResult.success(expected_cls())
            else:
                result = UPayload.unpack(payload, expected_cls)
                return RpcResult.success(result)

        exception = RuntimeError(f"Unknown or null payload type. Expected [{expected_cls.__name__}]")
        return RpcResult.failure(code=UCode.INVALID_ARGUMENT, message=str(exception))
