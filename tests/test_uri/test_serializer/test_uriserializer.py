"""
SPDX-FileCopyrightText: 2023 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import unittest

from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.v1.uri_pb2 import UUri


class TestUriSerializer(unittest.TestCase):
    def test_using_the_serializers(self):
        uri = UUri(
            authority_name="myAuthority",
            ue_id=1,
            ue_version_major=2,
            resource_id=3,
        )
        serialized_uri = UriSerializer.serialize(uri)
        self.assertEqual(serialized_uri, "//myAuthority/1/2/3")

    def test_deserializing_a_null_uuri(self):
        uri = UriSerializer.deserialize(None)
        self.assertTrue(UriValidator.is_empty(uri))

    def test_deserializing_a_empty_uuri(self):
        uri = UriSerializer.deserialize("")
        self.assertTrue(UriValidator.is_empty(uri))

    def test_deserializing_a_blank_uuri(self):
        uri = UriSerializer.deserialize(" ")
        self.assertTrue(UriValidator.is_empty(uri))

    def test_deserializing_with_a_valid_uri_that_has_scheme(self):
        uri = UriSerializer.deserialize("up://myAuthority/1/2/3")

        self.assertEqual(uri.authority_name, "myAuthority")
        self.assertEqual(uri.ue_id, 1)
        self.assertEqual(uri.ue_version_major, 2)
        self.assertEqual(uri.resource_id, 3)

    def test_deserializing_with_a_valid_uri_that_has_only_scheme(self):
        uri = UriSerializer.deserialize("up://")
        self.assertTrue(UriValidator.is_empty(uri))

    def test_deserializing_a_valid_uuri_with_all_fields(self):
        uri = UriSerializer.deserialize("//myAuthority/1/2/3")

        self.assertEqual(uri.authority_name, "myAuthority")
        self.assertEqual(uri.ue_id, 1)
        self.assertEqual(uri.ue_version_major, 2)
        self.assertEqual(uri.resource_id, 3)

    def test_deserializing_with_only_authority(self):
        uri = UriSerializer.deserialize("//myAuthority")

        self.assertEqual(uri.authority_name, "myAuthority")
        self.assertEqual(uri.ue_id, 0)
        self.assertEqual(uri.ue_version_major, 0)
        self.assertEqual(uri.resource_id, 0)

    def test_deserializing_authority_ueid(self):
        uri = UriSerializer.deserialize("//myAuthority/1")

        self.assertEqual(uri.authority_name, "myAuthority")
        self.assertEqual(uri.ue_id, 1)
        self.assertEqual(uri.ue_version_major, 0)
        self.assertEqual(uri.resource_id, 0)

    def test_deserializing_authority_ueid_ueversion(self):
        uri = UriSerializer.deserialize("//myAuthority/1/2")

        self.assertEqual(uri.authority_name, "myAuthority")
        self.assertEqual(uri.ue_id, 1)
        self.assertEqual(uri.ue_version_major, 2)
        self.assertEqual(uri.resource_id, 0)

    def test_deserializing_a_string_with_invalid_chars(self):
        uri = UriSerializer.deserialize("$$")
        self.assertTrue(UriValidator.is_empty(uri))

    def test_deserializing_with_names_instead_of_id_for_ueid(self):
        uri = UriSerializer.deserialize("//myAuthority/one/2/3")
        self.assertTrue(UriValidator.is_empty(uri))

    def test_deserializing_with_names_instead_of_id_for_ueversion(self):
        uri = UriSerializer.deserialize("//myAuthority/1/two/3")
        self.assertTrue(UriValidator.is_empty(uri))

    def test_deserializing_with_names_instead_of_id_for_resource_id(self):
        uri = UriSerializer.deserialize("//myAuthority/1/2/three")
        self.assertTrue(UriValidator.is_empty(uri))

    def test_deserializing_a_string_without_authority(self):
        uri = UriSerializer.deserialize("/1/2/3")

        self.assertEqual(uri.authority_name, "")
        self.assertEqual(uri.ue_id, 1)
        self.assertEqual(uri.ue_version_major, 2)
        self.assertEqual(uri.resource_id, 3)

    def test_deserializing_without_authority_and_resourceid(self):
        uri = UriSerializer.deserialize("/1/2")

        self.assertEqual(uri.authority_name, "")
        self.assertEqual(uri.ue_id, 1)
        self.assertEqual(uri.ue_version_major, 2)
        self.assertEqual(uri.resource_id, 0)

    def test_deserializing_without_authority_resourceid_version_major(self):
        uri = UriSerializer.deserialize("/1")

        self.assertEqual(uri.authority_name, "")
        self.assertEqual(uri.ue_id, 1)
        self.assertEqual(uri.ue_version_major, 0)
        self.assertEqual(uri.resource_id, 0)

    def test_deserializing_with_blank_authority(self):
        uri = UriSerializer.deserialize("///2")
        self.assertTrue(UriValidator.is_empty(uri))

    def test_deserializing_with_all_wildcard_values(self):
        uri = UriSerializer.deserialize("//*/FFFF/ff/ffff")

        self.assertEqual(uri.authority_name, "*")
        self.assertEqual(uri.ue_id, 0xFFFF)
        self.assertEqual(uri.ue_version_major, 0xFF)
        self.assertEqual(uri.resource_id, 0xFFFF)

    def test_deserializing_with_ueid_out_of_range(self):
        uri = UriSerializer.deserialize("/fffffffff/2/3")
        self.assertTrue(UriValidator.is_empty(uri))

    def test_deserializing_with_ueversionmajor_out_of_range(self):
        uri = UriSerializer.deserialize("/1/256/3")
        self.assertTrue(UriValidator.is_empty(uri))

    def test_deserializing_with_resourceid_out_of_range(self):
        uri = UriSerializer.deserialize("/1/2/65536")
        self.assertTrue(UriValidator.is_empty(uri))

    def test_deserializing_with_negative_ueid(self):
        uri = UriSerializer.deserialize("/-1/2/3")
        self.assertTrue(UriValidator.is_empty(uri))

    def test_deserializing_with_negative_versionmajor(self):
        uri = UriSerializer.deserialize("/1/-2/3")
        self.assertTrue(UriValidator.is_empty(uri))

    def test_deserializing_with_negative_resourceid(self):
        uri = UriSerializer.deserialize("/1/2/-3")
        self.assertTrue(UriValidator.is_empty(uri))

    def test_deserializing_with_wildcard_resourceid(self):
        uri = UriSerializer.deserialize("/1/2/ffff")

        self.assertEqual(uri.authority_name, "")
        self.assertEqual(uri.ue_id, 1)
        self.assertEqual(uri.ue_version_major, 2)
        self.assertEqual(uri.resource_id, 0xFFFF)

    def test_serializing_an_empty_uri(self):
        uri = UUri()
        serialized_uri = UriSerializer.serialize(uri)
        self.assertEqual(serialized_uri, "")

    def test_serializing_a_none_uri(self):
        serialized_uri = UriSerializer.serialize(None)

        self.assertEqual(serialized_uri, "")

    def test_serializing_only_authority_ueid(self):
        uri = UUri(authority_name="myAuthority", ue_id=1)
        serialized_uri = UriSerializer.serialize(uri)

        self.assertEqual(serialized_uri, "//myAuthority/1/0/0")

    def test_serializing_only_authority_ueid_version_major(self):
        uri = UUri(authority_name="myAuthority", ue_id=1, ue_version_major=2)
        serialized_uri = UriSerializer.serialize(uri)

        self.assertEqual(serialized_uri, "//myAuthority/1/2/0")


if __name__ == "__main__":
    unittest.main()
