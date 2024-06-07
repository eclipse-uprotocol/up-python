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
import json
import os
from google.protobuf import any_pb2
from uprotocol.cloudevent.datamodel.ucloudeventattributes import (
    UCloudEventAttributesBuilder,
    UCloudEventAttributes,
)
from uprotocol.cloudevent.factory.cloudeventfactory import CloudEventFactory
from uprotocol.cloudevent.factory.ucloudevent import UCloudEvent
from uprotocol.cloudevent.serialize.base64protobufserializer import (
    Base64ProtobufSerializer,
)
from uprotocol.cloudevent.serialize.cloudeventtojsonserializer import (
    CloudEventToJsonSerializer,
)
from uprotocol.cloudevent.cloudevents_pb2 import CloudEvent
from uprotocol.proto.uprotocol.v1.uattributes_pb2 import UMessageType, UPriority
from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri
from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UCode

from uprotocol.uri.serializer.uriserializer import UriSerializer


def get_json_object():
    current_directory = os.getcwd()
    json_file_path = os.path.join(
        current_directory,
        "tests",
        "test_cloudevent",
        "test_factory",
        "cloudevent.json",
    )

    with open(json_file_path, "r") as json_file:
        json_data = json.load(json_file)

    return json_data


def build_uri_for_test():
    uri = UUri(ue_id=12345, resource_id=531)
    return UriSerializer().serialize(uri)


def build_proto_payload_for_test():
    ce_proto = CloudEvent(
        spec_version="1.0",
        source="https://example.com",
        id="hello",
        type="example.demo",
        proto_data=any_pb2.Any(),
    )

    any_obj = any_pb2.Any()
    any_obj.Pack(ce_proto)
    return any_obj


class TestCloudEventFactory(unittest.TestCase):
    DATA_CONTENT_TYPE = CloudEventFactory.PROTOBUF_CONTENT_TYPE

    def test_all_cloud_events_from_json(self):
        cloudevents = get_json_object()
        for ce_json in cloudevents:
            bytes_ce = Base64ProtobufSerializer().serialize(
                ce_json["serialized_ce"]
            )
            cloudevent = CloudEventToJsonSerializer().deserialize(bytes_ce)
            self.assertEqual(UCloudEvent.get_id(cloudevent), ce_json["id"])
            self.assertEqual(
                UCloudEvent.get_specversion(cloudevent), ce_json["specversion"]
            )
            if "source" in ce_json:
                self.assertEqual(
                    UCloudEvent.get_source(cloudevent), ce_json["source"]
                )
            if "sink" in ce_json:
                self.assertEqual(
                    UCloudEvent.get_sink(cloudevent), ce_json["sink"]
                )
            if "type" in ce_json:
                self.assertEqual(
                    UCloudEvent.get_type(cloudevent), ce_json["type"]
                )
            if "priority" in ce_json:
                self.assertEqual(
                    UCloudEvent.get_priority(cloudevent), ce_json["priority"]
                )
            if "ttl" in ce_json:
                self.assertEqual(
                    UCloudEvent.get_ttl(cloudevent), ce_json["ttl"]
                )
            if "hash" in ce_json:
                self.assertEqual(
                    UCloudEvent.get_hash(cloudevent), ce_json["hash"]
                )
            if "token" in ce_json:
                self.assertEqual(
                    UCloudEvent.get_token(cloudevent), ce_json["token"]
                )
            if "dataschema" in ce_json:
                self.assertEqual(
                    UCloudEvent.get_data_schema(cloudevent),
                    ce_json["dataschema"],
                )
            if "datacontenttype" in ce_json:
                self.assertEqual(
                    UCloudEvent.get_data_content_type(cloudevent),
                    ce_json["datacontenttype"],
                )
            if "commstatus" in ce_json:
                self.assertEqual(
                    UCloudEvent.get_communication_status(cloudevent),
                    ce_json["commstatus"],
                )

    def test_create_base_cloud_event(self):
        source = build_uri_for_test()

        # fake payload
        proto_payload = build_proto_payload_for_test()

        # additional attributes
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_hash("somehash")
            .with_priority(UPriority.UPRIORITY_CS1)
            .with_ttl(3)
            .with_token("someOAuthToken")
            .with_traceparent("sometraceparent")
            .build()
        )

        # build the cloud event
        cloud_event = CloudEventFactory.build_base_cloud_event(
            "testme",
            source,
            proto_payload,
            u_cloud_event_attributes,
        )

        cloud_event.__setitem__("type", UCloudEvent.get_event_type(UMessageType.UMESSAGE_TYPE_PUBLISH))

        self.assertEqual("1.0", UCloudEvent.get_specversion(cloud_event))
        self.assertEqual("testme", UCloudEvent.get_id(cloud_event))
        self.assertEqual(source, UCloudEvent.get_source(cloud_event))
        self.assertEqual("pub.v1", UCloudEvent.get_type(cloud_event))
        self.assertNotIn("sink", cloud_event.get_attributes())
        self.assertEqual("somehash", UCloudEvent.get_hash(cloud_event))
        self.assertEqual(
            UPriority.Name(UPriority.UPRIORITY_CS1),
            UCloudEvent.get_priority(cloud_event),
        )
        self.assertEqual(3, UCloudEvent.get_ttl(cloud_event))
        self.assertEqual("someOAuthToken", UCloudEvent.get_token(cloud_event))
        self.assertEqual(
            "sometraceparent", UCloudEvent.get_traceparent(cloud_event)
        )
        self.assertEqual(
            proto_payload.SerializeToString(), cloud_event.get_data()
        )

    def test_create_base_cloud_event_with_datacontenttype_and_schema(self):
        source = build_uri_for_test()

        # fake payload
        proto_payload = build_proto_payload_for_test()

        # additional attributes
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_hash("somehash")
            .with_priority(UPriority.UPRIORITY_CS1)
            .with_ttl(3)
            .with_token("someOAuthToken")
            .build()
        )

        # build the cloud event
        cloud_event = CloudEventFactory.build_base_cloud_event(
            "testme",
            source,
            proto_payload,
            u_cloud_event_attributes,
        )

        cloud_event.__setitem__(
            "datacontenttype", CloudEventFactory.PROTOBUF_CONTENT_TYPE
        )
        cloud_event.__setitem__("dataschema", proto_payload.type_url)
        cloud_event.__setitem__("type", UCloudEvent.get_event_type(UMessageType.UMESSAGE_TYPE_PUBLISH))

        # test all attributes
        self.assertEqual("1.0", UCloudEvent.get_specversion(cloud_event))
        self.assertEqual("testme", UCloudEvent.get_id(cloud_event))
        self.assertEqual(source, UCloudEvent.get_source(cloud_event))
        self.assertEqual(
            UCloudEvent.get_event_type(UMessageType.UMESSAGE_TYPE_PUBLISH),
            UCloudEvent.get_type(cloud_event),
        )
        self.assertEqual(
            self.DATA_CONTENT_TYPE,
            UCloudEvent.get_data_content_type(cloud_event),
        )
        self.assertEqual(
            proto_payload.type_url, UCloudEvent.get_data_schema(cloud_event)
        )
        self.assertNotIn("sink", cloud_event.get_attributes())
        self.assertEqual("somehash", UCloudEvent.get_hash(cloud_event))
        self.assertEqual(
            UPriority.Name(UPriority.UPRIORITY_CS1),
            UCloudEvent.get_priority(cloud_event),
        )
        self.assertEqual(3, UCloudEvent.get_ttl(cloud_event))
        self.assertEqual("someOAuthToken", UCloudEvent.get_token(cloud_event))
        self.assertEqual(
            proto_payload.SerializeToString(), cloud_event.get_data()
        )

    def test_create_base_cloud_event_without_attributes(self):
        source = build_uri_for_test()

        # fake payload
        proto_payload = build_proto_payload_for_test()

        # no additional attributes
        u_cloud_event_attributes = UCloudEventAttributes.empty()

        # build the cloud event
        # build the cloud event
        cloud_event = CloudEventFactory.build_base_cloud_event(
            "testme",
            source,
            proto_payload,
            u_cloud_event_attributes,
        )

        cloud_event.__setitem__("type", UCloudEvent.get_event_type(UMessageType.UMESSAGE_TYPE_PUBLISH))

        # test all attributes
        self.assertEqual("1.0", UCloudEvent.get_specversion(cloud_event))
        self.assertEqual("testme", UCloudEvent.get_id(cloud_event))
        self.assertEqual(source, UCloudEvent.get_source(cloud_event))
        self.assertEqual(
            UCloudEvent.get_event_type(UMessageType.UMESSAGE_TYPE_PUBLISH),
            UCloudEvent.get_type(cloud_event),
        )
        self.assertNotIn("sink", cloud_event.get_attributes())
        self.assertNotIn("hash", cloud_event.get_attributes())
        self.assertNotIn("priority", cloud_event.get_attributes())
        self.assertNotIn("ttl", cloud_event.get_attributes())
        self.assertEqual(
            proto_payload.SerializeToString(), cloud_event.get_data()
        )

    def test_create_publish_cloud_event(self):
        # source
        source = build_uri_for_test()

        # fake payload
        proto_payload = build_proto_payload_for_test()

        # additional attributes
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_hash("somehash")
            .with_priority(UPriority.UPRIORITY_CS1)
            .with_ttl(3)
            .build()
        )

        cloud_event = CloudEventFactory.publish(
            source, proto_payload, u_cloud_event_attributes
        )

        # test all attributes
        self.assertEqual("1.0", UCloudEvent.get_specversion(cloud_event))
        self.assertIsNotNone(UCloudEvent.get_id(cloud_event))
        self.assertEqual(source, UCloudEvent.get_source(cloud_event))
        self.assertEqual(
            UCloudEvent.get_event_type(UMessageType.UMESSAGE_TYPE_PUBLISH),
            UCloudEvent.get_type(cloud_event),
        )
        self.assertNotIn("sink", cloud_event.get_attributes())
        self.assertEqual("somehash", UCloudEvent.get_hash(cloud_event))
        self.assertEqual(
            UPriority.Name(UPriority.UPRIORITY_CS1),
            UCloudEvent.get_priority(cloud_event),
        )
        self.assertEqual(3, UCloudEvent.get_ttl(cloud_event))

        self.assertEqual(
            proto_payload.SerializeToString(), cloud_event.get_data()
        )

    def test_create_notification_cloud_event(self):
        # source
        source = build_uri_for_test()

        # sink
        sink = build_uri_for_test()

        # fake payload
        proto_payload = build_proto_payload_for_test()

        # additional attributes

        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_hash("somehash")
            .with_priority(UPriority.UPRIORITY_CS2)
            .with_ttl(3)
            .build()
        )

        # build the cloud event of type publish with destination - a notification
        cloud_event = CloudEventFactory.notification(
            source, sink, proto_payload, u_cloud_event_attributes
        )

        # test all attributes
        self.assertEqual("1.0", UCloudEvent.get_specversion(cloud_event))
        self.assertIsNotNone(UCloudEvent.get_id(cloud_event))
        self.assertEqual(source, UCloudEvent.get_source(cloud_event))

        self.assertIn("sink", cloud_event.get_attributes())
        self.assertEqual(sink, UCloudEvent.get_sink(cloud_event))

        self.assertEqual(
            UCloudEvent.get_event_type(UMessageType.UMESSAGE_TYPE_NOTIFICATION),
            UCloudEvent.get_type(cloud_event),
        )
        self.assertEqual("somehash", UCloudEvent.get_hash(cloud_event))
        self.assertEqual(
            UPriority.Name(UPriority.UPRIORITY_CS2),
            UCloudEvent.get_priority(cloud_event),
        )
        self.assertEqual(3, UCloudEvent.get_ttl(cloud_event))

        self.assertEqual(
            proto_payload.SerializeToString(), cloud_event.get_data()
        )

    def test_create_request_cloud_event_from_local_use(self):
        # UriPart for the application requesting the RPC
        application_uri_for_rpc = build_uri_for_test()

        # service Method UriPart
        service_method_uri = build_uri_for_test()

        # fake payload
        proto_payload = build_proto_payload_for_test()

        # additional attributes

        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_hash("somehash")
            .with_priority(UPriority.UPRIORITY_CS2)
            .with_ttl(3)
            .with_token("someOAuthToken")
            .build()
        )

        cloud_event = CloudEventFactory.request(
            application_uri_for_rpc,
            service_method_uri,
            proto_payload,
            u_cloud_event_attributes,
        )

        # test all attributes
        self.assertEqual("1.0", UCloudEvent.get_specversion(cloud_event))
        self.assertIsNotNone(UCloudEvent.get_id(cloud_event))
        self.assertEqual(
            application_uri_for_rpc, UCloudEvent.get_source(cloud_event)
        )

        self.assertIn("sink", cloud_event.get_attributes())
        self.assertEqual(service_method_uri, UCloudEvent.get_sink(cloud_event))

        self.assertEqual("req.v1", UCloudEvent.get_type(cloud_event))
        self.assertEqual("somehash", UCloudEvent.get_hash(cloud_event))
        self.assertEqual(
            UPriority.Name(UPriority.UPRIORITY_CS2),
            UCloudEvent.get_priority(cloud_event),
        )
        self.assertEqual(3, UCloudEvent.get_ttl(cloud_event))
        self.assertEqual("someOAuthToken", UCloudEvent.get_token(cloud_event))

        self.assertEqual(
            proto_payload.SerializeToString(), cloud_event.get_data()
        )

    def test_create_response_cloud_event_originating_from_local_use(self):
        # UriPart for the application requesting the RPC
        application_uri_for_rpc = build_uri_for_test()

        # service Method UriPart
        service_method_uri = build_uri_for_test()

        # fake payload
        proto_payload = build_proto_payload_for_test()

        # additional attributes

        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_hash("somehash")
            .with_priority(UPriority.UPRIORITY_CS2)
            .with_ttl(3)
            .build()
        )

        cloud_event = CloudEventFactory.response(
            application_uri_for_rpc,
            service_method_uri,
            "requestIdFromRequestCloudEvent",
            proto_payload,
            u_cloud_event_attributes,
        )

        # test all attributes
        self.assertEqual("1.0", UCloudEvent.get_specversion(cloud_event))
        self.assertIsNotNone(UCloudEvent.get_id(cloud_event))
        self.assertEqual(
            service_method_uri, UCloudEvent.get_source(cloud_event)
        )

        self.assertIn("sink", cloud_event.get_attributes())
        self.assertEqual(
            application_uri_for_rpc, UCloudEvent.get_sink(cloud_event)
        )

        self.assertEqual("res.v1", UCloudEvent.get_type(cloud_event))
        self.assertEqual("somehash", UCloudEvent.get_hash(cloud_event))
        self.assertEqual(
            UPriority.Name(UPriority.UPRIORITY_CS2),
            UCloudEvent.get_priority(cloud_event),
        )
        self.assertEqual(3, UCloudEvent.get_ttl(cloud_event))

        self.assertEqual(
            "requestIdFromRequestCloudEvent",
            UCloudEvent.get_request_id(cloud_event),
        )

        # Use assertEqual to compare byte arrays
        self.assertEqual(
            proto_payload.SerializeToString(), cloud_event.get_data()
        )

    def test_create_failed_response_cloud_event_originating_from_local_use(
        self,
    ):
        # UriPart for the application requesting the RPC
        application_uri_for_rpc = build_uri_for_test()

        # service Method UriPart
        service_method_uri = build_uri_for_test()

        # additional attributes

        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_hash("somehash")
            .with_priority(UPriority.UPRIORITY_CS2)
            .with_ttl(3)
            .build()
        )

        cloud_event = CloudEventFactory.failed_response(
            application_uri_for_rpc,
            service_method_uri,
            "requestIdFromRequestCloudEvent",
            UCode.INVALID_ARGUMENT,
            u_cloud_event_attributes,
        )

        # test all attributes
        self.assertEqual("1.0", UCloudEvent.get_specversion(cloud_event))
        self.assertIsNotNone(UCloudEvent.get_id(cloud_event))
        self.assertEqual(
            service_method_uri, UCloudEvent.get_source(cloud_event)
        )

        self.assertIn("sink", cloud_event.get_attributes())
        self.assertEqual(
            application_uri_for_rpc, UCloudEvent.get_sink(cloud_event)
        )

        self.assertEqual("res.v1", UCloudEvent.get_type(cloud_event))
        self.assertEqual("somehash", UCloudEvent.get_hash(cloud_event))
        self.assertEqual(
            UPriority.Name(UPriority.UPRIORITY_CS2),
            UCloudEvent.get_priority(cloud_event),
        )
        self.assertEqual(3, UCloudEvent.get_ttl(cloud_event))
        self.assertEqual(
            UCode.INVALID_ARGUMENT,
            UCloudEvent.get_communication_status(cloud_event),
        )

        self.assertEqual(
            "requestIdFromRequestCloudEvent",
            UCloudEvent.get_request_id(cloud_event),
        )


if __name__ == "__main__":
    unittest.main()
