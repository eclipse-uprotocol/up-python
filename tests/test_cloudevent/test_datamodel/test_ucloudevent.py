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

import time
import unittest
from datetime import datetime, timezone

from google.protobuf import any_pb2

from uprotocol.cloudevent.cloudevents_pb2 import CloudEvent
from uprotocol.cloudevent.datamodel.ucloudeventattributes import (
    UCloudEventAttributesBuilder,
)
from uprotocol.cloudevent.factory.cloudeventfactory import CloudEventFactory
from uprotocol.cloudevent.factory.ucloudevent import UCloudEvent
from uprotocol.proto.uattributes_pb2 import UMessageType, UPriority
from uprotocol.proto.upayload_pb2 import UPayloadFormat
from uprotocol.proto.uri_pb2 import UEntity, UResource, UUri
from uprotocol.proto.ustatus_pb2 import UCode
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.uuid.serializer.longuuidserializer import LongUuidSerializer


def build_uri_for_test():
    uri = UUri(
        entity=UEntity(name="body.access"),
        resource=UResource(name="door", instance="front_left", message="Door"),
    )
    return LongUriSerializer().serialize(uri)


def build_proto_payload_for_test():
    ce_proto = CloudEvent(
        spec_version="1.0",
        source="//VCU.MY_CAR_VIN/body.access//door.front_left#Door",
        id="hello",
        type="example.demo",
        proto_data=any_pb2.Any(),
    )

    any_obj = any_pb2.Any()
    any_obj.Pack(ce_proto)
    return any_obj


def build_cloud_event_for_test():
    source = build_uri_for_test()
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
        proto_payload.SerializeToString(),
        proto_payload.type_url,
        u_cloud_event_attributes,
        UCloudEvent.get_event_type(UMessageType.UMESSAGE_TYPE_PUBLISH),
    )
    return cloud_event


def build_cloud_event_for_test_with_id(id):
    source = build_uri_for_test()
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
        id,
        source,
        proto_payload.SerializeToString(),
        proto_payload.type_url,
        u_cloud_event_attributes,
        UCloudEvent.get_event_type(UMessageType.UMESSAGE_TYPE_PUBLISH),
    )
    return cloud_event


class TestUCloudEvent(unittest.TestCase):
    DATA_CONTENT_TYPE = "application/x-protobuf"

    def test_extract_source_from_cloudevent(self):
        cloud_event = build_cloud_event_for_test()
        source = UCloudEvent.get_source(cloud_event)
        self.assertEqual("/body.access//door.front_left#Door", source)

    def test_extract_sink_from_cloudevent_when_sink_exists(self):
        sink = "//bo.cloud/petapp/1/rpc.response"
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("sink", sink)
        cloud_event.__setitem__("plevel", 4)
        self.assertEqual(sink, UCloudEvent.get_sink(cloud_event))

    def test_extract_sink_from_cloudevent_when_sink_does_not_exist(self):
        cloud_event = build_cloud_event_for_test()
        self.assertEqual(None, UCloudEvent.get_sink(cloud_event))

    def test_extract_request_id_from_cloudevent_when_request_id_exists(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("reqid", "somereqid")
        self.assertEqual("somereqid", UCloudEvent.get_request_id(cloud_event))

    def test_extract_request_id_from_cloudevent_when_request_id_does_not_exist(
        self,
    ):
        cloud_event = build_cloud_event_for_test()
        self.assertEqual(None, UCloudEvent.get_request_id(cloud_event))

    def test_extract_request_id_from_cloudevent_when_request_id_value_is_null(
        self,
    ):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("reqid", None)
        self.assertEqual(None, UCloudEvent.get_request_id(cloud_event))

    def test_extract_hash_from_cloudevent_when_hash_exists(self):
        cloud_event = build_cloud_event_for_test()
        self.assertEqual("somehash", UCloudEvent.get_hash(cloud_event))

    def test_extract_hash_from_cloudevent_when_hash_does_not_exist(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__delitem__("hash")
        self.assertEqual(None, UCloudEvent.get_hash(cloud_event))

    def test_extract_priority_from_cloudevent_when_priority_exists(self):
        cloud_event = build_cloud_event_for_test()
        self.assertEqual(
            UPriority.Name(UPriority.UPRIORITY_CS1),
            UCloudEvent.get_priority(cloud_event),
        )

    def test_extract_priority_from_cloudevent_when_priority_does_not_exist(
        self,
    ):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__delitem__("priority")
        self.assertEqual(None, UCloudEvent.get_priority(cloud_event))

    def test_extract_ttl_from_cloudevent_when_ttl_exists(self):
        cloud_event = build_cloud_event_for_test()
        self.assertEqual(UCode.INVALID_ARGUMENT, UCloudEvent.get_ttl(cloud_event))

    def test_extract_ttl_from_cloudevent_when_ttl_does_not_exists(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__delitem__("ttl")
        self.assertEqual(None, UCloudEvent.get_ttl(cloud_event))

    def test_extract_token_from_cloudevent_when_token_exists(self):
        cloud_event = build_cloud_event_for_test()
        self.assertEqual("someOAuthToken", UCloudEvent.get_token(cloud_event))

    def test_extract_token_from_cloudevent_when_token_does_not_exists(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__delitem__("token")
        self.assertEqual(None, UCloudEvent.get_token(cloud_event))

    def test_cloudevent_has_platform_error_when_platform_error_exists(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("commstatus", UCode.ABORTED)
        self.assertEqual(UCode.ABORTED, UCloudEvent.get_communication_status(cloud_event))

    def test_cloudevent_has_platform_error_when_platform_error_does_not_exist(
        self,
    ):
        cloud_event = build_cloud_event_for_test()
        self.assertEqual(UCode.OK, UCloudEvent.get_communication_status(cloud_event))

    def test_extract_platform_error_from_cloudevent_when_platform_error_exists_in_wrong_format(
        self,
    ):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("commstatus", "boom")
        self.assertEqual(UCode.OK, UCloudEvent.get_communication_status(cloud_event))

    def test_extract_platform_error_from_cloudevent_when_platform_error_exists(
        self,
    ):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("commstatus", UCode.INVALID_ARGUMENT)
        self.assertEqual(
            UCode.INVALID_ARGUMENT,
            UCloudEvent.get_communication_status(cloud_event),
        )

    def test_extract_platform_error_from_cloudevent_when_platform_error_does_not_exist(
        self,
    ):
        cloud_event = build_cloud_event_for_test()
        self.assertEqual(UCode.OK, UCloudEvent.get_communication_status(cloud_event))

    def test_adding_platform_error_to_existing_cloudevent(
        self,
    ):
        cloud_event = build_cloud_event_for_test()
        self.assertEqual(UCode.OK, UCloudEvent.get_communication_status(cloud_event))

        cloud_event_1 = UCloudEvent.add_communication_status(cloud_event, UCode.DEADLINE_EXCEEDED)

        self.assertEqual(UCode.OK, UCloudEvent.get_communication_status(cloud_event))

        self.assertEqual(
            UCode.DEADLINE_EXCEEDED,
            UCloudEvent.get_communication_status(cloud_event_1),
        )

    def test_adding_empty_platform_error_to_existing_cloudevent(
        self,
    ):
        cloud_event = build_cloud_event_for_test()
        self.assertEqual(UCode.OK, UCloudEvent.get_communication_status(cloud_event))

        cloud_event_1 = UCloudEvent.add_communication_status(cloud_event, None)

        self.assertEqual(UCode.OK, UCloudEvent.get_communication_status(cloud_event))

        self.assertEqual(cloud_event, cloud_event_1)

    def test_extract_creation_timestamp_from_cloudevent_uuid_id_when_not_a_uuid_v8_id(
        self,
    ):
        cloud_event = build_cloud_event_for_test()
        self.assertEqual(None, UCloudEvent.get_creation_timestamp(cloud_event))

    def test_extract_creation_timestamp_from_cloudevent_uuid_v8_id_when_uuid_v8_id_is_valid(
        self,
    ):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_cloud_event_for_test_with_id(str_uuid)
        maybe_creation_timestamp = UCloudEvent.get_creation_timestamp(cloud_event)
        self.assertIsNotNone(maybe_creation_timestamp)
        creation_timestamp = maybe_creation_timestamp / 1000

        now_timestamp = datetime.now(timezone.utc).timestamp()
        self.assertAlmostEqual(creation_timestamp, now_timestamp, delta=1)

    def test_cloudevent_is_not_expired_cd_when_no_ttl_configured(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__delitem__("ttl")
        self.assertFalse(UCloudEvent.is_expired_by_cloud_event_creation_date(cloud_event))

    def test_cloudevent_is_not_expired_cd_when_ttl_is_zero(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("ttl", 0)
        self.assertFalse(UCloudEvent.is_expired_by_cloud_event_creation_date(cloud_event))

    def test_cloudevent_is_not_expired_cd_when_ttl_is_minus_one(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("ttl", -1)
        self.assertFalse(UCloudEvent.is_expired_by_cloud_event_creation_date(cloud_event))

    def test_cloudevent_is_expired_cd_when_ttl_is_one(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("ttl", 1)
        time.sleep(0.002)
        self.assertTrue(UCloudEvent.is_expired_by_cloud_event_creation_date(cloud_event))

    def test_cloudevent_is_expired_when_ttl_1_mili(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("ttl", 1)
        cloud_event.__setitem__("id", str_uuid)
        time.sleep(8)
        self.assertTrue(UCloudEvent.is_expired(cloud_event))

    def test_cloudevent_is_expired_for_invalid_uuid(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("ttl", 50000)
        cloud_event.__setitem__("id", "")
        self.assertFalse(UCloudEvent.is_expired(cloud_event))

    def test_cloudevent_has_a_uuid_v8_id(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        self.assertTrue(UCloudEvent.is_cloud_event_id(cloud_event))

    def test_to_message_with_valid_event(self):
        # additional attributes
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder().with_priority(UPriority.UPRIORITY_CS2).with_ttl(3).build()
        )
        cloud_event = CloudEventFactory.publish(
            build_uri_for_test(),
            build_proto_payload_for_test(),
            u_cloud_event_attributes,
        )
        u_message = UCloudEvent.to_message(cloud_event)
        self.assertIsNotNone(u_message)

    def test_from_message_with_valid_message(self):
        # additional attributes
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_priority(UPriority.UPRIORITY_CS2)
            .with_ttl(3)
            .with_traceparent("someParent")
            .build()
        )
        cloud_event = CloudEventFactory.publish(
            build_uri_for_test(),
            build_proto_payload_for_test(),
            u_cloud_event_attributes,
        )
        u_message = UCloudEvent.to_message(cloud_event)
        self.assertIsNotNone(u_message)
        cloud_event1 = UCloudEvent.from_message(u_message)
        self.assertIsNotNone(cloud_event1)
        cloud_event.__delitem__("time")
        cloud_event1.__delitem__("time")
        self.assertEqual(cloud_event, cloud_event1)
        self.assertEqual(cloud_event.get_data(), cloud_event1.get_data())
        self.assertEqual(
            UCloudEvent.get_source(cloud_event),
            UCloudEvent.get_source(cloud_event1),
        )
        self.assertEqual(
            UCloudEvent.get_specversion(cloud_event),
            UCloudEvent.get_specversion(cloud_event1),
        )
        self.assertEqual(
            UCloudEvent.get_priority(cloud_event),
            UCloudEvent.get_priority(cloud_event1),
        )
        self.assertEqual(UCloudEvent.get_id(cloud_event), UCloudEvent.get_id(cloud_event1))
        self.assertEqual(
            UCloudEvent.get_type(cloud_event),
            UCloudEvent.get_type(cloud_event1),
        )

    def test_to_from_message_from_request_cloudevent(self):
        # additional attributes
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_priority(UPriority.UPRIORITY_CS2)
            .with_ttl(3)
            .with_token("someOAuthToken")
            .build()
        )

        cloud_event = CloudEventFactory.request(
            build_uri_for_test(),
            "//bo.cloud/petapp/1/rpc.response",
            CloudEventFactory.generate_cloud_event_id(),
            build_proto_payload_for_test(),
            u_cloud_event_attributes,
        )
        result = UCloudEvent.to_message(cloud_event)
        self.assertIsNotNone(result)
        self.assertEqual(UCloudEvent.get_ttl(cloud_event), result.attributes.ttl)
        self.assertEqual(UCloudEvent.get_token(cloud_event), result.attributes.token)
        self.assertEqual(
            UCloudEvent.get_sink(cloud_event),
            LongUriSerializer().serialize(result.attributes.sink),
        )
        self.assertEqual(
            UCloudEvent.get_payload(cloud_event).SerializeToString(),
            result.payload.value,
        )
        self.assertEqual(
            UCloudEvent.get_source(cloud_event),
            LongUriSerializer().serialize(result.attributes.source),
        )
        self.assertEqual(
            UCloudEvent.get_priority(cloud_event),
            UPriority.Name(result.attributes.priority),
        )

        cloud_event1 = UCloudEvent.from_message(result)
        cloud_event.__delitem__("time")
        cloud_event1.__delitem__("time")
        self.assertEqual(cloud_event, cloud_event1)
        self.assertEqual(cloud_event.get_data(), cloud_event1.get_data())
        self.assertEqual(
            UCloudEvent.get_source(cloud_event),
            UCloudEvent.get_source(cloud_event1),
        )
        self.assertEqual(
            UCloudEvent.get_sink(cloud_event),
            UCloudEvent.get_sink(cloud_event1),
        )
        self.assertEqual(
            UCloudEvent.get_specversion(cloud_event),
            UCloudEvent.get_specversion(cloud_event1),
        )
        self.assertEqual(
            UCloudEvent.get_priority(cloud_event),
            UCloudEvent.get_priority(cloud_event1),
        )
        self.assertEqual(UCloudEvent.get_id(cloud_event), UCloudEvent.get_id(cloud_event1))
        self.assertEqual(
            UCloudEvent.get_type(cloud_event),
            UCloudEvent.get_type(cloud_event1),
        )
        self.assertEqual(
            UCloudEvent.get_request_id(cloud_event),
            UCloudEvent.get_request_id(cloud_event1),
        )

    def test_to_from_message_from_request_cloudevent_without_attributes(self):
        # additional attributes
        u_cloud_event_attributes = UCloudEventAttributesBuilder().build()

        cloud_event = CloudEventFactory.request(
            build_uri_for_test(),
            "//bo.cloud/petapp/1/rpc.response",
            CloudEventFactory.generate_cloud_event_id(),
            build_proto_payload_for_test(),
            u_cloud_event_attributes,
        )
        result = UCloudEvent.to_message(cloud_event)
        self.assertIsNotNone(result)
        self.assertFalse(result.attributes.HasField("ttl"))
        self.assertEqual(
            UCloudEvent.get_sink(cloud_event),
            LongUriSerializer().serialize(result.attributes.sink),
        )
        self.assertEqual(
            UCloudEvent.get_payload(cloud_event).SerializeToString(),
            result.payload.value,
        )
        self.assertEqual(
            UCloudEvent.get_source(cloud_event),
            LongUriSerializer().serialize(result.attributes.source),
        )
        self.assertEqual(result.attributes.priority, 0)

        cloud_event1 = UCloudEvent.from_message(result)
        self.assertEqual(cloud_event.get_data(), cloud_event1.get_data())
        self.assertEqual(
            UCloudEvent.get_source(cloud_event),
            UCloudEvent.get_source(cloud_event1),
        )
        self.assertEqual(
            UCloudEvent.get_sink(cloud_event),
            UCloudEvent.get_sink(cloud_event1),
        )
        self.assertEqual(
            UCloudEvent.get_specversion(cloud_event),
            UCloudEvent.get_specversion(cloud_event1),
        )
        self.assertEqual(
            UCloudEvent.get_priority(cloud_event),
            UCloudEvent.get_priority(cloud_event1),
        )
        self.assertEqual(UCloudEvent.get_id(cloud_event), UCloudEvent.get_id(cloud_event1))
        self.assertEqual(
            UCloudEvent.get_type(cloud_event),
            UCloudEvent.get_type(cloud_event1),
        )
        self.assertEqual(
            UCloudEvent.get_request_id(cloud_event),
            UCloudEvent.get_request_id(cloud_event1),
        )

    def test_to_from_message_from_ucp_cloudevent(self):
        # additional attributes
        u_cloud_event_attributes = UCloudEventAttributesBuilder().with_ttl(3).with_token("someOAuthToken").build()

        cloud_event = CloudEventFactory.request(
            build_uri_for_test(),
            "//bo.cloud/petapp/1/rpc.response",
            CloudEventFactory.generate_cloud_event_id(),
            build_proto_payload_for_test(),
            u_cloud_event_attributes,
        )
        cloud_event.__setitem__("priority", "CS4")
        cloud_event.__setitem__("commstatus", 16)
        cloud_event.__setitem__("permission_level", 4)

        result = UCloudEvent.to_message(cloud_event)
        self.assertIsNotNone(result)
        self.assertEqual(UPriority.UPRIORITY_CS4, result.attributes.priority)
        cloud_event1 = UCloudEvent.from_message(result)
        self.assertEqual(
            UCloudEvent.get_priority(cloud_event1),
            UPriority.Name(result.attributes.priority),
        )

    def test_from_message_with_null_message(self):
        with self.assertRaises(ValueError) as context:
            UCloudEvent.from_message(None)
            self.assertTrue("message cannot be null." in context.exception)

    def test_cloud_event_to_string(self):
        u_cloud_event_attributes = UCloudEventAttributesBuilder().with_ttl(3).with_token("someOAuthToken").build()

        cloud_event = CloudEventFactory.request(
            build_uri_for_test(),
            "//bo.cloud/petapp/1/rpc.response",
            CloudEventFactory.generate_cloud_event_id(),
            build_proto_payload_for_test(),
            u_cloud_event_attributes,
        )
        cloud_event_string = UCloudEvent.to_string(cloud_event)
        self.assertTrue(
            "source='/body.access//door.front_left#Door', sink='//bo.cloud/petapp/1/rpc.response', type='req.v1'}"
            in cloud_event_string
        )

    def test_cloud_event_to_string_none(self):
        cloud_event_string = UCloudEvent.to_string(None)
        self.assertEqual(cloud_event_string, "null")

    def test_get_upayload_format_from_content_type(self):
        new_format = UCloudEvent().get_upayload_format_from_content_type("application/json")
        self.assertEqual(new_format, UPayloadFormat.UPAYLOAD_FORMAT_JSON)

    def test_to_message_none_entry(self):
        with self.assertRaises(ValueError) as context:
            UCloudEvent().to_message(None)
            self.assertTrue("Cloud Event can't be None" in context.exception)
