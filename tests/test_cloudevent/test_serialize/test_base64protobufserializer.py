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

from uprotocol.cloudevent.datamodel.ucloudeventattributes import UCloudEventAttributesBuilder
from uprotocol.cloudevent.factory.cloudeventfactory import CloudEventFactory
from uprotocol.cloudevent.serialize.base64protobufserializer import Base64ProtobufSerializer
from uprotocol.cloudevent.serialize.cloudeventserializers import CloudEventSerializers


class TestBase64ProtobufSerializer(unittest.TestCase):

    def test_deserialize_bytes_to_string(self):
        ce = CloudEventFactory.build_base_cloud_event("hello", "http://localhost", bytearray(), "",
                                                      UCloudEventAttributesBuilder().build(), "example.vertx")
        ce.__delitem__("time")
        bytes_data = CloudEventSerializers.PROTOBUF.serializer().serialize(ce)
        payload = Base64ProtobufSerializer().deserialize(bytes_data)
        self.assertEquals(
            "CgVoZWxsbxIQaHR0cDovL2xvY2FsaG9zdBoDMS4wIg1leGFtcGxlLnZlcnR4",
            payload)

    def test_deserialize_bytes_to_string_when_bytes_is_null(self):
        payload = Base64ProtobufSerializer().deserialize(None)
        self.assertEquals("", payload)

    def test_deserialize_bytes_to_string_when_bytes_is_empty(self):
        payload = Base64ProtobufSerializer().deserialize(bytearray())
        self.assertEquals("", payload)

    def test_serialize_string_into_bytes(self):
        json_str = "eyJzcGVjdmVyc2lvbiI6ICIxLjAiLCAiaWQiOiAiaGVsbG8iLCAic291cmNlIjogImh0dHA6Ly9sb2NhbGhvc3QiLCAidHlwZSI6ICJleGFtcGxlLnZlcnR4IiwgImRhdGFfYmFzZTY0IjogIiJ9"
        bytes_json = Base64ProtobufSerializer().serialize(json_str)

        ce = CloudEventFactory.build_base_cloud_event("hello", "http://localhost", bytearray(), "",
                                                      UCloudEventAttributesBuilder().build(), "example.vertx")
        ce.__delitem__("time")

        bytes_data = CloudEventSerializers.JSON.serializer().serialize(ce)
        self.assertEquals(bytes_json, bytes_data)

    def test_serialize_string_into_bytes_when_string_is_null(self):
        bytes_data = Base64ProtobufSerializer().serialize(None)
        self.assertEquals(bytearray(), bytes_data)

    def test_serialize_string_into_bytes_when_string_is_empty(self):
        bytes_data = Base64ProtobufSerializer().serialize('')
        self.assertEquals(bytearray(), bytes_data)


if __name__ == '__main__':
    unittest.main()
