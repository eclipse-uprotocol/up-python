# -------------------------------------------------------------------------

# Copyright (c) 2023 General Motors GTO LLC

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# -------------------------------------------------------------------------

from concurrent.futures import Future

from google.rpc.code_pb2 import Code
from google.rpc.status_pb2 import Status

from org_eclipse_uprotocol.rpc.rpcresult import RpcResult
from org_eclipse_uprotocol.transport.datamodel.upayload import UPayload


class RpcMapper:
    @staticmethod
    def map_response(response_future: Future, expected_cls):
        def handle_response(payload, exception):
            if exception:
                raise exception
            payload = payload.result()
            if not payload:
                raise RuntimeError(f"Server returned a null payload. Expected {expected_cls.__name__}")

            try:
                any_message = UPayload.get_any_from_payload_data(payload.data)
                if any_message.Is(expected_cls.DESCRIPTOR):
                    return RpcMapper.unpack_payload(any_message, expected_cls)
            except Exception as e:
                raise RuntimeError(f"{str(e)} [{Status.__name__}]") from e

            raise RuntimeError(f"Unknown payload type [{any_message.type_url}]. Expected [{expected_cls.__name__}]")

        result = None  # Initialize result

        def callbackwrapper(payload, exception=None):
            nonlocal result
            result = handle_response(payload, exception)

        response_future.add_done_callback(callbackwrapper)
        return result

    @staticmethod
    def map_response_to_result(response_future: Future, expected_cls):
        def handle_response(payload, exception=None):
            if exception:
                raise exception
            payload = payload.result()
            if not payload:
                raise RuntimeError(f"Server returned a null payload. Expected {expected_cls.__name__}")

            try:
                any_message = UPayload.get_any_from_payload_data(payload.data)

                if any_message.Is(expected_cls.DESCRIPTOR):
                    if expected_cls == Status:
                        return RpcMapper.calculate_status_result(any_message)
                    else:
                        return RpcResult.success(RpcMapper.unpack_payload(any_message, expected_cls))

                if any_message.Is(Status.DESCRIPTOR):
                    return RpcMapper.calculate_status_result(any_message)
            except Exception as e:
                raise RuntimeError(f"{str(e)} [{Status.__name__}]") from e

            raise RuntimeError(f"Unknown payload type [{any_message.type_url}]. Expected [{expected_cls.__name__}]")

        result = None  # Initialize result

        def callback_wrapper(payload, exception=None):
            nonlocal result
            result = handle_response(payload, exception)

        response_future.add_done_callback(callback_wrapper)
        return result

    @staticmethod
    def calculate_status_result(payload):
        status = RpcMapper.unpack_payload(payload, Status)
        return RpcResult.success(status) if status.code == Code.OK else RpcResult.failure(status)

    @staticmethod
    def unpack_payload(payload, expected_cls):
        try:
            payload.Unpack(expected_cls)
            return expected_cls
        except Exception as e:
            raise RuntimeError(f"{str(e)} [{Status.__name__}]") from e
