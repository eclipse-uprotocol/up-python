"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import time
import unittest

from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.validator.uattributesvalidator import UAttributesValidator, Validators
from uprotocol.v1.uattributes_pb2 import UAttributes, UMessageType, UPriority
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.uuid_pb2 import UUID


def build_default_uuri():
    return UUri(ue_id=1, ue_version_major=1, resource_id=0)


def build_method_uuri():
    return UUri(ue_id=1, ue_version_major=1, resource_id=1)


def build_topic_uuri():
    return UUri(ue_id=1, ue_version_major=1, resource_id=0x8000)


class TestUAttributesValidator(unittest.IsolatedAsyncioTestCase):
    def test_uattributes_validator_happy_path(self):
        message = UMessageBuilder.publish(build_topic_uuri()).build()

        validator = UAttributesValidator.get_validator(message.attributes)

        result = validator.validate(message.attributes)

        self.assertTrue(result.is_success())

        self.assertEqual(str(validator), "UAttributesValidator.Publish")

    def test_uattributes_validator_notification(self):
        message = UMessageBuilder.notification(build_topic_uuri(), build_default_uuri()).build()

        validator = UAttributesValidator.get_validator(message.attributes)

        result = validator.validate(message.attributes)

        self.assertTrue(result.is_success())

        self.assertEqual(str(validator), "UAttributesValidator.Notification")

    def test_uattributes_validator_request(self):
        message = UMessageBuilder.request(build_default_uuri(), build_method_uuri(), 1000).build()

        validator = UAttributesValidator.get_validator(message.attributes)

        result = validator.validate(message.attributes)

        self.assertTrue(result.is_success())

        self.assertEqual(str(validator), "UAttributesValidator.Request")

    def test_uattributes_validator_response(self):
        request = UMessageBuilder.request(build_default_uuri(), build_method_uuri(), 1000).build()
        message = UMessageBuilder.response(build_method_uuri(), build_default_uuri(), request.attributes.id).build()

        validator = UAttributesValidator.get_validator(message.attributes)

        result = validator.validate(message.attributes)

        self.assertTrue(result.is_success())

        self.assertEqual(str(validator), "UAttributesValidator.Response")

    def test_uattributes_validator_response_with_request_attributes(self):
        request = UMessageBuilder.request(build_default_uuri(), build_method_uuri(), 1000).build()
        message = UMessageBuilder.response_for_request(request.attributes).build()

        validator = UAttributesValidator.get_validator(message.attributes)

        result = validator.validate(message.attributes)

        self.assertTrue(result.is_success())

        self.assertEqual(str(validator), "UAttributesValidator.Response")

    def test_uattributes_validator_request_with_publish_validator(self):
        message = UMessageBuilder.request(build_default_uuri(), build_topic_uuri(), 1000).build()

        validator = Validators.PUBLISH.validator()

        result = validator.validate(message.attributes)

        self.assertFalse(result.is_success())
        self.assertEqual(str(validator), "UAttributesValidator.Publish")
        self.assertEqual(result.message, "Wrong Attribute Type [UMESSAGE_TYPE_REQUEST],Sink should not be present")

    def test_uattributes_validator_publish_with_notification_validator(self):
        message = UMessageBuilder.publish(build_topic_uuri()).build()

        validator = Validators.NOTIFICATION.validator()

        result = validator.validate(message.attributes)

        self.assertFalse(result.is_success())
        self.assertEqual(str(validator), "UAttributesValidator.Notification")
        self.assertEqual(result.message, "Wrong Attribute Type [UMESSAGE_TYPE_PUBLISH],Missing Sink")

    def test_uattributes_validator_response_with_request_validator(self):
        request = UMessageBuilder.request(build_default_uuri(), build_method_uuri(), 1000).build()
        response = UMessageBuilder.response_for_request(request.attributes).build()

        validator = Validators.REQUEST.validator()
        result = validator.validate(response.attributes)

        self.assertFalse(result.is_success())
        self.assertEqual(str(validator), "UAttributesValidator.Request")
        self.assertEqual(
            result.message,
            "Wrong Attribute Type [UMESSAGE_TYPE_RESPONSE],Missing TTL,"
            "Invalid Sink Uri,Message should not have a reqid",
        )

    def test_uattributes_validator_notification_with_response_validator(self):
        message = UMessageBuilder.notification(build_topic_uuri(), build_default_uuri()).build()

        validator = Validators.RESPONSE.validator()

        result = validator.validate(message.attributes)

        self.assertFalse(result.is_success())
        self.assertEqual(str(validator), "UAttributesValidator.Response")
        self.assertEqual(
            result.message,
            "Wrong Attribute Type [UMESSAGE_TYPE_NOTIFICATION],Invalid UPriority [UPRIORITY_CS1],Missing correlationId",
        )

    def test_uattribute_validator_request_missing_sink(self):
        message = UMessageBuilder.request(build_default_uuri(), build_default_uuri(), 1000).build()

        validator = UAttributesValidator.get_validator(message.attributes)
        result = validator.validate(message.attributes)
        self.assertTrue(result.is_failure())
        self.assertEqual(str(validator), "UAttributesValidator.Request")
        self.assertEqual(result.message, "Invalid Sink Uri")

    def test_uattribute_validator_request_valid_permission_level(self):
        message = (
            UMessageBuilder.request(build_default_uuri(), build_method_uuri(), 1000).with_permission_level(1).build()
        )

        validator = UAttributesValidator.get_validator(message.attributes)
        result = validator.validate(message.attributes)
        self.assertTrue(result.is_success())
        self.assertFalse(validator.is_expired(message.attributes))
        self.assertEqual(str(validator), "UAttributesValidator.Request")

    def test_uattribute_validator_request_expired(self):
        message = UMessageBuilder.request(build_default_uuri(), build_method_uuri(), 1).build()
        time.sleep(0.1)
        validator = UAttributesValidator.get_validator(message.attributes)
        self.assertTrue(validator.is_expired(message.attributes))

    def test_uattribute_validator_request_expired_malformed_id(self):
        attributes = UAttributes(
            id=UUID(),
            type=UMessageType.UMESSAGE_TYPE_REQUEST,
        )
        validator = UAttributesValidator.get_validator(attributes)
        self.assertFalse(validator.is_expired(attributes))

    def test_uattribute_validator_publish_with_req_id(self):
        publish = UMessageBuilder.publish(build_topic_uuri()).build()
        attributes = publish.attributes

        attributes.reqid.CopyFrom(UUID())

        validator = UAttributesValidator.get_validator(attributes)
        result = validator.validate(attributes)
        self.assertTrue(result.is_failure())
        self.assertEqual(str(validator), "UAttributesValidator.Publish")
        self.assertEqual(result.message, "Message should not have a reqid")

    def test_uattribute_validator_notification_missing_sink(self):
        message = UMessageBuilder.notification(build_topic_uuri(), build_default_uuri()).build()
        attributes = message.attributes
        attributes.ClearField("sink")
        validator = UAttributesValidator.get_validator(attributes)
        result = validator.validate(attributes)

        self.assertTrue(result.is_failure())
        self.assertEqual(str(validator), "UAttributesValidator.Notification")
        self.assertEqual(result.message, "Missing Sink")

    def test_uattribute_validator_notification_default_sink(self):
        message = UMessageBuilder.notification(build_topic_uuri(), build_default_uuri()).build()
        attributes = message.attributes
        attributes.sink.CopyFrom(UUri())
        validator = UAttributesValidator.get_validator(attributes)
        result = validator.validate(attributes)

        self.assertTrue(result.is_failure())
        self.assertEqual(str(validator), "UAttributesValidator.Notification")
        self.assertEqual(result.message, "Missing Sink")

    def test_uattribute_validator_notification_default_resource_id(self):
        message = UMessageBuilder.notification(build_topic_uuri(), build_topic_uuri()).build()
        validator = UAttributesValidator.get_validator(message.attributes)
        result = validator.validate(message.attributes)

        self.assertTrue(result.is_failure())
        self.assertEqual(str(validator), "UAttributesValidator.Notification")
        self.assertEqual(result.message, "Invalid Sink Uri")

    def test_uattribute_validator_validate_priority_less_than_cs0(self):
        message = UMessageBuilder.publish(build_topic_uuri()).build()
        attributes = message.attributes
        attributes.priority = UPriority.UPRIORITY_UNSPECIFIED
        validator = UAttributesValidator.get_validator(attributes)
        result = validator.validate(attributes)

        self.assertTrue(result.is_failure())
        self.assertEqual(str(validator), "UAttributesValidator.Publish")
        self.assertEqual(result.message, "Invalid UPriority [UPRIORITY_UNSPECIFIED]")

    def test_uattribute_validator_validate_id_missing(self):
        message = UMessageBuilder.publish(build_topic_uuri()).build()
        attributes = message.attributes
        attributes.ClearField("id")
        validator = UAttributesValidator.get_validator(attributes)
        result = validator.validate(attributes)

        self.assertTrue(result.is_failure())
        self.assertEqual(str(validator), "UAttributesValidator.Publish")
        self.assertEqual(result.message, "Missing id")

    def test_uattribute_validator_validate_priority_less_than_cs4(self):
        message = UMessageBuilder.request(build_default_uuri(), build_method_uuri(), 1000).build()
        attributes = message.attributes
        attributes.priority = UPriority.UPRIORITY_CS3
        validator = UAttributesValidator.get_validator(attributes)
        result = validator.validate(attributes)

        self.assertTrue(result.is_failure())
        self.assertEqual(str(validator), "UAttributesValidator.Request")
        self.assertEqual(result.message, "Invalid UPriority [UPRIORITY_CS3]")

    def test_uattribute_validator_validate_sink_response_missing(self):
        request = UMessageBuilder.request(build_default_uuri(), build_method_uuri(), 1000).build()
        response = UMessageBuilder.response_for_request(request.attributes).build()
        attributes = response.attributes
        attributes.ClearField("sink")
        validator = UAttributesValidator.get_validator(attributes)
        result = validator.validate(attributes)

        self.assertTrue(result.is_failure())
        self.assertEqual(str(validator), "UAttributesValidator.Response")
        self.assertEqual(result.message, "Missing Sink")

    def test_uattribute_validator_validate_sink_response_default(self):
        request = UMessageBuilder.request(build_default_uuri(), build_method_uuri(), 1000).build()
        response = UMessageBuilder.response_for_request(request.attributes).build()
        attributes = response.attributes
        attributes.sink.CopyFrom(UUri())
        validator = UAttributesValidator.get_validator(attributes)
        result = validator.validate(attributes)

        self.assertTrue(result.is_failure())
        self.assertEqual(str(validator), "UAttributesValidator.Response")
        self.assertEqual(result.message, "Missing Sink")

    def test_uattribute_validator_validate_sink_response_default_resource_id(self):
        request = UMessageBuilder.request(build_method_uuri(), build_default_uuri(), 1000).build()
        response = UMessageBuilder.response_for_request(request.attributes).build()
        validator = UAttributesValidator.get_validator(response.attributes)
        result = validator.validate(response.attributes)

        self.assertTrue(result.is_failure())
        self.assertEqual(str(validator), "UAttributesValidator.Response")
        self.assertEqual(result.message, "Invalid Sink Uri")

    def test_uattribute_validator_validate_reqid_missing(self):
        request = UMessageBuilder.request(build_default_uuri(), build_method_uuri(), 1000).build()
        response = UMessageBuilder.response_for_request(request.attributes).build()
        attributes = response.attributes
        attributes.ClearField("reqid")
        validator = UAttributesValidator.get_validator(attributes)
        result = validator.validate(attributes)

        self.assertTrue(result.is_failure())
        self.assertEqual(str(validator), "UAttributesValidator.Response")
        self.assertEqual(result.message, "Missing correlationId")

    def test_uattribute_validator_validate_reqid_default(self):
        request = UMessageBuilder.request(build_default_uuri(), build_method_uuri(), 1000).build()
        response = UMessageBuilder.response_for_request(request.attributes).build()
        attributes = response.attributes
        attributes.ClearField("reqid")
        validator = UAttributesValidator.get_validator(attributes)
        result = validator.validate(attributes)

        self.assertTrue(result.is_failure())
        self.assertEqual(str(validator), "UAttributesValidator.Response")
        self.assertEqual(result.message, "Missing correlationId")

    def test_uattribute_validator_validate_reqid_invalid(self):
        request = UMessageBuilder.request(build_default_uuri(), build_method_uuri(), 1000).build()
        response = UMessageBuilder.response_for_request(request.attributes).build()
        attributes = response.attributes
        attributes.reqid.lsb = 0xBEADBEEF
        attributes.reqid.msb = 0xDEADBEEF
        validator = UAttributesValidator.get_validator(attributes)
        result = validator.validate(attributes)

        self.assertTrue(result.is_failure())
        self.assertEqual(str(validator), "UAttributesValidator.Response")
        self.assertEqual(result.message, "Invalid correlation UUID")
