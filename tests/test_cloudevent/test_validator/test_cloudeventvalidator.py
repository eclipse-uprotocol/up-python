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


def build_base_publish_cloud_event_for_test():
    # uri
    source = build_long_uri_for_test()

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
        proto_payload.SerializeToString(),
        proto_payload.type_url,
        u_cloud_event_attributes,
        UCloudEvent.get_event_type(UMessageType.UMESSAGE_TYPE_PUBLISH),
    )
    return cloud_event

    pass


def build_base_notification_cloud_event_for_test():
    # uri
    source = build_long_uri_for_test()

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
        proto_payload.SerializeToString(),
        proto_payload.type_url,
        u_cloud_event_attributes,
        UCloudEvent.get_event_type(UMessageType.UMESSAGE_TYPE_NOTIFICATION),
    )
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
    return UUri(ue_id=12345, resource_id=531)


def build_long_uri_for_test():
    return UriSerializer().serialize(build_uuri_for_test())


class TestCloudEventValidator(unittest.TestCase):

    def test_create_a_v6_cloudevent_and_validate_it_against_sdk(self):
        source = build_long_uri_for_test()
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
            proto_payload.SerializeToString(),
            proto_payload.type_url,
            u_cloud_event_attributes,
            UCloudEvent.get_event_type(UMessageType.UMESSAGE_TYPE_PUBLISH),
        )
        validator = Validators.PUBLISH.validator()
        result = validator.validate(cloud_event)
        self.assertTrue(result.is_success())
        self.assertFalse(UCloudEvent.is_expired(cloud_event))

    def test_fetching_the_notification_validator(self):
        cloud_event = build_base_notification_cloud_event_for_test()
        validator = CloudEventValidator.get_validator(cloud_event)
        status = validator.validate_type(cloud_event).to_status()
        self.assertEqual(status, ValidationResult.STATUS_SUCCESS)
        self.assertEqual("CloudEventValidator.Notification", str(validator))
