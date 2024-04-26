# -------------------------------------------------------------------------
#
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
#
# -------------------------------------------------------------------------


import unittest

from uprotocol.proto.uri_pb2 import UEntity, UUri, UAuthority, UResource
from uprotocol.uri.factory.uresource_builder import UResourceBuilder
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.uri.validator.urivalidator import UriValidator


class TestLongUriSerializer(unittest.TestCase):

    def test_using_the_serializers(self):
        uri = UUri(
            entity=UEntity(name="hartley"),
            resource=UResourceBuilder.for_rpc_request("raise"),
        )

        str_uri = LongUriSerializer().serialize(uri)
        self.assertEqual("/hartley//rpc.raise", str_uri)
        uri2 = LongUriSerializer().deserialize(str_uri)
        self.assertEqual(uri, uri2)

    def test_parse_protocol_uri_when_is_null(self):
        uri = LongUriSerializer().deserialize(None)
        self.assertTrue(UriValidator.is_empty(uri))
        self.assertFalse(UriValidator.is_resolved(uri))
        self.assertFalse(UriValidator.is_long_form(uri))

    def test_parse_protocol_uri_when_is_empty_string(self):
        uri = ""
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_empty(uuri))
        uri2 = LongUriSerializer().serialize(None)
        self.assertTrue(len(uri2) == 0)

    def test_parse_protocol_uri_with_schema_and_slash(self):
        uri = "/"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(uuri.HasField("authority"))
        self.assertTrue(UriValidator.is_empty(uuri))
        self.assertFalse(uuri.HasField("resource"))
        self.assertFalse(uuri.HasField("entity"))
        uri2 = LongUriSerializer().serialize(UUri())
        self.assertTrue(len(uri2) == 0)

    def test_parse_protocol_uri_with_schema_and_double_slash(self):
        uri = "//"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(uuri.HasField("authority"))
        self.assertFalse(uuri.HasField("resource"))
        self.assertFalse(uuri.HasField("entity"))
        self.assertTrue(UriValidator.is_empty(uuri))

    def test_parse_protocol_uri_with_schema_and_3_slash_and_something(self):
        uri = "///body.access"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(uuri.HasField("authority"))
        self.assertFalse(uuri.HasField("resource"))
        self.assertFalse(uuri.HasField("entity"))
        self.assertTrue(UriValidator.is_empty(uuri))
        self.assertNotEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)

    def test_parse_protocol_uri_with_schema_and_4_slash_and_something(self):
        uri = "////body.access"
        uuri = LongUriSerializer().deserialize(uri)

        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertFalse(uuri.HasField("resource"))
        self.assertFalse(uuri.HasField("entity"))
        self.assertTrue(len(uuri.entity.name) == 0)
        self.assertEqual(0, uuri.entity.version_major)

    def test_parse_protocol_uri_with_schema_and_5_slash_and_something(self):
        uri = "/////body.access"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertFalse(uuri.HasField("resource"))
        self.assertFalse(uuri.HasField("entity"))
        self.assertTrue(UriValidator.is_empty(uuri))

    def test_parse_protocol_uri_with_schema_and_6_slash_and_something(self):
        uri = "//////body.access"
        uuri = LongUriSerializer().deserialize(uri)

        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertTrue(UriValidator.is_empty(uuri))

    def test_parse_protocol_uri_with_local_service_no_version(self):
        uri = "/body.access"
        uuri = LongUriSerializer().deserialize(uri)

        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual(0, uuri.entity.version_minor)
        self.assertFalse(uuri.HasField("resource"))

    def test_parse_protocol_uri_with_local_service_with_version(self):
        uri = "/body.access/1"
        uuri = LongUriSerializer().deserialize(uri)

        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertFalse(uuri.HasField("resource"))

    def test_parse_protocol_uri_with_local_service_no_version_with_resource_name_only(
        self,
    ):
        uri = "/body.access//door"
        uuri = LongUriSerializer().deserialize(uri)

        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual(0, uuri.entity.version_minor)
        self.assertEqual("door", uuri.resource.name)
        self.assertTrue(len(uuri.resource.instance) == 0)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_local_service_with_version_with_resource_name_only(
        self,
    ):
        uri = "/body.access/1/door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertTrue(len(uuri.resource.instance) == 0)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_local_service_no_version_with_resource_with_instance(
        self,
    ):
        uri = "/body.access//door.front_left"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_local_service_with_version_with_resource_with_getMessage(
        self,
    ):
        uri = "/body.access/1/door.front_left"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_local_service_no_version_with_resource_with_instance_and_getMessage(
        self,
    ):
        uri = "/body.access//door.front_left#Door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertFalse(len(uuri.resource.message) == 0)
        self.assertEqual("Door", uuri.resource.message)

    def test_parse_protocol_uri_with_local_service_with_version_with_resource_with_instance_and_getMessage(
        self,
    ):
        uri = "/body.access/1/door.front_left#Door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertFalse(len(uuri.resource.message) == 0)
        self.assertEqual("Door", uuri.resource.message)

    def test_parse_protocol_rpc_uri_with_local_service_no_version(self):
        uri = "/petapp//rpc.response"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("petapp", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("rpc", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("response", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_rpc_uri_with_local_service_with_version(self):
        uri = "/petapp/1/rpc.response"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("petapp", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("rpc", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("response", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_remote_service_only_device_and_domain(
        self,
    ):
        uri = "//VCU.MY_CAR_VIN"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)

    def test_parse_protocol_uri_with_remote_service_only_device_and_cloud_domain(
        self,
    ):
        uri = "//cloud.uprotocol.example.com"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("cloud.uprotocol.example.com", uuri.authority.name)
        self.assertFalse(uuri.HasField("entity"))
        self.assertFalse(uuri.HasField("resource"))

    def test_parse_protocol_uri_with_remote_service_no_version(self):
        uri = "//VCU.MY_CAR_VIN/body.access"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertFalse(uuri.HasField("resource"))

    def test_parse_protocol_uri_with_remote_cloud_service_no_version(self):
        uri = "//cloud.uprotocol.example.com/body.access"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("cloud.uprotocol.example.com", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertFalse(uuri.HasField("resource"))

    def test_parse_protocol_uri_with_remote_service_with_version(self):
        uri = "//VCU.MY_CAR_VIN/body.access/1"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertFalse(uuri.HasField("resource"))

    def test_parse_protocol_uri_with_remote_cloud_service_with_version(self):
        uri = "//cloud.uprotocol.example.com/body.access/1"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("cloud.uprotocol.example.com", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertFalse(uuri.HasField("resource"))

    def test_parse_protocol_uri_with_remote_service_no_version_with_resource_name_only(
        self,
    ):
        uri = "//VCU.MY_CAR_VIN/body.access//door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertTrue(len(uuri.resource.instance) == 0)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_remote_cloud_service_no_version_with_resource_name_only(
        self,
    ):
        uri = "//cloud.uprotocol.example.com/body.access//door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("cloud.uprotocol.example.com", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertTrue(len(uuri.resource.instance) == 0)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_remote_service_with_version_with_resource_name_only(
        self,
    ):
        uri = "//VCU.MY_CAR_VIN/body.access/1/door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertTrue(len(uuri.resource.instance) == 0)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_remote_service_cloud_with_version_with_resource_name_only(
        self,
    ):
        uri = "//cloud.uprotocol.example.com/body.access/1/door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("cloud.uprotocol.example.com", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertTrue(len(uuri.resource.instance) == 0)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_remote_service_no_version_with_resource_and_instance_no_getMessage(
        self,
    ):
        uri = "//VCU.MY_CAR_VIN/body.access//door.front_left"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_remote_service_with_version_with_resource_and_instance_no_getMessage(
        self,
    ):
        uri = "//VCU.MY_CAR_VIN/body.access/1/door.front_left"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_remote_service_no_version_with_resource_and_instance_and_getMessage(
        self,
    ):
        uri = "//VCU.MY_CAR_VIN/body.access//door.front_left#Door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertFalse(len(uuri.resource.message) == 0)
        self.assertEqual("Door", uuri.resource.message)

    def test_parse_protocol_uri_with_remote_cloud_service_no_version_with_resource_and_instance_and_getMessage(
        self,
    ):
        uri = "//cloud.uprotocol.example.com/body.access//door.front_left#Door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("cloud.uprotocol.example.com", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertFalse(len(uuri.resource.message) == 0)
        self.assertEqual("Door", uuri.resource.message)

    def test_parse_protocol_uri_with_remote_service_with_version_with_resource_and_instance_and_getMessage(
        self,
    ):
        uri = "//VCU.MY_CAR_VIN/body.access/1/door.front_left#Door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertFalse(len(uuri.resource.message) == 0)
        self.assertEqual("Door", uuri.resource.message)

    def test_parse_protocol_uri_with_remote_cloud_service_with_version_with_resource_and_instance_and_getMessage(
        self,
    ):
        uri = (
            "//cloud.uprotocol.example.com/body.access/1/door.front_left#Door"
        )
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("cloud.uprotocol.example.com", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertFalse(len(uuri.resource.message) == 0)
        self.assertEqual("Door", uuri.resource.message)

    def test_parse_protocol_uri_with_remote_service_with_version_with_resource_with_message_device_no_domain(
        self,
    ):
        uri = "//VCU/body.access/1/door.front_left"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_rpc_uri_with_remote_service_no_version(self):
        uri = "//bo.cloud/petapp//rpc.response"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("bo.cloud", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("petapp", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("rpc", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("response", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_rpc_uri_with_remote_service_with_version(self):
        uri = "//bo.cloud/petapp/1/rpc.response"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("bo.cloud", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("petapp", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("rpc", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("response", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_build_protocol_uri_from__uri_when__uri_isnull(self):
        uprotocol_uri = LongUriSerializer().serialize(None)
        self.assertEqual("", uprotocol_uri)

    def test_build_protocol_uri_from__uri_when__uri_isEmpty(self):
        uuri = UUri()
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual("", uprotocol_uri)

    def test_build_protocol_uri_from__uri_when__uri_has_empty_use(self):
        uuri = UUri(resource=UResource(name="door"))
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual("///door", uprotocol_uri)

    def test_build_protocol_uri_from__uri_when__uri_has_local_authority_service_no_version(
        self,
    ):
        uuri = UUri(entity=UEntity(name="body.access"))
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual("/body.access", uprotocol_uri)

    def test_build_protocol_uri_from__uri_when__uri_has_local_authority_service_and_version(
        self,
    ):
        use = UEntity(name="body.access", version_major=1)
        uuri = UUri(entity=use, resource=UResource())
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual("/body.access/1", uprotocol_uri)

    def test_build_protocol_uri_from__uri_when__uri_has_local_authority_service_no_version_with_resource(
        self,
    ):
        use = UEntity(name="body.access")
        uuri = UUri(entity=use, resource=UResource(name="door"))
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual("/body.access//door", uprotocol_uri)

    def test_build_protocol_uri_from__uri_when__uri_has_local_authority_service_and_version_with_resource(
        self,
    ):
        use = UEntity(name="body.access", version_major=1)
        uuri = UUri(entity=use, resource=UResource(name="door"))
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual("/body.access/1/door", uprotocol_uri)

    def test_build_protocol_uri_from_uri_when_uri_has_l_authority_service_n_vsn_with_rsrc_with_instance_n_getMessage(
        self,
    ):
        use = UEntity(name="body.access")
        uuri = UUri(
            entity=use, resource=UResource(name="door", instance="front_left")
        )
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual("/body.access//door.front_left", uprotocol_uri)

    def test_build_protocol_uri_from_uri_when_uri_has_l_authority_service_and_vsn_with_rsrc_with_instance_n_getMessage(
        self,
    ):
        use = UEntity(name="body.access", version_major=1)
        uuri = UUri(
            entity=use, resource=UResource(name="door", instance="front_left")
        )
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual("/body.access/1/door.front_left", uprotocol_uri)

    def test_build_protocol_uri_from_uri_when_uri_has_l_authority_svc_no_vsn_with_rsrc_with_instance_with_getMessage(
        self,
    ):
        use = UEntity(name="body.access")
        uuri = UUri(
            entity=use,
            resource=UResource(
                name="door", instance="front_left", message="Door"
            ),
        )
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual("/body.access//door.front_left#Door", uprotocol_uri)

    def test_build_protocol_uri_from_uri_when_uri_has_l_authority_svc_and_vsn_with_rsrc_with_instance_with_getMessage(
        self,
    ):
        use = UEntity(name="body.access", version_major=1)
        uuri = UUri(
            entity=use,
            resource=UResource(
                name="door", instance="front_left", message="Door"
            ),
        )
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual("/body.access/1/door.front_left#Door", uprotocol_uri)

    def test_build_protocol_uri_from_uri_when_uri_has_remote_authority_service_no_version(
        self,
    ):
        use = UEntity(name="body.access")
        uuri = UUri(authority=UAuthority(name="vcu.my_car_vin"), entity=use)
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual("//vcu.my_car_vin/body.access", uprotocol_uri)

    def test_build_protocol_uri_from_uri_when_uri_has_remote_authority_service_and_version(
        self,
    ):
        use = UEntity(name="body.access", version_major=1)
        uuri = UUri(authority=UAuthority(name="vcu.my_car_vin"), entity=use)
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual("//vcu.my_car_vin/body.access/1", uprotocol_uri)

    def test_build_protocol_uri_from_uri_when_uri_has_remote_cloud_authority_service_and_version(
        self,
    ):
        use = UEntity(name="body.access", version_major=1)
        uuri = UUri(
            authority=UAuthority(name="cloud.uprotocol.example.com"),
            entity=use,
        )
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual(
            "//cloud.uprotocol.example.com/body.access/1", uprotocol_uri
        )

    def test_build_protocol_uri_from_uri_when_uri_has_remote_authority_service_and_version_with_resource(
        self,
    ):
        use = UEntity(name="body.access", version_major=1)
        uuri = UUri(
            authority=UAuthority(name="vcu.my_car_vin"),
            entity=use,
            resource=UResource(name="door"),
        )
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual("//vcu.my_car_vin/body.access/1/door", uprotocol_uri)

    def test_build_protocol_uri_from_uri_when_uri_has_remote_authority_service_no_version_with_resource(
        self,
    ):
        use = UEntity(name="body.access")
        uuri = UUri(
            authority=UAuthority(name="vcu.my_car_vin"),
            entity=use,
            resource=UResource(name="door"),
        )
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual("//vcu.my_car_vin/body.access//door", uprotocol_uri)

    def test_build_protocol_uri_from_uri_when_uri_has_r_authority_svc_and_vsn_with_rsrc_with_instance_no_getMessage(
        self,
    ):
        use = UEntity(name="body.access", version_major=1)
        uuri = UUri(
            authority=UAuthority(name="vcu.my_car_vin"),
            entity=use,
            resource=UResource(name="door", instance="front_left"),
        )
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual(
            "//vcu.my_car_vin/body.access/1/door.front_left", uprotocol_uri
        )

    def test_build_protocol_uri_from_uri_when_uri_has_r_cld_authority_svc_and_vsn_with_rsrc_with_instance_n_getMessage(
        self,
    ):
        use = UEntity(name="body.access", version_major=1)
        uuri = UUri(
            authority=UAuthority(name="cloud.uprotocol.example.com"),
            entity=use,
            resource=UResource(name="door", instance="front_left"),
        )
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual(
            "//cloud.uprotocol.example.com/body.access/1/door.front_left",
            uprotocol_uri,
        )

    def test_build_protocol_uri_from_uri_when_uri_has_r_authority_svc_no_vsn_with_resource_with_instance_n_getMessage(
        self,
    ):
        use = UEntity(name="body.access")
        uuri = UUri(
            authority=UAuthority(name="vcu.my_car_vin"),
            entity=use,
            resource=UResource(name="door", instance="front_left"),
        )
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual(
            "//vcu.my_car_vin/body.access//door.front_left", uprotocol_uri
        )

    def test_build_protocol_uri_from_uri_when_uri_has_r_authority_svc_and_version_with_rsrc_with_i_and_getMessage(
        self,
    ):
        use = UEntity(name="body.access", version_major=1)
        uuri = UUri(
            authority=UAuthority(name="vcu.my_car_vin"),
            entity=use,
            resource=UResource(
                name="door", instance="front_left", message="Door"
            ),
        )
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual(
            "//vcu.my_car_vin/body.access/1/door.front_left#Door",
            uprotocol_uri,
        )

    def test_build_protocol_uri_from_uri_when_uri_has_r_authority_svc_no_version_with_rsrc_with_i_and_getMessage(
        self,
    ):
        use = UEntity(name="body.access")
        uuri = UUri(
            authority=UAuthority(name="vcu.my_car_vin"),
            entity=use,
            resource=UResource(
                name="door", instance="front_left", message="Door"
            ),
        )
        uprotocol_uri = LongUriSerializer().serialize(uuri)
        self.assertEqual(
            "//vcu.my_car_vin/body.access//door.front_left#Door", uprotocol_uri
        )

    def test_build_protocol_uri_for_source_part_of_rpc_request_where_source_is_local(
        self,
    ):
        use = UEntity(name="petapp", version_major=1)
        resource = UResource(name="rpc", instance="response")
        uprotocol_uri = LongUriSerializer().serialize(
            UUri(entity=use, resource=resource)
        )
        self.assertEqual("/petapp/1/rpc.response", uprotocol_uri)

    def test_build_protocol_uri_for_source_part_of_rpc_request_where_source_is_remote(
        self,
    ):
        uAuthority = UAuthority(name="cloud.uprotocol.example.com")
        use = UEntity(name="petapp")
        resource = UResource(name="rpc", instance="response")

        uprotocol_uri = LongUriSerializer().serialize(
            UUri(authority=uAuthority, entity=use, resource=resource)
        )
        self.assertEqual(
            "//cloud.uprotocol.example.com/petapp//rpc.response", uprotocol_uri
        )

    def test_build_protocol_uri_from_uri_parts_when_uri_has_remote_authority_service_and_version_with_resource(
        self,
    ):
        u_authority = UAuthority(name="vcu.my_car_vin")
        use = UEntity(name="body.access", version_major=1)
        resource = UResource(name="door")
        uprotocol_uri = LongUriSerializer().serialize(
            UUri(authority=u_authority, entity=use, resource=resource)
        )
        self.assertEqual("//vcu.my_car_vin/body.access/1/door", uprotocol_uri)

    def test_custom_scheme_no_scheme(self):
        u_authority = UAuthority(name="vcu.my_car_vin")
        use = UEntity(name="body.access", version_major=1)
        resource = UResource(name="door")
        ucustom_uri = LongUriSerializer().serialize(
            UUri(authority=u_authority, entity=use, resource=resource)
        )
        self.assertEqual("//vcu.my_car_vin/body.access/1/door", ucustom_uri)

    def test_parse_local_protocol_uri_with_custom_scheme(self):
        uri = "custom:/body.access//door.front_left#Door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance.strip()) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertFalse(len(uuri.resource.message.strip()) == 0)
        self.assertEqual("Door", uuri.resource.message)

    def test_parse_remote_protocol_uri_with_custom_scheme(self):
        uri = "custom://vcu.vin/body.access//door.front_left#Door"
        uri2 = "//vcu.vin/body.access//door.front_left#Door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertEqual("vcu.vin", uuri.authority.name)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertEqual("Door", uuri.resource.message)
        self.assertEqual(uri2, LongUriSerializer().serialize(uuri))

    def test_b_prtcl_uri__uri__uri_rmte_auth_srvc_vsn_rsrc_emp_instc(self):
        u_authority = UAuthority(name="vcu.my_car_vin")
        use = UEntity(name="body.access", version_major=1)
        resource = UResource(name="door", instance="", message="Door")
        ucustom_uri = LongUriSerializer().serialize(
            UUri(authority=u_authority, entity=use, resource=resource)
        )
        self.assertEqual(
            "//vcu.my_car_vin/body.access/1/door#Door", ucustom_uri
        )

    def test_b_prtcl_uri__uri__uri_rmte_auth_srvc_vsn_rsrc_emp_msg(self):
        u_authority = UAuthority(name="vcu.my_car_vin")
        use = UEntity(name="body.access", version_major=1)
        resource = UResource(name="door", instance="front_left", message="")
        ucustom_uri = LongUriSerializer().serialize(
            UUri(authority=u_authority, entity=use, resource=resource)
        )
        self.assertEqual(
            "//vcu.my_car_vin/body.access/1/door.front_left", ucustom_uri
        )

    def test_b_prtcl_uri__uri__uri_empty_auth_service_ver_w_rsrc(self):
        u_authority = UAuthority(name="")
        use = UEntity(name="body.access", version_major=1)
        resource = UResource(
            name="door", instance="front_left", message="Door"
        )
        ucustom_uri = LongUriSerializer().serialize(
            UUri(authority=u_authority, entity=use, resource=resource)
        )
        self.assertEqual("/body.access/1/door.front_left#Door", ucustom_uri)


if __name__ == "__main__":
    unittest.main()
