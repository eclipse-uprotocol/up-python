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

import socket
import unittest

from org_eclipse_uprotocol.proto.uri_pb2 import UEntity, UUri, UAuthority, UResource
from org_eclipse_uprotocol.uri.builder.uresource_builder import UResourceBuilder
from org_eclipse_uprotocol.uri.serializer.microuriserializer import MicroUriSerializer
from org_eclipse_uprotocol.uri.validator.urivalidator import UriValidator


class MicroUriSerializerTest(unittest.TestCase):

    def test_empty(self):
        bytes_uuri = MicroUriSerializer().serialize(UUri())
        self.assertEqual(len(bytes_uuri), 0)
        uri2 = MicroUriSerializer().deserialize(bytes_uuri)
        self.assertTrue(UriValidator.is_empty(uri2))

    def test_null(self):
        bytes_uuri = MicroUriSerializer().serialize(None)
        self.assertEqual(len(bytes_uuri), 0)
        uri2 = MicroUriSerializer().deserialize(None)
        self.assertTrue(UriValidator.is_empty(uri2))

    def test_serialize_uri(self):
        uri = UUri(entity=UEntity(id=29999, version_major=254), resource=UResource(id=19999))
        bytes_uuri = MicroUriSerializer().serialize(uri)
        uri2 = MicroUriSerializer().deserialize(bytes_uuri)
        self.assertEqual(uri, uri2)

    def test_serialize_remote_uri_without_address(self):
        uri = UUri(authority=UAuthority(name="vcu.vin"), entity=UEntity(id=29999, version_major=254),
                   resource=UResourceBuilder.for_rpc_response())
        bytes_uuri = MicroUriSerializer().serialize(uri)
        self.assertTrue(len(bytes_uuri) == 0)

    def test_serialize_uri_missing_ids(self):
        uri = UUri(entity=UEntity(name="hartley"), resource=UResourceBuilder.for_rpc_response())
        bytes_uuri = MicroUriSerializer().serialize(uri)
        self.assertTrue(len(bytes_uuri) == 0)

    def test_serialize_uri_missing_resource_id(self):
        uri = UUri(entity=UEntity(name="hartley"))
        bytes_uuri = MicroUriSerializer().serialize(uri)
        self.assertTrue(len(bytes_uuri) == 0)

    def test_deserialize_bad_microuri_length(self):
        badMicroUUri = bytes([0x1, 0x0, 0x0, 0x0, 0x0])
        uuri = MicroUriSerializer().deserialize(badMicroUUri)
        self.assertTrue(UriValidator.is_empty(uuri))

        badMicroUUri = bytes([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0])
        uuri = MicroUriSerializer().deserialize(badMicroUUri)
        self.assertTrue(UriValidator.is_empty(uuri))

    def test_deserialize_bad_microuri_not_version_1(self):
        badMicroUUri = bytes([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0])
        uuri = MicroUriSerializer().deserialize(badMicroUUri)
        self.assertTrue(UriValidator.is_empty(uuri))

    def test_deserialize_bad_microuri_not_valid_address_type(self):
        badMicroUUri = bytes([0x1, 0x5, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0])
        uuri = MicroUriSerializer().deserialize(badMicroUUri)
        self.assertTrue(UriValidator.is_empty(uuri))

    def test_deserialize_bad_microuri_valid_address_type_invalid_length(self):
        badMicroUUri = bytes([0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0])
        uuri = MicroUriSerializer().deserialize(badMicroUUri)
        self.assertTrue(UriValidator.is_empty(uuri))

        badMicroUUri = bytes([0x1, 0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0])
        uuri = MicroUriSerializer().deserialize(badMicroUUri)
        self.assertTrue(UriValidator.is_empty(uuri))

        badMicroUUri = bytes([0x1, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0])
        uuri = MicroUriSerializer().deserialize(badMicroUUri)
        self.assertTrue(UriValidator.is_empty(uuri))

    def test_serialize_good_ipv4_based_authority(self):
        uri = UUri(authority=UAuthority(ip=bytes(socket.inet_pton(socket.AF_INET, "10.0.3.3"))),
                   entity=UEntity(id=29999, version_major=254), resource=UResourceBuilder.for_rpc_request_with_id(99))
        bytes_uuri = MicroUriSerializer().serialize(uri)
        uri2 = MicroUriSerializer().deserialize(bytes_uuri)
        self.assertTrue(len(bytes_uuri) > 0)
        self.assertTrue(UriValidator.is_micro_form(uri))
        self.assertTrue(UriValidator.is_micro_form(uri2))
        self.assertEqual(str(uri), str(uri2))
        self.assertTrue(uri == uri2)

    def test_serialize_good_ipv6_based_authority(self):
        uri = UUri(authority=UAuthority(
            ip=bytes(socket.inet_pton(socket.AF_INET6, "2001:0db8:85a3:0000:0000:8a2e:0370:7334"))),
            entity=UEntity(id=29999, version_major=254), resource=UResource(id=19999))
        bytes_uuri = MicroUriSerializer().serialize(uri)
        uri2 = MicroUriSerializer().deserialize(bytes_uuri)
        self.assertTrue(UriValidator.is_micro_form(uri))
        self.assertTrue(len(bytes_uuri) > 0)
        self.assertTrue(uri == uri2)

    def test_serialize_id_based_authority(self):
        size = 13
        byteArray = bytearray(i for i in range(size))
        uri = UUri(authority=UAuthority(id=bytes(byteArray)), entity=UEntity(id=29999, version_major=254),
                   resource=UResource(id=19999))
        bytes_uuri = MicroUriSerializer().serialize(uri)
        uri2 = MicroUriSerializer().deserialize(bytes_uuri)
        self.assertTrue(UriValidator.is_micro_form(uri))
        self.assertTrue(len(bytes_uuri) > 0)
        self.assertTrue(uri == uri2)

    def test_serialize_bad_length_ip_based_authority(self):
        byteArray = bytes([127, 1, 23, 123, 12, 6])
        uri = UUri(authority=UAuthority(ip=bytes(byteArray)), entity=UEntity(id=29999, version_major=254),
                   resource=UResource(id=19999))
        bytes_uuri = MicroUriSerializer().serialize(uri)
        self.assertTrue(len(bytes_uuri) == 0)

    def test_serialize_id_size_255_based_authority(self):
        size = 129
        byteArray = bytes(i for i in range(size))
        uri = UUri(authority=UAuthority(id=bytes(byteArray)), entity=UEntity(id=29999, version_major=254),
                   resource=UResourceBuilder.for_rpc_request_with_id(99))
        bytes_uuri = MicroUriSerializer().serialize(uri)
        self.assertEqual(len(bytes_uuri), 9 + size)
        uri2 = MicroUriSerializer().deserialize(bytes_uuri)
        self.assertTrue(UriValidator.is_micro_form(uri))
        self.assertTrue(uri == uri2)


if __name__ == '__main__':
    unittest.main()
