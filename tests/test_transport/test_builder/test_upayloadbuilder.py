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

import unittest
from google.protobuf.any_pb2 import Any
from google.protobuf.wrappers_pb2 import BoolValue
from google.protobuf.api_pb2 import Method
from google.protobuf.message import Message
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat

from uprotocol.transport.builder.upayloadbuilder import UPayloadBuilder


class TestUPayloadBuilder(unittest.TestCase):

    def _create_upayload_builder(self):
        return UPayloadBuilder()

    def _assert_pack_to_any(self, expected: Message, actual: UPayload):
        self.assertEqual(
            UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
            actual.format,
        )
        self.assertEqual(0, actual.length)
        self.assertEqual(0, actual.reference)
        self.assertEqual(expected.SerializeToString(), actual.value)

    def test_pack_to_any_given_boolvalue_returns_upayload(self):
        builder = self._create_upayload_builder()

        msg: Message = BoolValue(value=True)
        any_message = Any()
        any_message.Pack(msg)

        upayload: UPayload = builder.pack_to_any(msg)
        self.assertIsNotNone(upayload)

        self._assert_pack_to_any(any_message, upayload)

    def test_pack_to_any_given_any_returns_upayload(self):
        builder = self._create_upayload_builder()

        msg: Message = Any(type_url=None, value=b"bytes")
        any_message = Any()
        any_message.Pack(msg)

        upayload: UPayload = builder.pack_to_any(msg)
        self.assertIsNotNone(upayload)

        self._assert_pack_to_any(any_message, upayload)

    def test_pack_to_any_given_method_returns_upayload(self):
        builder = self._create_upayload_builder()

        msg: Message = Method(
            name="name",
            request_type_url="request_type_url",
            response_type_url="response_type_url",
            request_streaming=None,
        )
        any_message = Any()
        any_message.Pack(msg)

        upayload: UPayload = builder.pack_to_any(msg)
        self.assertIsNotNone(upayload)

        self._assert_pack_to_any(any_message, upayload)

    def _assert_pack(self, expected: Message, actual: UPayload):
        self.assertEqual(
            UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, actual.format
        )
        self.assertEqual(0, actual.length)
        self.assertEqual(0, actual.reference)
        self.assertEqual(expected.SerializeToString(), actual.value)

    def test_pack_given_boolvalue_returns_upayload(self):
        builder = self._create_upayload_builder()

        msg: Message = BoolValue(value=True)

        upayload: UPayload = builder.pack(msg)

        self._assert_pack(msg, upayload)

    def test_pack_given_any_returns_upayload(self):
        builder = self._create_upayload_builder()

        msg: Message = Any(type_url=None, value=b"bytes")

        upayload: UPayload = builder.pack(msg)

        self._assert_pack(msg, upayload)

    def test_pack_given_method_returns_upayload(self):
        builder = self._create_upayload_builder()

        msg: Message = Method(
            name="name",
            request_type_url="request_type_url",
            response_type_url="response_type_url",
            request_streaming=None,
        )

        upayload: UPayload = builder.pack(msg)

        self._assert_pack(msg, upayload)

    def test_unpack_given_pack_returns_boolvalue(self):
        builder = self._create_upayload_builder()

        original_msg: Message = BoolValue(value=False)
        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF,
            value=original_msg.SerializeToString(),
        )

        unpacked_msg: BoolValue = builder.unpack(upayload, BoolValue)

        self.assertEqual(original_msg, unpacked_msg)

    def test_unpack_given_upayload_proto_returns_method(self):
        builder = self._create_upayload_builder()

        original_msg: Message = Method(
            name="name",
            request_type_url="request_type_url",
            response_type_url="response_type_url",
            request_streaming=None,
        )
        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF,
            value=original_msg.SerializeToString(),
        )

        unpacked_msg: Method = builder.unpack(upayload, Method)

        self.assertEqual(original_msg, unpacked_msg)

    def test_unpack_exception(self):
        builder = self._create_upayload_builder()

        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF,
            value=b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        )

        unpacked_msg: Method = builder.unpack(upayload, Method)

        self.assertEqual(unpacked_msg, None)

    def test_unpack_given_upayload_proto_returns_any(self):
        builder = self._create_upayload_builder()

        original_msg: Message = Any(type_url=None, value=b"bytes")
        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF,
            value=original_msg.SerializeToString(),
        )

        unpacked_msg: Any = builder.unpack(upayload, Any)

        self.assertEqual(original_msg, unpacked_msg)

    def test_unpack_given_any_wrapped_upayload_returns_boolvalue(self):
        builder = self._create_upayload_builder()

        original_msg: Message = BoolValue(value=False)
        any_message = Any()
        any_message.Pack(original_msg)

        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
            value=any_message.SerializeToString(),
        )

        unpacked_msg: BoolValue = builder.unpack(upayload, BoolValue)

        self.assertEqual(original_msg, unpacked_msg)

    def test_unpack_given_any_wrapped_upayload_returns_any(self):
        builder = self._create_upayload_builder()

        original_msg: Message = Any(value=b"bytes")
        any_message = Any()
        any_message.Pack(original_msg)

        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
            value=any_message.SerializeToString(),
        )

        unpacked_msg: Any = builder.unpack(upayload, Any)

        self.assertEqual(original_msg, unpacked_msg)

    def test_unpack_given_any_wrapped_upayload_returns_method(self):
        builder = self._create_upayload_builder()

        original_msg: Message = Method(
            name="name",
            request_type_url="request_type_url",
            response_type_url="response_type_url",
            request_streaming=None,
        )
        any_message = Any()
        any_message.Pack(original_msg)

        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
            value=any_message.SerializeToString(),
        )

        unpacked_msg: Method = builder.unpack(upayload, Method)

        self.assertEqual(original_msg, unpacked_msg)

    def test_unpack_given_wrong_format_returns_none(self):
        builder = self._create_upayload_builder()

        original_msg: Message = Any()
        any_message = Any()
        any_message.Pack(original_msg)

        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_JSON,
            value=any_message.SerializeToString(),
        )

        unpacked_msg: Any = builder.unpack(upayload, Any)

        self.assertIsNone(unpacked_msg)

    def test_unpack_given_none_returns_none(self):
        builder = self._create_upayload_builder()

        unpacked_msg: Any = builder.unpack(None, Any)

        self.assertIsNone(unpacked_msg)

    def test_unpack_given_no_upayload_value_returns_none(self):
        builder = self._create_upayload_builder()

        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_JSON
        )

        unpacked_msg: Any = builder.unpack(upayload, Any)

        self.assertIsNone(unpacked_msg)
