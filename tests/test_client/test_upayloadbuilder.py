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

from uprotocol.client.upayload import UPayload

from uprotocol.proto.uprotocol.v1.uattributes_pb2 import UPayloadFormat


class TestUPayloadBuilder(unittest.TestCase):

    def _assert_pack_to_any(self, expected, actual: UPayload):
        self.assertEqual(
            UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
            actual.get_format(),
        )
        self.assertEqual(expected.SerializeToString(), actual.get_data())

    def test_pack_to_any_given_boolvalue_returns_upayload(self):

        msg: BoolValue = BoolValue(value=True)
        any_message = Any()
        any_message.Pack(msg)

        upayload: UPayload = UPayload.pack_to_any(msg)
        self.assertIsNotNone(upayload)

    def test_pack_to_any_given_any_returns_upayload(self):

        msg: Any = Any(type_url=None, value=b"bytes")
        any_message = Any()
        any_message.Pack(msg)

        upayload: UPayload = UPayload.pack_to_any(msg)
        self.assertIsNotNone(upayload)

        self._assert_pack_to_any(any_message, upayload)

    def test_pack_to_any_given_method_returns_upayload(self):

        msg: Method = Method(
            name="name",
            request_type_url="request_type_url",
            response_type_url="response_type_url",
            request_streaming=None,
        )
        any_message = Any()
        any_message.Pack(msg)

        upayload: UPayload = UPayload.pack_to_any(msg)
        self.assertIsNotNone(upayload)

        self._assert_pack_to_any(any_message, upayload)

    def _assert_pack(self, expected, actual: UPayload):
        self.assertEqual(
            UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, actual.get_format()
        )
        self.assertEqual(expected.SerializeToString(), actual.get_data())

    def test_pack_given_boolvalue_returns_upayload(self):

        msg: BoolValue = BoolValue(value=True)

        upayload: UPayload = UPayload.pack(msg)

        self._assert_pack(msg, upayload)

    def test_pack_given_any_returns_upayload(self):

        msg: Any = Any(type_url=None, value=b"bytes")

        upayload: UPayload = UPayload.pack(msg)

        self._assert_pack(msg, upayload)

    def test_pack_given_method_returns_upayload(self):

        msg: Method = Method(
            name="name",
            request_type_url="request_type_url",
            response_type_url="response_type_url",
            request_streaming=None,
        )

        upayload: UPayload = UPayload.pack(msg)

        self._assert_pack(msg, upayload)

    def test_unpack_given_pack_returns_boolvalue(self):

        original_msg: BoolValue = BoolValue(value=False)
        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF,
            data=original_msg.SerializeToString(),
        )

        unpacked_msg: BoolValue = UPayload.unpack(upayload, BoolValue)

        self.assertEqual(original_msg, unpacked_msg)

    def test_unpack_given_upayload_proto_returns_method(self):

        original_msg: Method = Method(
            name="name",
            request_type_url="request_type_url",
            response_type_url="response_type_url",
            request_streaming=None,
        )
        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF,
            data=original_msg.SerializeToString(),
        )

        unpacked_msg: Method = UPayload.unpack(upayload, Method)

        self.assertEqual(original_msg, unpacked_msg)

    def test_unpack_exception(self):

        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF,
            data=b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        )

        unpacked_msg: Method = UPayload.unpack(upayload, Method)

        self.assertIsNone(unpacked_msg)

    def test_unpack_given_upayload_proto_returns_any(self):

        original_msg: Any = Any(type_url=None, value=b"bytes")
        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF,
            data=original_msg.SerializeToString(),
        )

        unpacked_msg: Any = UPayload.unpack(upayload, Any)

        self.assertEqual(original_msg, unpacked_msg)

    def test_unpack_given_any_wrapped_upayload_returns_boolvalue(self):

        original_msg: BoolValue = BoolValue(value=False)
        any_message = Any()
        any_message.Pack(original_msg)

        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
            data=any_message.SerializeToString(),
        )

        unpacked_msg: BoolValue = UPayload.unpack(upayload, BoolValue)

        self.assertEqual(original_msg, unpacked_msg)

    def test_unpack_given_any_wrapped_upayload_returns_any(self):

        original_msg: Any = Any(value=b"bytes")
        any_message = Any()
        any_message.Pack(original_msg)

        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
            data=any_message.SerializeToString(),
        )

        unpacked_msg: Any = UPayload.unpack(upayload, Any)

        self.assertEqual(original_msg, unpacked_msg)

    def test_unpack_given_any_wrapped_upayload_returns_method(self):

        original_msg: Method = Method(
            name="name",
            request_type_url="request_type_url",
            response_type_url="response_type_url",
            request_streaming=None,
        )
        any_message = Any()
        any_message.Pack(original_msg)

        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
            data=any_message.SerializeToString(),
        )

        unpacked_msg: Method = UPayload.unpack(upayload, Method)

        self.assertEqual(original_msg, unpacked_msg)

    def test_unpack_given_wrong_format_returns_none(self):

        original_msg: Any = Any()
        any_message = Any()
        any_message.Pack(original_msg)

        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_JSON,
            data=any_message.SerializeToString(),
        )

        unpacked_msg: Any = UPayload.unpack(upayload, Any)

        self.assertIsNone(unpacked_msg)

    def test_unpack_given_none_returns_none(self):

        unpacked_msg: Any = UPayload.unpack(None, Any)

        self.assertIsNone(unpacked_msg)

    def test_unpack_given_no_upayload_value_returns_none(self):

        upayload: UPayload = UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_JSON,
            data=None,
        )

        unpacked_msg: Any = UPayload.unpack(upayload, Any)

        self.assertIsNone(unpacked_msg)
