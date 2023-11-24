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


import unittest
from concurrent.futures import Future
from google.protobuf.any_pb2 import Any
from google.protobuf.wrappers_pb2 import Int32Value
from org_eclipse_uprotocol.proto.cloudevents_pb2 import CloudEvent
from org_eclipse_uprotocol.proto.uattributes_pb2 import UPriority
from org_eclipse_uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from org_eclipse_uprotocol.proto.uri_pb2 import UUri, UEntity
from org_eclipse_uprotocol.proto.ustatus_pb2 import UStatus, UCode
from org_eclipse_uprotocol.rpc.rpcclient import RpcClient
from org_eclipse_uprotocol.rpc.rpcmapper import RpcMapper
from org_eclipse_uprotocol.rpc.rpcresult import RpcResult
from org_eclipse_uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from org_eclipse_uprotocol.uri.serializer.longuriserializer import LongUriSerializer


def build_cloud_event():
    return CloudEvent(spec_version="1.0", source="https://example.com", id="HARTLEY IS THE BEST")


def build_upayload():
    any_obj = Any()
    any_obj.Pack(build_cloud_event())
    return UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=any_obj.SerializeToString())


def build_topic():
    return LongUriSerializer().deserialize("//vcu.vin/hartley/1/rpc.Raise")


def build_uattributes():
    return UAttributesBuilder.request(UPriority.UPRIORITY_CS4, UUri(entity=UEntity(name="hartley")), 1000).build()


class ReturnsNumber3(RpcClient):
    def invoke_method(self, topic, payload, attributes):
        future = Future()
        any_obj = Any()
        any_obj.Pack(Int32Value(value=3))
        data = UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=any_obj.SerializeToString())
        future.set_result(data)
        return future


class HappyPath(RpcClient):
    def invoke_method(self, topic, payload, attributes):
        future = Future()
        data = build_upayload()
        future.set_result(data)
        return future


class WithUStatusCodeInsteadOfHappyPath(RpcClient):
    def invoke_method(self, topic, payload, attributes):
        future = Future()
        status = UStatus(code=UCode.INVALID_ARGUMENT, message="boom")
        any_value = Any()
        any_value.Pack(status)
        data = UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=any_value.SerializeToString())
        future.set_result(data)
        return future


class WithUStatusCodeHappyPath(RpcClient):
    def invoke_method(self, topic, payload, attributes):
        future = Future()
        status = UStatus(code=UCode.OK, message="all good")
        any_value = Any()
        any_value.Pack(status)
        data = UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=any_value.SerializeToString())
        future.set_result(data)
        return future


class ThatBarfsCrapyPayload(RpcClient):
    def invoke_method(self, topic, payload, attributes):
        future = Future()
        response = UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_RAW, value=bytes([0]))
        future.set_result(response)
        return future


class ThatCompletesWithAnException(RpcClient):
    def invoke_method(self, topic, payload, attributes):
        future = Future()
        future.set_exception(RuntimeError("Boom"))
        return future


class ThatReturnsTheWrongProto(RpcClient):
    def invoke_method(self, topic, payload, attributes):
        future = Future()
        any_value = Any()
        any_value.Pack(Int32Value(value=42))
        data = UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=any_value.SerializeToString())
        future.set_result(data)
        return future


class WithNullInPayload(RpcClient):
    def invoke_method(self, topic, payload, attributes):
        future = Future()
        future.set_result(None)
        return future


def rpc_response(invoke_method_response: Future):
    payload, exception = invoke_method_response.result()

    any_value = Any()
    try:
        any_value.ParseFromString(payload.value)
    except Exception as e:
        raise RuntimeError(str(e)) from e

    # invoke method had some unexpected problem.
    if exception is not None:
        raise RuntimeError(str(exception)) from exception

    # test to see if we have the expected type
    if any_value.Is(CloudEvent.DESCRIPTOR):
        try:
            cloud_event = CloudEvent()
            any_value.Unpack(cloud_event)
            return cloud_event
        except Exception as e:
            raise RuntimeError(str(e)) from e

    # this will be called only if the expected return type is not status, but status was returned to
    # indicate a problem.
    if any_value.Is(UStatus.DESCRIPTOR):
        try:
            status = UStatus()
            any_value.Unpack(status)
            raise RuntimeError(f"Error returned, status code: [{status.code}], message: [{status.message}]")
        except Exception as e:
            raise RuntimeError(f"{str(e)} [com.google.grpc.UStatus]") from e

    raise RuntimeError(f"Unknown payload type [{any_value.type_url}]")


class TestRpc(unittest.TestCase):

    def test_compose_happy_path(self):
        rpc_response = RpcMapper.map_response_to_result(
            ReturnsNumber3().invoke_method(build_topic(), build_upayload(), build_uattributes()), Int32Value)
        mapped = rpc_response.map(lambda x: x.value + 5)
        self.assertTrue(rpc_response.isSuccess())
        self.assertEquals(8, mapped.successValue())

    def test_compose_that_returns_status(self):
        rpc_response = RpcMapper.map_response_to_result(
            WithUStatusCodeInsteadOfHappyPath().invoke_method(build_topic(), build_upayload(), build_uattributes()), Int32Value)
        mapped = rpc_response.map(lambda x: x.value + 5)
        self.assertTrue(rpc_response.isFailure())
        self.assertEquals(UCode.INVALID_ARGUMENT, mapped.failureValue().code)
        self.assertEquals("boom", mapped.failureValue().message)







