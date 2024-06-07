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
from unittest import result

from google.protobuf import any_pb2

from uprotocol.cloudevent.datamodel.ucloudeventattributes import (
    UCloudEventAttributesBuilder,
)
from uprotocol.cloudevent.factory.cloudeventfactory import CloudEventFactory
from uprotocol.cloudevent.factory.ucloudevent import UCloudEvent
from uprotocol.cloudevent.validate.cloudeventvalidator import (
    CloudEventValidator,
    Validators,
)
from uprotocol.cloudevent.cloudevents_pb2 import CloudEvent
from uprotocol.proto.uprotocol.v1.uattributes_pb2 import UPriority, UMessageType
from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri
from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.uuid.serializer.uuidserializer import UuidSerializer
from uprotocol.validation.validationresult import ValidationResult


def build_default_topic_uri_for_test():
    return UriSerializer().serialize(
        UUri(ue_id=1, ue_version_major=1, resource_id=0)
    )

def build_method_uri_for_test():
    return UriSerializer().serialize(
        UUri(ue_id=1, ue_version_major=1, resource_id=3)
    )

def build_base_publish_cloud_event_for_test():
    # uri
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
        UuidSerializer().serialize(Factories.UUIDV6.create()),
        source,
        proto_payload,
        u_cloud_event_attributes
    )
    cloud_event.__setitem__("type", "pub.v1")
    return cloud_event

    pass


def build_base_notification_cloud_event_for_test():
    # uri
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
        UuidSerializer().serialize(Factories.UUIDV6.create()),
        source,
        proto_payload,
        u_cloud_event_attributes
    )
    cloud_event.__setitem__("sink", "/1/2/0")
    cloud_event.__setitem__("type", "not.v1")
    return cloud_event

    pass


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


def build_uuri_for_test():
    return UUri(ue_id=1, resource_id=0x8000)


def build_uri_for_test():
    return UriSerializer().serialize(build_uuri_for_test())


class TestCloudEventValidator(unittest.TestCase):

    def test_create_a_v6_cloudevent_and_validate_it_against_sdk(self):
        source = build_uri_for_test()
        uuid = Factories.UUIDV6.create()
        id = UuidSerializer.serialize(uuid)
        proto_payload = build_proto_payload_for_test()
        # additional attributes
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_priority(UPriority.UPRIORITY_CS0)
            .with_ttl(1000)
            .build()
        )
        # build the cloud event
        cloud_event = CloudEventFactory.build_base_cloud_event(
            id,
            source,
            proto_payload,
            u_cloud_event_attributes
        )
        cloud_event.__setitem__("type", "pub.v1")
        validator = Validators.PUBLISH.validator()
        result = validator.validate(cloud_event)
        self.assertTrue(result.is_success())
        self.assertFalse(UCloudEvent.is_expired(cloud_event))

    def test_get_validator_for_valid_response_type_message(self):
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_priority(UPriority.UPRIORITY_CS1)
            .with_ttl(1000)
            .build()
        )

        cloud_event = CloudEventFactory.response(
            build_default_topic_uri_for_test(),
            build_method_uri_for_test(),
            UuidSerializer().serialize(Factories.UPROTOCOL.create()),
            None,
            u_cloud_event_attributes
        )

        validator = CloudEventValidator.get_validator(cloud_event)
        result = validator.validate(cloud_event)
        self.assertTrue(result.is_success())
        self.assertEqual("CloudEventValidator.Response", str(validator))

    def test_get_validator_for_valid_request_message(self):
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_priority(UPriority.UPRIORITY_CS1)
            .with_ttl(1000)
            .build()
        )

        cloud_event = CloudEventFactory.request(
            build_default_topic_uri_for_test(),
            build_method_uri_for_test(),
            None,
            u_cloud_event_attributes
        )
        cloud_event.__setitem__("source", "/1/2/8000")

        validator = CloudEventValidator.get_validator(cloud_event)
        result = validator.validate(cloud_event)
        self.assertTrue(result.is_success())
        self.assertEqual("CloudEventValidator.Request", str(validator))

    def test_get_validator_for_valid_no_type_message(self):
        cloud_event = build_base_publish_cloud_event_for_test()
        cloud_event.__delitem__("type")

        validator = CloudEventValidator.get_validator(cloud_event)
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual("CloudEventValidator.Publish", str(validator))

    def test_get_validator_for_valid_publish_type_message(self):

        cloud_event = build_base_publish_cloud_event_for_test()

        validator = CloudEventValidator.get_validator(cloud_event)
        result = validator.validate(cloud_event)
        self.assertTrue(result.is_success())
        self.assertEqual("CloudEventValidator.Publish", str(validator))

    def test_get_validator_for_invalid_type_message(self):
        cloud_event = build_base_notification_cloud_event_for_test()
        cloud_event.__setitem__("type", "")
        validator = CloudEventValidator.get_validator(cloud_event)
        self.assertEqual("CloudEventValidator.Publish", str(validator))

    def test_validate_id_when_id_is_invalid(self):
        cloud_event = build_base_publish_cloud_event_for_test()
        cloud_event.__setitem__("id", "bad")
        validator = CloudEventValidator.get_validator(cloud_event)
        result = validator.validate(cloud_event)
        self.assertTrue(result.is_failure())
        self.assertEqual(result.message, "Invalid CloudEvent Id [bad]. CloudEvent Id must be of type UUIDv8.")

    def test_validate_specversion_when_specversion_is_invalid(self):
        cloud_event = build_base_publish_cloud_event_for_test()
        cloud_event.__setitem__("specversion", "3.0")
        validator = CloudEventValidator.get_validator(cloud_event)
        result = validator.validate(cloud_event)
        self.assertTrue(result.is_failure())
        self.assertEqual(result.message, "Invalid CloudEvent version [3.0]. CloudEvent version must be 1.0.")

    def test_fetching_the_notification_validator(self):
        cloud_event = build_base_notification_cloud_event_for_test()
        validator = CloudEventValidator.get_validator(cloud_event)
        status = validator.validate_type(cloud_event).to_status()
        self.assertEqual(status, ValidationResult.STATUS_SUCCESS)
        self.assertEqual("CloudEventValidator.Notification", str(validator))

    def test_publish_validator_for_valid_publish_type_message_with_sink(self):
        cloud_event = build_base_publish_cloud_event_for_test()
        cloud_event.__setitem__("sink", "/1/2/3")
        validator = Validators.PUBLISH.validator()
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Publish should not have a sink")

    def test_publish_validator_for_invalid_source_topic(self):
        cloud_event = build_base_publish_cloud_event_for_test()
        cloud_event.__setitem__("source", "invalid-source-topic")
        validator = Validators.PUBLISH.validator()
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Invalid Publish type CloudEvent source [invalid-source-topic].")

    def test_publish_validator_for_invalid_type(self):
        cloud_event = build_base_publish_cloud_event_for_test()
        cloud_event.__setitem__("type", "not.v1")
        validator = Validators.PUBLISH.validator()
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Invalid CloudEvent type [not.v1]. " +\
                         "CloudEvent of type Publish must have a type of 'pub.v1'")
        
    def test_notification_validator_for_valid_notification_type_message(self):
        cloud_event = build_base_notification_cloud_event_for_test()
        validator = Validators.NOTIFICATION.validator()
        result = validator.validate(cloud_event)
        self.assertTrue(result.is_success())

    def test_notification_validator_for_invalid_sink(self):
        cloud_event = build_base_notification_cloud_event_for_test()
        cloud_event.__setitem__("sink", "/1/2/3")
        validator = Validators.NOTIFICATION.validator()
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Invalid Notification type CloudEvent sink [/1/2/3].")

    def test_notification_validator_for_invalid_source(self):
        cloud_event = build_base_notification_cloud_event_for_test()
        cloud_event.__setitem__("source", "invalid-source-topic")
        validator = Validators.NOTIFICATION.validator()
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Invalid Notification type CloudEvent source [invalid-source-topic].")

    def test_notification_validator_for_null_sink(self):
        cloud_event = build_base_notification_cloud_event_for_test()
        cloud_event.__setitem__("sink", "")
        validator = Validators.NOTIFICATION.validator()
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Invalid CloudEvent sink. Notification CloudEvent sink must be an  uri.")

    def test_notification_validator_when_type_is_wrong(self):
        cloud_event = build_base_notification_cloud_event_for_test()
        cloud_event.__setitem__("type", "pub.v1")
        validator = Validators.NOTIFICATION.validator()
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Invalid CloudEvent type [pub.v1]. " +\
                         "CloudEvent of type Notification must have a type of 'not.v1'")
        
    def test_request_validator_for_valid_request_message(self):
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_priority(UPriority.UPRIORITY_CS1)
            .with_ttl(1000)
            .build()
        )

        cloud_event = CloudEventFactory.request(
            build_default_topic_uri_for_test(),
            build_method_uri_for_test(),
            None,
            u_cloud_event_attributes
        )
        cloud_event.__setitem__("source", "/1/2/8000")

        validator = Validators.REQUEST.validator()
        result = validator.validate(cloud_event)
        self.assertTrue(result.is_success())

    def test_request_validator_for_invalid_sink(self):
        cloud_event = CloudEventFactory.request(
            build_default_topic_uri_for_test(),
            build_method_uri_for_test(),
            None,
            UCloudEventAttributesBuilder().build()
        )
        cloud_event.__setitem__("source", "/1/2/8000")
        cloud_event.__setitem__("sink", "/1/2/32799")
        validator = Validators.REQUEST.validator()
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Invalid RPC Request type CloudEvent sink [/1/2/32799].")

    def test_request_validator_for_invalid_source(self):
        cloud_event = CloudEventFactory.request(
            build_default_topic_uri_for_test(),
            build_method_uri_for_test(),
            None,
            UCloudEventAttributesBuilder().build()
        )
        cloud_event.__setitem__("source", "invalid-source-topic")
        validator = Validators.REQUEST.validator()
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Invalid RPC Request type CloudEvent source [invalid-source-topic].")

    def test_request_validator_for_null_sink(self):
        cloud_event = CloudEventFactory.request(
            build_default_topic_uri_for_test(),
            build_method_uri_for_test(),
            None,
            UCloudEventAttributesBuilder().build()
        )
        cloud_event.__setitem__("source", "/1/2/8000")
        cloud_event.__setitem__("sink", "")
        validator = Validators.REQUEST.validator()
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Invalid CloudEvent sink. RPC Request CloudEvent sink must be an uri.")

    def test_request_validator_when_type_is_wrong(self):
        cloud_event = CloudEventFactory.request(
            build_default_topic_uri_for_test(),
            build_method_uri_for_test(),
            None,
            UCloudEventAttributesBuilder().build()
        )
        cloud_event.__setitem__("source", "/1/2/8000")
        cloud_event.__setitem__("type", "pub.v1")
        validator = Validators.REQUEST.validator()
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Invalid CloudEvent type [pub.v1]. " +\
                         "CloudEvent of type Request must have a type of 'req.v1'")

    def test_response_validator_for_valid_response_type_message(self):
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_priority(UPriority.UPRIORITY_CS1)
            .with_ttl(1000)
            .build()
        )

        cloud_event = CloudEventFactory.response(
            build_default_topic_uri_for_test(),
            build_method_uri_for_test(),
            UuidSerializer().serialize(Factories.UPROTOCOL.create()),
            None,
            u_cloud_event_attributes
        )

        validator = Validators.RESPONSE.validator()
        result = validator.validate(cloud_event)
        self.assertTrue(result.is_success())

    def test_response_validator_for_invalid_sink(self):
        cloud_event = CloudEventFactory.response(
            build_default_topic_uri_for_test(),
            build_method_uri_for_test(),
            UuidSerializer().serialize(Factories.UPROTOCOL.create()),
            None,
            UCloudEventAttributesBuilder().build()
        )
        cloud_event.__setitem__("sink", "/1/2/3299")
        validator = Validators.RESPONSE.validator()
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Invalid RPC Response type CloudEvent sink [/1/2/3299].")

    def test_response_validator_for_invalid_source(self):
        cloud_event = CloudEventFactory.response(
            build_default_topic_uri_for_test(),
            build_method_uri_for_test(),
            UuidSerializer().serialize(Factories.UPROTOCOL.create()),
            None,
            UCloudEventAttributesBuilder().build()
        )
        cloud_event.__setitem__("source", "invalid-source-topic")
        validator = Validators.RESPONSE.validator()
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Invalid RPC Response type CloudEvent source [invalid-source-topic].")

    def test_response_validator_for_null_sink(self):
        cloud_event = CloudEventFactory.response(
            build_default_topic_uri_for_test(),
            build_method_uri_for_test(),
            UuidSerializer().serialize(Factories.UPROTOCOL.create()),
            None,
            UCloudEventAttributesBuilder().build()
        )
        cloud_event.__setitem__("sink", "")
        validator = Validators.RESPONSE.validator()
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Invalid CloudEvent sink. RPC Response CloudEvent sink must be an uri.")

    def test_response_validator_when_type_is_wrong(self):
        cloud_event = CloudEventFactory.response(
            build_default_topic_uri_for_test(),
            build_method_uri_for_test(),
            UuidSerializer().serialize(Factories.UPROTOCOL.create()),
            None,
            UCloudEventAttributesBuilder().build()
        )
        cloud_event.__setitem__("type", "pub.v1")
        validator = Validators.RESPONSE.validator()
        result = validator.validate(cloud_event)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Invalid CloudEvent type [pub.v1]. " +\
                         "CloudEvent of type Response must have a type of 'res.v1'")

if __name__ == "__main__":
    unittest.main()
