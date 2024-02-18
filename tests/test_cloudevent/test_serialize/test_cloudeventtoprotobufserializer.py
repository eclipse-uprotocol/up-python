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
#
# -------------------------------------------------------------------------

import json
import os
import unittest

from cloudevents.http import CloudEvent as ApacheCloudEvent
from google.protobuf import any_pb2

from uprotocol.cloudevent.datamodel.ucloudeventattributes import UCloudEventAttributesBuilder
from uprotocol.cloudevent.factory.cloudeventfactory import CloudEventFactory
from uprotocol.cloudevent.factory.ucloudevent import UCloudEvent
from uprotocol.cloudevent.serialize.base64protobufserializer import Base64ProtobufSerializer
from uprotocol.cloudevent.serialize.cloudeventserializers import CloudEventSerializers
from uprotocol.cloudevent.serialize.cloudeventtoprotobufserializer import CloudEventToProtobufSerializer
from uprotocol.cloudevent.cloudevents_pb2 import CloudEvent
from uprotocol.proto.uattributes_pb2 import UPriority, UMessageType
from uprotocol.proto.uri_pb2 import UUri, UEntity, UResource
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer

serializer = CloudEventSerializers.PROTOBUF.serializer()


def build_uuri_for_test():
    uri = UUri(entity=UEntity(name="body.access"),
               resource=UResource(name="door", instance="front_left", message="Door"))
    return LongUriSerializer().serialize(uri)


def build_proto_payload_for_test():
    ce_proto = CloudEvent(spec_version="1.0", source="https://example.com", id="hello", type="example.demo",
                          proto_data=any_pb2.Any(),
                          attributes={"ttl": CloudEvent.CloudEventAttributeValue(ce_string="3")})

    any_obj = any_pb2.Any()
    any_obj.Pack(ce_proto)
    return any_obj


def get_json_object():
    current_directory = os.getcwd()
    json_file_path = os.path.join(current_directory, "tests","test_cloudevent",
    "test_serialize","cloudevent_to_protobuf.json")
    with open(json_file_path, 'r') as json_file:
        json_data = json.load(json_file)

    return json_data


class TestCloudEventToProtobufSerializer(unittest.TestCase):

    def test_all_cloud_events_from_json(self):
        cloudevents = get_json_object()
        for ce_json in cloudevents:
            bytes_ce = Base64ProtobufSerializer().serialize(ce_json['serialized_ce'])
            cloudevent = CloudEventToProtobufSerializer().deserialize(bytes_ce)
            self.assertEqual(UCloudEvent.get_id(cloudevent), ce_json['id'])
            self.assertEqual(UCloudEvent.get_specversion(cloudevent), ce_json['specversion'])
            if 'source' in ce_json:
                self.assertEqual(UCloudEvent.get_source(cloudevent), ce_json['source'])
            if 'sink' in ce_json:
                self.assertEqual(UCloudEvent.get_sink(cloudevent), ce_json['sink'])
            if 'type' in ce_json:
                self.assertEqual(UCloudEvent.get_type(cloudevent), ce_json['type'])
            if 'priority' in ce_json:
                self.assertEqual(UCloudEvent.get_priority(cloudevent), ce_json['priority'])
            if 'ttl' in ce_json:
                self.assertEqual(UCloudEvent.get_ttl(cloudevent), ce_json['ttl'])
            if 'hash' in ce_json:
                self.assertEqual(UCloudEvent.get_hash(cloudevent), ce_json['hash'])
            if 'token' in ce_json:
                self.assertEqual(UCloudEvent.get_token(cloudevent), ce_json['token'])
            if 'dataschema' in ce_json:
                self.assertEqual(UCloudEvent.get_data_schema(cloudevent), ce_json['dataschema'])
            if 'datacontenttype' in ce_json:
                self.assertEqual(UCloudEvent.get_data_content_type(cloudevent), ce_json['datacontenttype'])
            if 'commstatus' in ce_json:
                self.assertEqual(UCloudEvent.get_communication_status(cloudevent), ce_json['commstatus'])

    def test_serialize_and_deserialize_cloud_event_to_protobuf(self):
        source = build_uuri_for_test()
        proto_payload = build_proto_payload_for_test()
        # additional attributes
        u_cloud_event_attributes = UCloudEventAttributesBuilder().with_hash("somehash").with_priority(
            UPriority.UPRIORITY_CS0).with_ttl(3).build()

        # build the cloud event
        cloud_event = CloudEventFactory.build_base_cloud_event("hello", "/body.access/1/door.front_left",
                                                               proto_payload.SerializeToString(),
                                                               proto_payload.type_url, u_cloud_event_attributes,
                                                               UCloudEvent.get_event_type(
                                                                   UMessageType.UMESSAGE_TYPE_PUBLISH))

        cloud_event.__delitem__("time")
        serialized_data = serializer.serialize(cloud_event)

        deserialized_data = serializer.deserialize(serialized_data)
        deserialized_data.__delitem__("time")
        self.assertEqual(cloud_event, deserialized_data)

    def test_serialize_two_different_cloud_event_are_not_the_same(self):
        proto_payload = build_proto_payload_for_test()
        json_attributes1 = {"id": "hello", "source": "/body.access/1/door.front_left", "type": "pub.v1"}
        cloud_event1 = ApacheCloudEvent(json_attributes1, proto_payload.SerializeToString())
        cloud_event1.__setitem__('datacontenttype', 'application/protobuf')
        cloud_event1.__setitem__('dataschema', proto_payload.type_url)
        cloud_event1.__delitem__("time")

        json_attributes2 = {"source": "/body.access/1/door.front_left", "type": "file.v1"}
        cloud_event2 = ApacheCloudEvent(json_attributes2, proto_payload.SerializeToString())
        cloud_event2.__delitem__("time")
        serialized1 = serializer.serialize(cloud_event1)
        serialized2 = serializer.serialize(cloud_event2)
        self.assertNotEqual(serialized1, serialized2)

    def test_double_serialization_protobuf_when_creating_cloud_event_with_factory_methods(self):
        proto_payload = build_proto_payload_for_test()
        source = build_uuri_for_test()
        # additional attributes
        u_cloud_event_attributes = UCloudEventAttributesBuilder().with_hash("somehash").with_priority(
            UPriority.UPRIORITY_CS1).with_ttl(3).with_token("someOAuthToken").build()

        # build the cloud event
        cloud_event = CloudEventFactory.build_base_cloud_event("testme", source, proto_payload.SerializeToString(),
                                                               proto_payload.type_url, u_cloud_event_attributes,
                                                               UCloudEvent.get_event_type(
                                                                   UMessageType.UMESSAGE_TYPE_PUBLISH))
        cloud_event.__delitem__("time")

        serialized_data = serializer.serialize(cloud_event)
        deserialized_data = serializer.deserialize(serialized_data)
        deserialized_data.__delitem__("time")
        self.assertEqual(cloud_event, deserialized_data)

