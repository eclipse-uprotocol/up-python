# -------------------------------------------------------------------------

# Copyright (c) 2023 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: 2023 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0

# -------------------------------------------------------------------------


from concurrent.futures import Future

from google.protobuf import any_pb2
from org_eclipse_uprotocol.proto.ustatus_pb2 import UCode
from org_eclipse_uprotocol.proto.ustatus_pb2 import UStatus

from org_eclipse_uprotocol.rpc.rpcresult import RpcResult
from org_eclipse_uprotocol.proto.upayload_pb2 import UPayload


class RpcMapper:
    """
    RPC Wrapper is an interface that provides static methods to be able to wrap an RPC request with an RPC Response (
    uP-L2). APIs that return Message assumes that the payload is protobuf serialized com.google.protobuf.Any (
    UPayloadFormat.PROTOBUF) and will barf if anything else is passed
    """

    @staticmethod
    def map_response(response_future: Future, expected_cls):
        """
         Map a response of CompletableFuture&lt;UPayload&gt; from Link into a CompletableFuture containing the
         declared expected return type of the RPC method or an exception.<br><br>
        @param response_future:CompletableFuture&lt;UPayload&gt; response from uTransport.
        @param expected_cls:The class name of the declared expected return type of the RPC method.
        @return:Returns a CompletableFuture containing the declared expected return type of the RPC method or an
        exception.
        """

        def handle_response(payload, exception):
            if exception:
                raise exception
            payload = payload.result()
            if not payload:
                raise RuntimeError(f"Server returned a null payload. Expected {expected_cls.__name__}")

            try:
                any_message = any_pb2.Any()
                any_message.ParseFromString(payload.value)
                if any_message.Is(expected_cls.DESCRIPTOR):
                    return RpcMapper.unpack_payload(any_message, expected_cls)
            except Exception as e:
                raise RuntimeError(f"{str(e)} [{UStatus.__name__}]") from e

            raise RuntimeError(f"Unknown payload type [{any_message.type_url}]. Expected [{expected_cls.__name__}]")

        result = None  # Initialize result

        def callbackwrapper(payload, exception=None):
            nonlocal result
            result = handle_response(payload, exception)

        response_future.add_done_callback(callbackwrapper)
        return result

    @staticmethod
    def map_response_to_result(response_future: Future, expected_cls):
        """
        Map a response of CompletableFuture&lt;Any&gt; from Link into a CompletableFuture containing an RpcResult
        containing the declared expected return type T, or a UStatus containing any errors.<br><br>
        @param response_future:CompletableFuture&lt;Any&gt; response from Link.
        @param expected_cls:The class name of the declared expected return type of the RPC method.
        @return:Returns a CompletableFuture containing an RpcResult containing the declared expected return type T,
        or a UStatus containing any errors.
        """

        def handle_response(payload, exception=None):
            if exception:
                raise exception
            payload = payload.result()
            if not payload:
                raise RuntimeError(f"Server returned a null payload. Expected {expected_cls.__name__}")

            try:
                any_message = any_pb2.Any()
                any_message.ParseFromString(payload.value)

                if any_message.Is(expected_cls.DESCRIPTOR):
                    if expected_cls == UStatus:
                        return RpcMapper.calculate_status_result(any_message)
                    else:
                        return RpcResult.success(RpcMapper.unpack_payload(any_message, expected_cls))

                if any_message.Is(UStatus.DESCRIPTOR):
                    return RpcMapper.calculate_status_result(any_message)
            except Exception as e:
                raise RuntimeError(f"{str(e)} [{UStatus.__name__}]") from e

            raise RuntimeError(f"Unknown payload type [{any_message.type_url}]. Expected [{expected_cls.__name__}]")

        result = None  # Initialize result

        def callback_wrapper(payload, exception=None):
            nonlocal result
            result = handle_response(payload, exception)

        response_future.add_done_callback(callback_wrapper)
        return result

    @staticmethod
    def calculate_status_result(payload):
        status = RpcMapper.unpack_payload(payload, UStatus)
        return RpcResult.success(status) if status.code == UCode.OK else RpcResult.failure(status)

    @staticmethod
    def unpack_payload(payload, expected_cls):
        """
        Unpack a payload of type {@link Any} into an object of type T, which is what was packing into the {@link Any}
        object.<br><br>
        @param payload:an {@link Any} message containing a type of expectedClazz.
        @param expected_cls:The class name of the object packed into the {@link Any}
        @return:Returns an object of type T and of the class name specified, that was packed into the {@link Any}
        object.
        """
        try:
            payload.Unpack(expected_cls)
            return expected_cls
        except Exception as e:
            raise RuntimeError(f"{str(e)} [{UStatus.__name__}]") from e
