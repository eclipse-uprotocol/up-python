"""
SPDX-FileCopyrightText: Copyright (c) 2023 Contributors to the
Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SPDX-FileType: SOURCE
SPDX-License-Identifier: Apache-2.0
"""

from concurrent.futures import Future
from google.protobuf import any_pb2

from uprotocol.client.upayload import UPayload
from uprotocol.client.rpc_result import RpcResult

from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UCode
from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UStatus


class RpcMapper:
    """
    RPC Wrapper is an interface that provides static methods to be able to
    wrap an RPC request with an RPC Response (
    uP-L2). APIs that return Message assumes that the message is
    protobuf serialized com.google.protobuf.Any (
    UMessageFormat.PROTOBUF) and will barf if anything else is passed
    """

    @staticmethod
    def map_response(payload_future: Future, expected_cls):
        """
        Map a response of payload_future from Link
        into a Futre containing the
        declared expected return type of the RPC method or an
        exception.
        @param payload_future: Future response from uTransport.
        @param expected_cls: The class name of the declared expected
        return type of the RPC method.
        @return: Returns a Future containing the declared
        expected return type of the RPC method or an exception.
        """
        response_future: Future = Future()

        def handle_response(payload: UPayload):
            nonlocal response_future
            if not payload or len(payload.get_data()) == 0:
                response_future.set_exception(
                    RuntimeError(
                        "Server returned a null payload. "
                        f"Expected {expected_cls.__name__}"
                    )
                )
                return response_future
            try:
                any_message = any_pb2.Any()
                any_message.ParseFromString(payload.get_data())
                if any_message.Is(expected_cls.DESCRIPTOR):
                    response_future.set_result(
                        RpcMapper.unpack_payload(any_message, expected_cls)
                    )
                else:
                    response_future.set_exception(
                        RuntimeError(
                            f"Unknown payload type [{any_message.type_url}]. "
                            f"Expected [{expected_cls.__name__}]"
                        )
                    )

            except Exception as e:
                response_future.set_exception(
                    RuntimeError(f"{str(e)} [{UStatus.__name__}]")
                )

        payload_future.add_done_callback(handle_response)

        return response_future

    @staticmethod
    def map_response_to_result(response_future: Future, expected_cls):
        """
        Map a response of Futre from Link into a Future containing an RpcResult
        containing the declared expected return type expected_cls, or a
        UStatus containing any errors.
        @param response_future: Future response from Link.
        @param expected_cls:The class name of the declared expected
        return type of the RPC method.
        @return:Returns a CompletableFuture containing an RpcResult
        containing the declared expected return type expected_cls,
        or a UStatus containing any errors.
        """

        def handle_response(payload):
            if payload.exception():
                exception = payload.exception()
                return RpcResult.failure(
                    value=exception, message=str(exception)
                )

            if not payload or len(payload.get_data()) == 0:
                exception = RuntimeError(
                    "Server returned a null payload. "
                    f"Expected {expected_cls.__name__}"
                )
                return RpcResult.failure(
                    value=exception, message=str(exception)
                )

            try:
                any_message = any_pb2.Any()
                any_message.ParseFromString(payload.get_data())

                if any_message.Is(expected_cls.DESCRIPTOR):
                    if expected_cls == UStatus:
                        return RpcMapper.calculate_status_result(any_message)
                    else:
                        return RpcResult.success(
                            RpcMapper.unpack_payload(any_message, expected_cls)
                        )

                if any_message.Is(UStatus.DESCRIPTOR):
                    return RpcMapper.calculate_status_result(any_message)
            except Exception as e:
                exception = RuntimeError(f"{str(e)} [{UStatus.__name__}]")
                return RpcResult.failure(
                    value=exception, message=str(exception)
                )

            exception = RuntimeError(
                f"Unknown payload type [{any_message.type_url}]. "
                f"Expected [{expected_cls.DESCRIPTOR.full_name}]"
            )
            return RpcResult.failure(value=exception, message=str(exception))

        result = None  # Initialize result

        def callback_wrapper(payload):
            nonlocal result
            result = handle_response(payload)

        response_future.add_done_callback(callback_wrapper)
        return result

    @staticmethod
    def calculate_status_result(payload):
        status = RpcMapper.unpack_payload(payload, UStatus)
        return (
            RpcResult.success(status)
            if status.code == UCode.OK
            else RpcResult.failure(status)
        )

    @staticmethod
    def unpack_payload(payload, expected_cls):
        """
        Unpack a payload of type Any into an object of type T,
        which is what was packing into the Any object.
        @param payload:an Any message containing a type of expectedClazz.
        @param expected_cls:The class name of the object packed into the Any
        @return:Returns an object of type T and of the class name specified,
        that was packed into the Any object.
        """
        try:
            value = expected_cls()
            value.ParseFromString(payload.value)
            # payload.Unpack(expected_cls)
            return value
        except Exception as e:
            raise RuntimeError(f"{str(e)} [{UStatus.__name__}]") from e
