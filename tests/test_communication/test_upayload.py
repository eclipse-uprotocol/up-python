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

from google.protobuf import message

from uprotocol.communication.upayload import UPayload
from uprotocol.v1.uattributes_pb2 import (
    UPayloadFormat,
)
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri


class TestUPayload(unittest.TestCase):
    def test_is_empty_with_null_upayload(self):
        self.assertTrue(UPayload.is_empty(UPayload.pack(None)))
        self.assertTrue(UPayload.is_empty(UPayload.pack_to_any(None)))

    def test_is_empty_when_building_a_valid_upayload_that_data_is_empty_but_format_is_not(self):
        payload = UPayload.pack(UUri())
        self.assertFalse(UPayload.is_empty(payload))

    def test_is_empty_when_building_a_valid_upayload_where_both_data_and_format_are_not_empty(self):
        uri = UUri(authority_name="Neelam")
        payload = UPayload.pack_to_any(uri)
        self.assertFalse(UPayload.is_empty(payload))

    def test_is_empty_when_passing_null(self):
        self.assertTrue(UPayload.is_empty(None))

    def test_unpacking_a_upayload_calling_unpack_with_null(self):
        self.assertFalse(isinstance(UPayload.unpack(None, UUri), message.Message))
        self.assertFalse(isinstance(UPayload.unpack(UPayload.pack(None), UUri), message.Message))

    def test_unpacking_passing_a_null_bytestring(self):
        self.assertFalse(
            isinstance(
                UPayload.unpack_data_format(None, UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, UUri), message.Message
            )
        )

    def test_unpacking_a_google_protobuf_any_packed_upayload(self):
        uri = UUri(authority_name="Neelam")
        payload = UPayload.pack_to_any(uri)
        unpacked = UPayload.unpack(payload, UUri)
        self.assertTrue(isinstance(unpacked, message.Message))
        self.assertEqual(uri, unpacked)

    def test_unpacking_an_unsupported_format_in_upayload(self):
        uri = UUri(authority_name="Neelam")
        payload = UPayload.pack_from_data_and_format(uri.SerializeToString(), UPayloadFormat.UPAYLOAD_FORMAT_JSON)
        unpacked = UPayload.unpack(payload, UUri)
        self.assertFalse(isinstance(unpacked, message.Message))
        self.assertEqual(unpacked, None)

    def test_unpacking_to_unpack_a_message_of_the_wrong_type(self):
        uri = UUri(authority_name="Neelam")
        unpacked = UPayload.unpack_data_format(
            uri.SerializeToString(), UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, UMessage
        )
        self.assertFalse(isinstance(unpacked, message.Message))
        self.assertEqual(unpacked, None)

    def test_equals_when_they_are_equal(self):
        uri = UUri(authority_name="Neelam")
        payload1 = UPayload.pack_to_any(uri)
        payload2 = UPayload.pack_to_any(uri)
        self.assertEqual(payload1, payload2)

    def test_equals_when_they_are_not_equal(self):
        uri1 = UUri(authority_name="Neelam")
        uri2 = UUri(authority_name="Neelam")
        payload1 = UPayload.pack_to_any(uri1)
        payload2 = UPayload.pack(uri2)
        self.assertNotEqual(payload1, payload2)

    def test_equals_when_object_is_null(self):
        uri = UUri(authority_name="Neelam")
        payload = UPayload.pack_to_any(uri)
        self.assertFalse(payload is None)

    def test_equals_when_object_is_not_an_instance_of_upayload(self):
        uri = UUri(authority_name="Neelam")
        payload = UPayload.pack_to_any(uri)
        self.assertFalse(payload is uri)

    def test_equals_when_it_is_the_same_object(self):
        uri = UUri(authority_name="Neelam")
        payload = UPayload.pack_to_any(uri)
        self.assertTrue(payload is payload)

    def test_equals_when_the_data_is_the_same_but_the_format_is_not(self):
        uri = UUri(authority_name="Neelam")
        payload1 = UPayload.pack_from_data_and_format(uri.SerializeToString(), UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF)
        payload2 = UPayload.pack_from_data_and_format(uri.SerializeToString(), UPayloadFormat.UPAYLOAD_FORMAT_JSON)
        self.assertNotEqual(payload1, payload2)

    def test_hash_code(self):
        uri = UUri(authority_name="Neelam")
        payload = UPayload.pack_to_any(uri)
        self.assertEqual(payload.__hash__(), payload.__hash__())


if __name__ == '__main__':
    unittest.main()
