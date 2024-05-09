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

from google.protobuf import any_pb2

from uprotocol.cloudevent.datamodel.ucloudeventattributes import (
    UCloudEventAttributesBuilder,
)
from uprotocol.cloudevent.factory.cloudeventfactory import CloudEventFactory
from uprotocol.cloudevent.factory.ucloudevent import UCloudEvent
from uprotocol.cloudevent.serialize.cloudeventserializers import (
    CloudEventSerializers,
)
from uprotocol.cloudevent.cloudevents_pb2 import CloudEvent
from uprotocol.proto.uattributes_pb2 import UPriority, UMessageType

protoContentType = CloudEventFactory.PROTOBUF_CONTENT_TYPE
serializer = CloudEventSerializers.JSON.serializer()


def build_proto_payload_for_test():
    ce_proto = CloudEvent(
        spec_version="1.0",
        source="https://example.com",
        id="hello",
        type="example.demo",
        proto_data=any_pb2.Any(),
        attributes={"ttl": CloudEvent.CloudEventAttributeValue(ce_string="3")},
    )

    any_obj = any_pb2.Any()
    any_obj.Pack(ce_proto)
    return any_obj


class TestCloudEventToJsonSerializer(unittest.TestCase):

    def test_serialize_cloud_event_to_json(self):
        proto_payload = build_proto_payload_for_test()
        # additional attributes
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_priority(UPriority.UPRIORITY_CS1)
            .with_ttl(3)
            .build()
        )

        # build the cloud event
        cloud_event = CloudEventFactory.build_base_cloud_event(
            "hello",
            "/body.access/1/door.front_left",
            proto_payload.SerializeToString(),
            proto_payload.type_url,
            u_cloud_event_attributes,
            UCloudEvent.get_event_type(UMessageType.UMESSAGE_TYPE_PUBLISH),
        )
        cloud_event.__setitem__("datacontenttype", protoContentType)
        cloud_event.__setitem__("dataschema", proto_payload.type_url)
        cloud_event.__delitem__("time")
        bytes_data = serializer.serialize(cloud_event)
        json_str = bytes_data.decode("utf-8")
        expected = (
            '{"specversion": "1.0", "id": "hello", "source": "/body.access/1/door.front_left", '
            '"type": "pub.v1", "datacontenttype": "application/x-protobuf", "dataschema": '
            '"type.googleapis.com/io.cloudevents.v1.CloudEvent", "data_base64": '
            '"CjB0eXBlLmdvb2dsZWFwaXMuY29tL2lvLmNsb3VkZXZlbnRzLnYxLkNsb3VkRXZlbnQSPQoFaGVs'
            'bG8SE2h0dHBzOi8vZXhhbXBsZS5jb20aAzEuMCIMZXhhbXBsZS5kZW1vKgoKA3R0bBIDGgEzQgA=", '
            '"ttl": 3, "priority": "UPRIORITY_CS1"}'
        )
        self.assertEqual(expected, json_str)

    def test_serialize_and_deserialize_cloud_event_to_json(self):
        proto_payload = build_proto_payload_for_test()
        # additional attributes
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_priority(UPriority.UPRIORITY_CS1)
            .with_ttl(3)
            .build()
        )

        # build the cloud event
        cloud_event = CloudEventFactory.build_base_cloud_event(
            "hello",
            "/body.access/1/door.front_left",
            proto_payload.SerializeToString(),
            proto_payload.type_url,
            u_cloud_event_attributes,
            UCloudEvent.get_event_type(UMessageType.UMESSAGE_TYPE_PUBLISH),
        )
        cloud_event.__setitem__("datacontenttype", protoContentType)
        cloud_event.__setitem__("dataschema", proto_payload.type_url)
        cloud_event.__delitem__("time")
        serialized_data = serializer.serialize(cloud_event)
        deserialized_data = serializer.deserialize(serialized_data)
        deserialized_data.__delitem__("time")

        self.assertEqual(cloud_event, deserialized_data)

    def test_double_serialization_protobuf_when_creating_cloud_event_with_factory_methods(
        self,
    ):
        proto_payload = build_proto_payload_for_test()
        # additional attributes
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_priority(UPriority.UPRIORITY_CS1)
            .with_ttl(3)
            .build()
        )

        # build the cloud event
        cloud_event1 = CloudEventFactory.build_base_cloud_event(
            "hello",
            "/body.access/1/door.front_left",
            proto_payload.SerializeToString(),
            proto_payload.type_url,
            u_cloud_event_attributes,
            UCloudEvent.get_event_type(UMessageType.UMESSAGE_TYPE_PUBLISH),
        )
        cloud_event1.__setitem__("datacontenttype", protoContentType)
        cloud_event1.__setitem__("dataschema", proto_payload.type_url)
        cloud_event1.__delitem__("time")
        serialized_data1 = serializer.serialize(cloud_event1)
        cloud_event2 = serializer.deserialize(serialized_data1)
        cloud_event2.__delitem__("time")
        self.assertEqual(cloud_event2, cloud_event1)
        serialized_data2 = serializer.serialize(cloud_event2)
        self.assertEqual(serialized_data1, serialized_data2)
        cloud_event3 = serializer.deserialize(serialized_data2)
        cloud_event3.__delitem__("time")

        payload1 = UCloudEvent.unpack(cloud_event3, CloudEvent)
        self.assertEqual(cloud_event2, cloud_event3)
        payload2 = CloudEvent()
        payload2.ParseFromString(proto_payload.value)
        self.assertEqual(payload1, payload2)
        self.assertEqual(cloud_event1, cloud_event3)
