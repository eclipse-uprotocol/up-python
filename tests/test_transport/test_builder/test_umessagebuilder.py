"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import unittest

from google.protobuf.any_pb2 import Any

from uprotocol.communication.upayload import UPayload
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.v1.uattributes_pb2 import (
    UAttributes,
    UMessageType,
    UPayloadFormat,
    UPriority,
)
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri


def build_source():
    return UUri(ue_id=2, ue_version_major=1, resource_id=0)


def build_sink():
    return UUri(ue_id=2, ue_version_major=1, resource_id=0)


def get_uuid():
    return Factories.UPROTOCOL.create()


class TestUMessageBuilder(unittest.IsolatedAsyncioTestCase):
    def test_publish(self):
        """
        Test Publish
        """
        publish: UMessage = UMessageBuilder.publish(build_source()).build()
        self.assertIsNotNone(publish)
        self.assertEqual(UMessageType.UMESSAGE_TYPE_PUBLISH, publish.attributes.type)
        self.assertEqual(UPriority.UPRIORITY_CS1, publish.attributes.priority)

    def test_notification(self):
        """
        Test Notification
        """
        sink = build_sink()
        notification: UMessage = UMessageBuilder.notification(build_source(), sink).build()
        self.assertIsNotNone(notification)
        self.assertEqual(
            UMessageType.UMESSAGE_TYPE_NOTIFICATION,
            notification.attributes.type,
        )
        self.assertEqual(UPriority.UPRIORITY_CS1, notification.attributes.priority)
        self.assertEqual(sink, notification.attributes.sink)

    def test_request(self):
        """
        Test Request
        """
        sink = build_sink()
        ttl = 1000
        request: UMessage = UMessageBuilder.request(build_source(), sink, ttl).build()
        self.assertIsNotNone(request)
        self.assertEqual(UMessageType.UMESSAGE_TYPE_REQUEST, request.attributes.type)
        self.assertEqual(UPriority.UPRIORITY_CS4, request.attributes.priority)
        self.assertEqual(sink, request.attributes.sink)
        self.assertEqual(ttl, request.attributes.ttl)

    def test_request_with_priority(self):
        """
        Test Request
        """
        sink = build_sink()
        ttl = 1000
        request: UMessage = (
            UMessageBuilder.request(build_source(), sink, ttl).with_priority(UPriority.UPRIORITY_CS5).build()
        )
        self.assertIsNotNone(request)
        self.assertEqual(UMessageType.UMESSAGE_TYPE_REQUEST, request.attributes.type)
        self.assertEqual(UPriority.UPRIORITY_CS5, request.attributes.priority)
        self.assertEqual(sink, request.attributes.sink)
        self.assertEqual(ttl, request.attributes.ttl)

    def test_response(self):
        """
        Test Response
        """
        sink = build_sink()
        req_id = get_uuid()
        response: UMessage = UMessageBuilder.response(build_source(), sink, req_id).build()
        self.assertIsNotNone(response)
        self.assertEqual(UMessageType.UMESSAGE_TYPE_RESPONSE, response.attributes.type)
        self.assertEqual(UPriority.UPRIORITY_CS4, response.attributes.priority)
        self.assertEqual(sink, response.attributes.sink)
        self.assertEqual(req_id, response.attributes.reqid)

    def test_response_with_existing_request(self):
        """
        Test Response with existing request
        """
        request: UMessage = UMessageBuilder.request(build_source(), build_sink(), 1000).build()
        response: UMessage = UMessageBuilder.response_for_request(request.attributes).build()
        self.assertIsNotNone(response)
        self.assertEqual(UMessageType.UMESSAGE_TYPE_RESPONSE, response.attributes.type)
        self.assertEqual(UPriority.UPRIORITY_CS4, request.attributes.priority)
        self.assertEqual(UPriority.UPRIORITY_CS4, response.attributes.priority)
        self.assertEqual(request.attributes.source, response.attributes.sink)
        self.assertEqual(request.attributes.sink, response.attributes.source)
        self.assertEqual(request.attributes.id, response.attributes.reqid)

    def test_build(self):
        """
        Test Build
        """
        builder: UMessageBuilder = (
            UMessageBuilder.publish(build_source())
            .with_token("test_token")
            .with_permission_level(2)
            .with_commstatus(UCode.CANCELLED)
            .with_traceparent("myParents")
        )
        message: UMessage = builder.build()
        attributes: UAttributes = message.attributes
        self.assertIsNotNone(message)
        self.assertIsNotNone(attributes)
        self.assertEqual(UMessageType.UMESSAGE_TYPE_PUBLISH, attributes.type)
        self.assertEqual(UPriority.UPRIORITY_CS1, attributes.priority)
        self.assertEqual("test_token", attributes.token)
        self.assertEqual(2, attributes.permission_level)
        self.assertEqual(UCode.CANCELLED, attributes.commstatus)
        self.assertEqual("myParents", attributes.traceparent)

    def test_build_with_upayload(self):
        """
        Test building UMessage with UPayload payload
        """
        message: UMessage = UMessageBuilder.publish(build_source()).build_from_upayload(
            UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, data=build_sink().SerializeToString())
        )
        self.assertIsNotNone(message)
        self.assertIsNotNone(message.payload)
        self.assertEqual(
            UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF,
            message.attributes.payload_format,
        )
        self.assertEqual(message.payload, build_sink().SerializeToString())

    def test_build_with_any_payload(self):
        """
        Test building UMessage with Any payload
        """
        message: UMessage = UMessageBuilder.publish(build_source()).build_from_upayload(
            UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY, data=Any().SerializeToString())
        )
        self.assertIsNotNone(message)
        self.assertIsNotNone(message.payload)
        self.assertEqual(
            UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
            message.attributes.payload_format,
        )
        self.assertEqual(message.payload, Any().SerializeToString())

    def test_build_response_with_wrong_priority(self):
        """
        Test building response with wrong priority
        """
        sink = build_sink()
        req_id = get_uuid()
        response = UMessageBuilder.response(build_source(), sink, req_id).with_priority(UPriority.UPRIORITY_CS3).build()
        self.assertIsNotNone(response)
        self.assertEqual(UMessageType.UMESSAGE_TYPE_RESPONSE, response.attributes.type)
        self.assertEqual(UPriority.UPRIORITY_CS4, response.attributes.priority)
        self.assertEqual(sink, response.attributes.sink)
        self.assertEqual(req_id, response.attributes.reqid)

    def test_build_request_with_wrong_priority(self):
        """
        Test building request with wrong priority
        """
        sink = build_sink()
        ttl = 1000
        request = UMessageBuilder.request(build_source(), sink, ttl).with_priority(UPriority.UPRIORITY_CS0).build()
        self.assertIsNotNone(request)
        self.assertEqual(UMessageType.UMESSAGE_TYPE_REQUEST, request.attributes.type)
        self.assertEqual(UPriority.UPRIORITY_CS4, request.attributes.priority)
        self.assertEqual(sink, request.attributes.sink)
        self.assertEqual(ttl, request.attributes.ttl)

    def test_build_notification_with_wrong_priority(self):
        """
        Test building notification with wrong priority
        """
        sink = build_sink()
        notification = UMessageBuilder.notification(build_source(), sink).with_priority(UPriority.UPRIORITY_CS0).build()
        self.assertIsNotNone(notification)
        self.assertEqual(
            UMessageType.UMESSAGE_TYPE_NOTIFICATION,
            notification.attributes.type,
        )
        self.assertEqual(UPriority.UPRIORITY_CS1, notification.attributes.priority)
        self.assertEqual(sink, notification.attributes.sink)

    def test_build_publish_with_wrong_priority(self):
        """
        Test building publish with wrong priority
        """
        publish = UMessageBuilder.publish(build_source()).with_priority(UPriority.UPRIORITY_CS0).build()
        self.assertIsNotNone(publish)
        self.assertEqual(UMessageType.UMESSAGE_TYPE_PUBLISH, publish.attributes.type)
        self.assertEqual(UPriority.UPRIORITY_CS1, publish.attributes.priority)

    def test_build_publish_with_priority(self):
        """
        Test building publish with priority
        """
        publish = UMessageBuilder.publish(build_source()).with_priority(UPriority.UPRIORITY_CS4).build()
        self.assertIsNotNone(publish)
        self.assertEqual(UMessageType.UMESSAGE_TYPE_PUBLISH, publish.attributes.type)
        self.assertEqual(UPriority.UPRIORITY_CS4, publish.attributes.priority)

    def test_publish_source_is_none(self):
        """
        Test publish with source is None
        """
        with self.assertRaises(ValueError):
            UMessageBuilder.publish(None)

    def test_notification_source_is_none(self):
        """
        Test notification with source is None
        """
        with self.assertRaises(ValueError):
            UMessageBuilder.notification(None, build_sink())

    def test_notification_sink_is_none(self):
        """
        Test notification with sink is None
        """
        with self.assertRaises(ValueError):
            UMessageBuilder.notification(build_source(), None)

    def test_request_source_is_none(self):
        """
        Test request with source is None
        """
        with self.assertRaises(ValueError):
            UMessageBuilder.request(None, build_sink(), 1000)

    def test_request_sink_is_none(self):
        """
        Test request with sink is None
        """
        with self.assertRaises(ValueError):
            UMessageBuilder.request(build_source(), None, 1000)

    def test_request_ttl_is_none(self):
        """
        Test request with ttl is None
        """
        with self.assertRaises(ValueError):
            UMessageBuilder.request(build_source(), build_sink(), None)

    def test_response_source_is_none(self):
        """
        Test response with source is None
        """
        with self.assertRaises(ValueError):
            UMessageBuilder.response(None, build_sink(), get_uuid())

    def test_response_sink_is_none(self):
        """
        Test response with sink is None
        """
        with self.assertRaises(ValueError):
            UMessageBuilder.response(build_source(), None, get_uuid())

    def test_response_req_id_is_none(self):
        """
        Test response with req_id is None
        """
        with self.assertRaises(ValueError):
            UMessageBuilder.response(build_source(), build_sink(), None)
