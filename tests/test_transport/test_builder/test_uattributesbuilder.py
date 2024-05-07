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
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.proto.uattributes_pb2 import UPriority, UMessageType
from uprotocol.proto.uri_pb2 import UUri, UAuthority, UEntity
from uprotocol.proto.ustatus_pb2 import UCode
from uprotocol.uri.factory.uresource_builder import UResourceBuilder
from uprotocol.uuid.factory.uuidfactory import Factories


def build_source():
    return UUri(
        authority=UAuthority(name="vcu.someVin.veh.steven.gm.com"),
        entity=UEntity(name="petapp.steven.gm.com", version_major=1),
        resource=UResourceBuilder.for_rpc_request(None),
    )


def build_sink():
    return UUri(
        authority=UAuthority(name="vcu.someVin.veh.steven.gm.com"),
        entity=UEntity(name="petapp.steven.gm.com", version_major=1),
        resource=UResourceBuilder.for_rpc_response(),
    )


def get_uuid():
    return Factories.UPROTOCOL.create()


class TestUAttributesBuilder(unittest.TestCase):

    def test_publish(self):
        source = build_source()
        builder = UAttributesBuilder.publish(source, UPriority.UPRIORITY_CS1)
        self.assertIsNotNone(builder)
        attributes = builder.build()
        self.assertIsNotNone(attributes)
        self.assertEqual(UMessageType.UMESSAGE_TYPE_PUBLISH, attributes.type)
        self.assertEqual(UPriority.UPRIORITY_CS1, attributes.priority)

    def test_notification(self):
        source = build_source()
        sink = build_sink()
        builder = UAttributesBuilder.notification(
            source, sink, UPriority.UPRIORITY_CS1
        )
        self.assertIsNotNone(builder)
        attributes = builder.build()
        self.assertIsNotNone(attributes)
        self.assertEqual(
            UMessageType.UMESSAGE_TYPE_NOTIFICATION, attributes.type
        )
        self.assertEqual(UPriority.UPRIORITY_CS1, attributes.priority)
        self.assertEqual(sink, attributes.sink)

    def test_request(self):
        source = build_source()
        sink = build_sink()
        ttl = 1000
        builder = UAttributesBuilder.request(
            source, sink, UPriority.UPRIORITY_CS4, ttl
        )
        self.assertIsNotNone(builder)
        attributes = builder.build()
        self.assertIsNotNone(attributes)
        self.assertEqual(UMessageType.UMESSAGE_TYPE_REQUEST, attributes.type)
        self.assertEqual(UPriority.UPRIORITY_CS4, attributes.priority)
        self.assertEqual(sink, attributes.sink)
        self.assertEqual(ttl, attributes.ttl)

    def test_response(self):
        source = build_source()
        sink = build_sink()
        req_id = get_uuid()
        builder = UAttributesBuilder.response(
            source, sink, UPriority.UPRIORITY_CS6, req_id
        )
        self.assertIsNotNone(builder)
        attributes = builder.build()
        self.assertIsNotNone(attributes)
        self.assertEqual(UMessageType.UMESSAGE_TYPE_RESPONSE, attributes.type)
        self.assertEqual(UPriority.UPRIORITY_CS6, attributes.priority)
        self.assertEqual(sink, attributes.sink)
        self.assertEqual(req_id, attributes.reqid)

    def test_response_with_existing_request(self):
        request = UAttributesBuilder.request(
            build_source(), build_sink(), UPriority.UPRIORITY_CS6, 1000
        ).build()
        builder = UAttributesBuilder.response(request)
        self.assertIsNotNone(builder)
        response = builder.build()
        self.assertIsNotNone(response)
        self.assertEqual(UMessageType.UMESSAGE_TYPE_RESPONSE, response.type)
        self.assertEqual(UPriority.UPRIORITY_CS6, response.priority)
        self.assertEqual(request.sink, response.source)
        self.assertEqual(request.source, response.sink)
        self.assertEqual(request.id, response.reqid)

    def test_build(self):
        req_id = get_uuid()
        builder = (
            UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS1)
            .withTtl(1000)
            .withToken("test_token")
            .withSink(build_sink())
            .withPermissionLevel(2)
            .withCommStatus(UCode.CANCELLED)
            .withReqId(req_id)
            .withTraceparent("test_traceparent")
        )
        attributes = builder.build()
        self.assertIsNotNone(attributes)
        self.assertEqual(UMessageType.UMESSAGE_TYPE_PUBLISH, attributes.type)
        self.assertEqual(UPriority.UPRIORITY_CS1, attributes.priority)
        self.assertEqual(1000, attributes.ttl)
        self.assertEqual("test_token", attributes.token)
        self.assertEqual(build_source(), attributes.source)
        self.assertEqual(build_sink(), attributes.sink)
        self.assertEqual(2, attributes.permission_level)
        self.assertEqual(UCode.CANCELLED, attributes.commstatus)
        self.assertEqual(req_id, attributes.reqid)
        self.assertEqual("test_traceparent", attributes.traceparent)

    def test_publish_source_is_none(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.publish(None, UPriority.UPRIORITY_CS1)
            self.assertTrue("Source cannot be None." in context.exception)

    def test_publish_priority_is_none(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.publish(build_source(), None)
            self.assertTrue("UPriority cannot be null." in context.exception)

    def test_notification_source_is_none(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.notification(
                None, build_sink(), UPriority.UPRIORITY_CS1
            )
            self.assertTrue("Source cannot be None." in context.exception)

    def test_notification_priority_is_none(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.notification(build_source(), build_sink(), None)
            self.assertTrue("UPriority cannot be null." in context.exception)

    def test_notification_sink_is_none(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.notification(
                build_source(), None, UPriority.UPRIORITY_CS1
            )
            self.assertTrue("sink cannot be null." in context.exception)

    def test_request_source_is_none(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.request(
                None, build_sink(), UPriority.UPRIORITY_CS1, 1000
            )
            self.assertTrue("Source cannot be None." in context.exception)

    def test_request_priority_is_none(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.request(
                build_source(), build_sink(), None, 1000
            )
            self.assertTrue("UPriority cannot be null." in context.exception)

    def test_request_sink_is_none(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.request(
                build_source(), None, UPriority.UPRIORITY_CS1, 1000
            )
            self.assertTrue("sink cannot be null." in context.exception)

    def test_request_ttl_is_none(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.request(
                build_source(), build_sink(), UPriority.UPRIORITY_CS1, None
            )
            self.assertTrue("ttl cannot be null." in context.exception)

    def test_response_priority_is_none(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.response(
                build_source(), build_sink(), None, get_uuid()
            )
            self.assertTrue("UPriority cannot be null." in context.exception)

    def test_response_sink_is_none(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.response(
                build_source(), None, UPriority.UPRIORITY_CS1, get_uuid()
            )
            self.assertTrue("sink cannot be null." in context.exception)

    def test_response_reqid_is_none(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.response(
                build_source(), build_sink(), UPriority.UPRIORITY_CS1, None
            )
            self.assertTrue("reqid cannot be null." in context.exception)

    def test_response_request_is_none(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.response(None)
            self.assertTrue("request cannot be null." in context.exception)


if __name__ == "__main__":
    unittest.main()
