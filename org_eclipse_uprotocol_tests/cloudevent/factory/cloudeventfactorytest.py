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

from google.protobuf import any_pb2

from org_eclipse_uprotocol.cloudevent.datamodel.ucloudeventattributes import UCloudEventAttributesBuilder
from org_eclipse_uprotocol.cloudevent.factory.cloudeventfactory import CloudEventFactory
from org_eclipse_uprotocol.cloudevent.factory.ucloudevent import UCloudEvent
from org_eclipse_uprotocol.proto.cloudevents_pb2 import CloudEvent
from org_eclipse_uprotocol.proto.uattributes_pb2 import UMessageType, UPriority
from org_eclipse_uprotocol.proto.uri_pb2 import UUri, UEntity, UResource
from org_eclipse_uprotocol.uri.serializer.longuriserializer import LongUriSerializer


class CloudEventFactoryTest(unittest.TestCase):
    DATA_CONTENT_TYPE = "application/cloudevents+protobuf"

    def test_create_base_cloud_event(self):
        source = self.build_uri_for_test()

        # fake payload
        proto_payload = self.build_proto_payload_for_test()

        # additional attributes
        u_cloud_event_attributes = UCloudEventAttributesBuilder().with_hash("somehash").with_priority(
            UPriority.UPRIORITY_CS1).with_ttl(3).with_token("someOAuthToken").build()

        # build the cloud event
        cloud_event = CloudEventFactory.build_base_cloud_event("testme", source, proto_payload, proto_payload.type_url,
                                                               u_cloud_event_attributes, UCloudEvent.get_event_type(
                UMessageType.UMESSAGE_TYPE_PUBLISH))

        self.assertEqual("1.0", UCloudEvent.get_specversion(cloud_event))
        self.assertEqual("testme", UCloudEvent.get_id(cloud_event))
        self.assertEqual(source, UCloudEvent.get_source(cloud_event))
        self.assertEqual('pub.v1', UCloudEvent.get_type(cloud_event))
        self.assertNotIn("sink", cloud_event.get_attributes())
        self.assertEqual("somehash", UCloudEvent.get_hash(cloud_event))
        self.assertEqual(UPriority.UPRIORITY_CS1, UCloudEvent.get_priority(cloud_event))
        self.assertEqual(3, UCloudEvent.get_ttl(cloud_event))
        self.assertEqual("someOAuthToken", UCloudEvent.get_token(cloud_event))
        self.assertEqual(proto_payload, UCloudEvent.get_payload(cloud_event))

    def build_uri_for_test(self):
        uri = UUri(entity=UEntity(name="body.access"),
                   resource=UResource(name="door", instance="front_left", message="Door"))
        return LongUriSerializer().serialize(uri)

    def build_proto_payload_for_test(self):
        ce_proto = CloudEvent(spec_version="1.0", source="https://example.com", id="hello", type="example.demo",
                              proto_data=any_pb2.Any())

        any_obj = any_pb2.Any()
        any_obj.Pack(ce_proto)
        return any_obj


if __name__ == '__main__':
    unittest.main()
