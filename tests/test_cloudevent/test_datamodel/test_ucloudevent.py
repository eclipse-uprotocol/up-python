# -------------------------------------------------------------------------
#
# Copyright (c) 2023 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License") you may not use this file except in compliance
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

from uprotocol.proto.uri_pb2 import UUri, UEntity, UResource
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.proto.cloudevents_pb2 import CloudEvent
from uprotocol.proto.uattributes_pb2 import UMessageType, UPriority
from uprotocol.cloudevent.factory.cloudeventfactory import CloudEventFactory
from uprotocol.proto.ustatus_pb2 import UCode
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.uuid.serializer.longuuidserializer import LongUuidSerializer
import time
import unittest

from google.protobuf import any_pb2

from uprotocol.cloudevent.datamodel.ucloudeventattributes import UCloudEventAttributesBuilder
from uprotocol.cloudevent.factory.ucloudevent import UCloudEvent

def build_uri_for_test():
    uri = UUri(entity=UEntity(name="body.access"),
               resource=UResource(name="door", instance="front_left", message="Door"))
    return LongUriSerializer().serialize(uri)


def build_proto_payload_for_test():
    ce_proto = CloudEvent(spec_version="1.0", source="//VCU.MY_CAR_VIN/body.access//door.front_left#Door", id="hello",
                          type="example.demo",
                          proto_data=any_pb2.Any())

    any_obj = any_pb2.Any()
    any_obj.Pack(ce_proto)
    return any_obj


def build_cloud_event_for_test():
    source = build_uri_for_test()
    proto_payload = build_proto_payload_for_test()
    # additional attributes
    u_cloud_event_attributes = UCloudEventAttributesBuilder().with_hash("somehash").with_priority(
        UPriority.UPRIORITY_CS1).with_ttl(3).with_token("someOAuthToken").build()

    # build the cloud event
    cloud_event = CloudEventFactory.build_base_cloud_event("testme", source, proto_payload.SerializeToString(),
                                                           proto_payload.type_url, u_cloud_event_attributes,
                                                           UCloudEvent.get_event_type(
                                                               UMessageType.UMESSAGE_TYPE_PUBLISH))
    return cloud_event


class TestUCloudEvent(unittest.TestCase):
    DATA_CONTENT_TYPE = "application/x-protobuf"

    def test_extract_source_from_cloudevent(self):
        cloud_event = build_cloud_event_for_test()
        source = UCloudEvent.get_source(cloud_event)
        self.assertEquals("/body.access//door.front_left#Door", source)

    def test_extract_sink_from_cloudevent_when_sink_exists(self):
        sink = "//bo.cloud/petapp/1/rpc.response"
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("sink", sink)
        self.assertEquals(sink, UCloudEvent.get_sink(cloud_event))

    def test_extract_sink_from_cloudevent_when_sink_does_not_exist(self):
        cloud_event = build_cloud_event_for_test()
        self.assertEquals(None, UCloudEvent.get_sink(cloud_event))

    def test_extract_requestId_from_cloudevent_when_requestId_exists(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("reqid", "somereqid")
        self.assertEquals("somereqid", UCloudEvent.get_request_id(cloud_event))

    def test_extract_requestId_from_cloudevent_when_requestId_does_not_exist(self):
        cloud_event = build_cloud_event_for_test()
        self.assertEquals(None, UCloudEvent.get_request_id(cloud_event))

    def test_extract_requestId_from_cloudevent_when_requestId_value_is_null(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("reqid", None)
        self.assertEquals(None, UCloudEvent.get_request_id(cloud_event))

    def test_extract_hash_from_cloudevent_when_hash_exists(self):
        cloud_event = build_cloud_event_for_test()
        self.assertEquals("somehash", UCloudEvent.get_hash(cloud_event))

    def test_extract_hash_from_cloudevent_when_hash_does_not_exist(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__delitem__("hash")
        self.assertEquals(None, UCloudEvent.get_hash(cloud_event))

    def test_extract_priority_from_cloudevent_when_priority_exists(self):
        cloud_event = build_cloud_event_for_test()
        self.assertEquals(UPriority.Name(UPriority.UPRIORITY_CS1), UCloudEvent.get_priority(cloud_event))

    def test_extract_priority_from_cloudevent_when_priority_does_not_exist(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__delitem__("priority")
        self.assertEquals(None, UCloudEvent.get_priority(cloud_event))

    def test_extract_ttl_from_cloudevent_when_ttl_exists(self):
        cloud_event = build_cloud_event_for_test()
        self.assertEquals(3, UCloudEvent.get_ttl(cloud_event))

    def test_extract_ttl_from_cloudevent_when_ttl_does_not_exists(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__delitem__("ttl")
        self.assertEquals(None, UCloudEvent.get_ttl(cloud_event))

    def test_extract_token_from_cloudevent_when_token_exists(self):
        cloud_event = build_cloud_event_for_test()
        self.assertEquals("someOAuthToken", UCloudEvent.get_token(cloud_event))

    def test_extract_token_from_cloudevent_when_token_does_not_exists(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__delitem__("token")
        self.assertEquals(None, UCloudEvent.get_token(cloud_event))

    def test_cloudevent_has_platform_error_when_platform_error_exists(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("commstatus", UCode.ABORTED)
        self.assertEquals(10, UCloudEvent.get_communication_status(cloud_event))

    def test_cloudevent_has_platform_error_when_platform_error_does_not_exist(self):
        cloud_event = build_cloud_event_for_test()
        self.assertEquals(UCode.OK, UCloudEvent.get_communication_status(cloud_event))

    def test_extract_platform_error_from_cloudevent_when_platform_error_exists_in_wrong_format(self):
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("commstatus", "boom")
        self.assertEquals(UCode.OK, UCloudEvent.get_communication_status(cloud_event))

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

    def test_cloudevent_is_expired_when_ttl_1_mili(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("ttl", 1)
        cloud_event.__setitem__('id', str_uuid)
        time.sleep(8)
        self.assertTrue(UCloudEvent.is_expired(cloud_event))

    def test_cloudevent_is_expired_for_invalid_uuid(self):
        uuid = Factories.UPROTOCOL.create()
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__("ttl", 50000)
        cloud_event.__setitem__('id', "")
        self.assertFalse(UCloudEvent.is_expired(cloud_event))

    def test_cloudevent_has_a_UUIDV8_id(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_cloud_event_for_test()
        cloud_event.__setitem__('id', str_uuid)
        self.assertTrue(UCloudEvent.is_cloud_event_id(cloud_event))

    def test_to_message_with_valid_event(self):
        # additional attributes
        u_cloud_event_attributes = UCloudEventAttributesBuilder().with_priority(
            UPriority.UPRIORITY_CS2).with_ttl(3).build()
        cloud_event = CloudEventFactory.publish(build_uri_for_test(), build_proto_payload_for_test(),
                                                u_cloud_event_attributes)
        u_message = UCloudEvent.toMessage(cloud_event)
        self.assertIsNotNone(u_message)

    def test_from_message_with_valid_message(self):
        # additional attributes
        u_cloud_event_attributes = UCloudEventAttributesBuilder().with_priority(
            UPriority.UPRIORITY_CS2).with_ttl(3).build()
        cloud_event = CloudEventFactory.publish(build_uri_for_test(), build_proto_payload_for_test(),
                                                u_cloud_event_attributes)
        u_message = UCloudEvent.toMessage(cloud_event)
        self.assertIsNotNone(u_message)
        cloud_event1 = UCloudEvent.fromMessage(u_message)
        self.assertIsNotNone(cloud_event1)
        self.assertEquals(cloud_event, cloud_event1)
        self.assertEquals(cloud_event.get_data(), cloud_event1.get_data())
        self.assertEquals(UCloudEvent.get_source(cloud_event), UCloudEvent.get_source(cloud_event1))
        self.assertEquals(UCloudEvent.get_specversion(cloud_event), UCloudEvent.get_specversion(cloud_event1))
        self.assertEquals(UCloudEvent.get_priority(cloud_event), UCloudEvent.get_priority(cloud_event1))
        self.assertEquals(UCloudEvent.get_id(cloud_event), UCloudEvent.get_id(cloud_event1))
        self.assertEquals(UCloudEvent.get_type(cloud_event), UCloudEvent.get_type(cloud_event1))

    def test_to_from_message_from_request_cloudevent(self):
        # additional attributes
        u_cloud_event_attributes = UCloudEventAttributesBuilder().with_priority(
            UPriority.UPRIORITY_CS2).with_ttl(3).with_token("someOAuthToken").build()

        cloud_event = CloudEventFactory.request(build_uri_for_test(), "//bo.cloud/petapp/1/rpc.response",
                                                CloudEventFactory.generate_cloud_event_id(),
                                                build_proto_payload_for_test(),
                                                u_cloud_event_attributes)
        result = UCloudEvent.toMessage(cloud_event)
        self.assertIsNotNone(result)
        self.assertEquals(UCloudEvent.get_ttl(cloud_event), result.attributes.ttl)
        self.assertEquals(UCloudEvent.get_token(cloud_event), result.attributes.token)
        self.assertEquals(UCloudEvent.get_sink(cloud_event),
                          LongUriSerializer().serialize(result.attributes.sink))
        self.assertEquals(UCloudEvent.get_payload(cloud_event).SerializeToString(), result.payload.value)
        self.assertEquals(UCloudEvent.get_source(cloud_event),
                          LongUriSerializer().serialize(result.source))
        self.assertEquals(UCloudEvent.get_priority(cloud_event),
                          UPriority.Name(result.attributes.priority))

        cloud_event1 = UCloudEvent.fromMessage(result)
        self.assertEquals(cloud_event, cloud_event1)
        self.assertEquals(cloud_event.get_data(), cloud_event1.get_data())
        self.assertEquals(UCloudEvent.get_source(cloud_event), UCloudEvent.get_source(cloud_event1))
        self.assertEquals(UCloudEvent.get_sink(cloud_event), UCloudEvent.get_sink(cloud_event1))
        self.assertEquals(UCloudEvent.get_specversion(cloud_event), UCloudEvent.get_specversion(cloud_event1))
        self.assertEquals(UCloudEvent.get_priority(cloud_event), UCloudEvent.get_priority(cloud_event1))
        self.assertEquals(UCloudEvent.get_id(cloud_event), UCloudEvent.get_id(cloud_event1))
        self.assertEquals(UCloudEvent.get_type(cloud_event), UCloudEvent.get_type(cloud_event1))
        self.assertEquals(UCloudEvent.get_request_id(cloud_event), UCloudEvent.get_request_id(cloud_event1))

    def test_to_from_message_from_request_cloudevent_without_attributes(self):
        # additional attributes
        u_cloud_event_attributes = UCloudEventAttributesBuilder().build()

        cloud_event = CloudEventFactory.request(build_uri_for_test(), "//bo.cloud/petapp/1/rpc.response",
                                                CloudEventFactory.generate_cloud_event_id(),
                                                build_proto_payload_for_test(),
                                                u_cloud_event_attributes)
        result = UCloudEvent.toMessage(cloud_event)
        self.assertIsNotNone(result)
        self.assertFalse(result.attributes.HasField('ttl'))
        self.assertEquals(UCloudEvent.get_sink(cloud_event),
                     LongUriSerializer().serialize(result.attributes.sink))
        self.assertEquals(UCloudEvent.get_payload(cloud_event).SerializeToString(), result.payload.value)
        self.assertEquals(UCloudEvent.get_source(cloud_event), LongUriSerializer().serialize(result.source))
        self.assertEquals(result.attributes.priority, 0)

        cloud_event1 = UCloudEvent.fromMessage(result)
        self.assertEquals(cloud_event.get_data(), cloud_event1.get_data())
        self.assertEquals(UCloudEvent.get_source(cloud_event),UCloudEvent.get_source(cloud_event1))
        self.assertEquals(UCloudEvent.get_sink(cloud_event),UCloudEvent.get_sink(cloud_event1))
        self.assertEquals(UCloudEvent.get_specversion(cloud_event),UCloudEvent.get_specversion(cloud_event1))
        self.assertEquals(UCloudEvent.get_priority(cloud_event),UCloudEvent.get_priority(cloud_event1))
        self.assertEquals(UCloudEvent.get_id(cloud_event),UCloudEvent.get_id(cloud_event1))
        self.assertEquals(UCloudEvent.get_type(cloud_event),UCloudEvent.get_type(cloud_event1))
        self.assertEquals(UCloudEvent.get_request_id(cloud_event),UCloudEvent.get_request_id(cloud_event1))

    def test_to_from_message_from_UCP_cloudevent(self):
        # additional attributes
        u_cloud_event_attributes = UCloudEventAttributesBuilder().with_ttl(3).with_token("someOAuthToken").build()

        cloud_event = CloudEventFactory.request(build_uri_for_test(), "//bo.cloud/petapp/1/rpc.response",
                                                CloudEventFactory.generate_cloud_event_id(),
                                                build_proto_payload_for_test(),
                                                u_cloud_event_attributes)
        cloud_event.__setitem__("priority", "CS4")

        result = UCloudEvent.toMessage(cloud_event)
        self.assertIsNotNone(result)
        self.assertEquals(UPriority.UPRIORITY_CS4,result.attributes.priority)
        cloud_event1 = UCloudEvent.fromMessage(result)
        self.assertEquals(UCloudEvent.get_priority(cloud_event1),UPriority.Name(result.attributes.priority))

