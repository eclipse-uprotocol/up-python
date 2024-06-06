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

from uprotocol.proto.uattributes_pb2 import UAttributes, UPriority
from uprotocol.proto.uri_pb2 import UAuthority, UEntity, UUri
from uprotocol.proto.uuid_pb2 import UUID
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.transport.validate.uattributesvalidator import (
    UAttributesValidator,
    Validators,
)
from uprotocol.uri.factory.uresourcebuilder import UResourceBuilder
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.validation.validationresult import ValidationResult


def build_sink():
    return UUri(
        authority=UAuthority(name="vcu.someVin.veh.steven.gm.com"),
        entity=UEntity(name="petapp.steven.gm.com", version_major=1),
        resource=UResourceBuilder.for_rpc_response(),
    )


def build_source():
    return UUri(
        authority=UAuthority(name="vcu.someVin.veh.steven.gm.com"),
        entity=UEntity(name="petapp.steven.gm.com", version_major=1),
        resource=UResourceBuilder.for_rpc_request(None),
    )


class TestUAttributesValidator(unittest.TestCase):
    def test_fetching_validator_for_publish_type(self):
        publish = UAttributesValidator.get_validator(
            UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).build()
        )
        self.assertEqual("UAttributesValidator.Publish", str(publish))

    def test_fetching_validator_for_request_type(self):
        request = UAttributesValidator.get_validator(
            UAttributesBuilder.request(build_source(), UUri(), UPriority.UPRIORITY_CS4, 1000).build()
        )
        self.assertEqual("UAttributesValidator.Request", str(request))

    def test_fetching_validator_for_response_type(self):
        response = UAttributesValidator.get_validator(
            UAttributesBuilder.response(
                build_source(),
                UUri(),
                UPriority.UPRIORITY_CS4,
                Factories.UPROTOCOL.create(),
            ).build()
        )
        self.assertEqual("UAttributesValidator.Response", str(response))

    def test_fetching_validator_for_notification_type(self):
        response = UAttributesValidator.get_validator(
            UAttributesBuilder.notification(build_source(), UUri(), UPriority.UPRIORITY_CS4).build()
        )
        self.assertEqual("UAttributesValidator.Notification", str(response))

    def test_fetching_validator_for_no_type(self):
        response = UAttributesValidator.get_validator(UAttributes())
        self.assertEqual("UAttributesValidator.Publish", str(response))

    def test_validate_u_attributes_for_publish_message_payload(self):
        attributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).build()
        validator = Validators.PUBLISH.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validate_u_attributes_for_publish_message_payload_alls(self):
        attributes = (
            UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0)
            .with_ttl(1000)
            .with_sink(build_sink())
            .with_permission_level(2)
            .with_comm_status(3)
            .with_req_id(Factories.UPROTOCOL.create())
            .build()
        )

        validator = Validators.PUBLISH.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validate_u_attributes_for_publish_message_payload_invalid_type(
        self,
    ):
        attributes = UAttributesBuilder.response(
            build_source(),
            build_sink(),
            UPriority.UPRIORITY_CS0,
            Factories.UPROTOCOL.create(),
        ).build()
        validator = Validators.PUBLISH.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual(
            "Wrong Attribute Type [UMESSAGE_TYPE_RESPONSE]",
            status.get_message(),
        )

    def test_validate_u_attributes_for_publish_message_payload_invalid_ttl(
        self,
    ):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_ttl(-1).build()
            self.assertTrue("Value out of range: -1" in context.exception)

    def test_validate_u_attributes_for_publish_message_payload_invalid_sink(
        self,
    ):
        attributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_sink(UUri()).build()
        validator = Validators.PUBLISH.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Uri is empty.", status.get_message())

    def test_validate_u_attributes_for_publish_message_payload_invalid_permission_level(
        self,
    ):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_permission_level(-42).build()
            self.assertTrue("Value out of range: -42" in context.exception)

    def test_validate_u_attributes_for_rpc_request_message_payload(self):
        attributes = UAttributesBuilder.request(build_source(), build_sink(), UPriority.UPRIORITY_CS4, 1000).build()
        validator = Validators.REQUEST.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validate_u_attributes_for_rpc_request_message_payload_alls(self):
        attributes = (
            UAttributesBuilder.request(build_source(), build_sink(), UPriority.UPRIORITY_CS4, 1000)
            .with_permission_level(2)
            .with_comm_status(3)
            .with_req_id(Factories.UPROTOCOL.create())
            .build()
        )

        validator = Validators.REQUEST.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validate_u_attributes_for_rpc_request_message_payload_invalid_type(
        self,
    ):
        attributes = (
            UAttributesBuilder.response(
                build_source(),
                build_sink(),
                UPriority.UPRIORITY_CS4,
                Factories.UPROTOCOL.create(),
            )
            .with_ttl(1000)
            .build()
        )

        validator = Validators.REQUEST.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual(
            "Wrong Attribute Type [UMESSAGE_TYPE_RESPONSE]",
            status.get_message(),
        )

    def test_validate_u_attributes_for_rpc_request_message_payload_invalid_ttl(
        self,
    ):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.request(build_source(), build_sink(), UPriority.UPRIORITY_CS4, -1).build()
            self.assertTrue("Value out of range: -1" in context.exception)

    def test_validate_u_attributes_for_rpc_request_message_payload_invalid_sink(
        self,
    ):
        attributes = UAttributesBuilder.request(build_source(), UUri(), UPriority.UPRIORITY_CS4, 1000).build()

        validator = Validators.REQUEST.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Uri is empty.", status.get_message())

    def test_validate_u_attributes_for_rpc_request_message_payload_invalid_permission_level(
        self,
    ):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.request(
                build_source(), build_sink(), UPriority.UPRIORITY_CS4, 1000
            ).with_permission_level(-42).build()
            self.assertTrue("Value out of range: -42" in context.exception)

    def test_validate_u_attributes_for_rpc_response_message_payload(self):
        attributes = UAttributesBuilder.response(
            build_source(),
            build_sink(),
            UPriority.UPRIORITY_CS4,
            Factories.UPROTOCOL.create(),
        ).build()

        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validate_u_attributes_for_rpc_response_message_payload_alls(self):
        attributes = (
            UAttributesBuilder.response(
                build_source(),
                build_sink(),
                UPriority.UPRIORITY_CS4,
                Factories.UPROTOCOL.create(),
            )
            .with_permission_level(2)
            .with_comm_status(3)
            .build()
        )

        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validate_u_attributes_for_rpc_response_message_payload_invalid_type(
        self,
    ):
        attributes = UAttributesBuilder.notification(build_source(), build_sink(), UPriority.UPRIORITY_CS4).build()

        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual(
            "Wrong Attribute Type [UMESSAGE_TYPE_NOTIFICATION],Missing correlationId",
            status.get_message(),
        )

    def test_validate_u_attributes_for_rpc_response_message_payload_invalid_ttl(
        self,
    ):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.response(
                build_source(),
                build_sink(),
                UPriority.UPRIORITY_CS4,
                Factories.UPROTOCOL.create(),
            ).with_ttl(-1).build()
            self.assertTrue("Value out of range: -1" in context.exception)

    def test_validate_u_attributes_for_rpc_response_message_payload_missing_sink_and_missing_request_id(
        self,
    ):
        attributes = UAttributesBuilder.response(build_source(), UUri(), UPriority.UPRIORITY_CS4, UUID()).build()

        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Missing Sink,Missing correlationId", status.get_message())

    def test_validate_u_attributes_for_rpc_response_message_payload_invalid_permission_level(
        self,
    ):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.response(
                build_source(),
                build_sink(),
                UPriority.UPRIORITY_CS4,
                Factories.UPROTOCOL.create(),
            ).with_permission_level(-42).build()
            self.assertTrue("Value out of range: -42" in context.exception)

    def test_validate_u_attributes_for_rpc_response_message_payload_missing_request_id(
        self,
    ):
        attributes = UAttributesBuilder.response(build_source(), build_sink(), UPriority.UPRIORITY_CS4, UUID()).build()

        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Missing correlationId", status.get_message())

    def test_validate_u_attributes_for_publish_message_payload_not_expired(
        self,
    ):
        attributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).build()

        validator = Validators.PUBLISH.validator()
        self.assertFalse(validator.is_expired(attributes))

    def test_validate_u_attributes_for_publish_message_payload_not_expired_with_ttl_zero(
        self,
    ):
        attributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_ttl(0).build()

        validator = Validators.PUBLISH.validator()
        self.assertFalse(validator.is_expired(attributes))

    def test_validate_u_attributes_for_publish_message_payload_not_expired_with_ttl(
        self,
    ):
        attributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_ttl(10000).build()

        validator = Validators.PUBLISH.validator()
        self.assertFalse(validator.is_expired(attributes))

    def test_validate_u_attributes_for_publish_message_payload_expired_with_ttl(
        self,
    ):
        attributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_ttl(1).build()

        time.sleep(0.8)

        validator = Validators.PUBLISH.validator()
        self.assertTrue(validator.is_expired(attributes))

    # ----

    def test_validating_publish_invalid_ttl_attribute(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_ttl(-1).build()
            self.assertTrue("Value out of range: -1" in context.exception)

    def test_validating_valid_ttl_attribute(self):
        attributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_ttl(100).build()

        validator = Validators.PUBLISH.validator()
        status = validator.validate_ttl(attributes)
        self.assertEqual(ValidationResult.success(), status)

    def test_validating_invalid_sink_attribute(self):
        uri = LongUriSerializer().deserialize("//")
        attributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_sink(uri).build()
        validator = Validators.PUBLISH.validator()
        status = validator.validate_sink(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Uri is empty.", status.get_message())

    def test_validating_valid_sink_attribute(self):
        uri = UUri(
            authority=UAuthority(name="vcu.someVin.veh.steven.gm.com"),
            entity=UEntity(name="petapp.steven.gm.com", version_major=1),
            resource=UResourceBuilder.for_rpc_response(),
        )
        attributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_sink(uri).build()

        validator = Validators.PUBLISH.validator()
        status = validator.validate_sink(attributes)
        self.assertEqual(ValidationResult.success(), status)

    def test_validating_valid_req_id_attribute(self):
        attributes = (
            UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0)
            .with_req_id(Factories.UPROTOCOL.create())
            .build()
        )

        validator = Validators.PUBLISH.validator()
        status = validator.validate_req_id(attributes)
        self.assertEqual(ValidationResult.success(), status)

    def test_validating_valid_type_attribute(self):
        attributes = (
            UAttributesBuilder.notification(build_source(), build_sink(), UPriority.UPRIORITY_CS0)
            .with_req_id(Factories.UPROTOCOL.create())
            .build()
        )

        validator = Validators.NOTIFICATION.validator()
        status = validator.validate_type(attributes)
        self.assertEqual(ValidationResult.success(), status)

    def test_validating_valid_sink_attribute(self):
        attributes = (
            UAttributesBuilder.notification(build_source(), build_sink(), UPriority.UPRIORITY_CS0)
            .with_req_id(Factories.UPROTOCOL.create())
            .build()
        )

        validator = Validators.NOTIFICATION.validator()
        status = validator.validate_sink(attributes)
        self.assertEqual(ValidationResult.success(), status)

    def test_validating_none_attribute(self):
        attributes = None

        validator = Validators.NOTIFICATION.validator()
        status = validator.validate_sink(attributes)
        self.assertEqual("UAttributes cannot be null.", status.get_message())

    def test_validating_invalid_sink_attribute(self):
        attributes = (
            UAttributesBuilder.notification(build_source(), UUri(), UPriority.UPRIORITY_CS0)
            .with_req_id(Factories.UPROTOCOL.create())
            .build()
        )

        validator = Validators.NOTIFICATION.validator()
        status = validator.validate_sink(attributes)
        self.assertEqual("Missing Sink", status.get_message())

    def test_validating_invalid_permission_level_attribute(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_permission_level(-1).build()
            self.assertTrue("Value out of range: -1" in context.exception)

    def test_validating_valid_permission_level_attribute(self):
        attributes = (
            UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_permission_level(3).build()
        )

        validator = Validators.PUBLISH.validator()
        status = validator.validate_permission_level(attributes)
        self.assertEqual(ValidationResult.success(), status)

    def test_validating_valid_permission_level_attribute_invalid(self):
        attributes = (
            UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_permission_level(0).build()
        )

        validator = Validators.PUBLISH.validator()
        status = validator.validate_permission_level(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid Permission Level", status.get_message())

    def test_validating_request_message_types(self):
        attributes = UAttributesBuilder.request(build_source(), build_sink(), UPriority.UPRIORITY_CS6, 100).build()

        validator = UAttributesValidator.get_validator(attributes)
        self.assertEqual("UAttributesValidator.Request", str(validator))
        status = validator.validate(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validating_request_validator_with_wrong_messagetype(self):
        attributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS6).build()

        validator = Validators.REQUEST.validator()
        self.assertEqual("UAttributesValidator.Request", str(validator))
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual(
            "Wrong Attribute Type [UMESSAGE_TYPE_PUBLISH],Missing TTL,Missing Sink",
            status.get_message(),
        )

    def test_validating_request_validator_with_wrong_bad_ttl(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.request(
                build_source(),
                LongUriSerializer().deserialize("/hartley/1/rpc.response"),
                UPriority.UPRIORITY_CS6,
                -1,
            ).build()
            self.assertTrue("Value out of range: -1" in context.exception)

    def test_validating_response_validator_with_wrong_bad_ttl(self):
        with self.assertRaises(ValueError) as context:
            UAttributesBuilder.response(
                build_source(),
                LongUriSerializer().deserialize("/hartley/1/rpc.response"),
                UPriority.UPRIORITY_CS6,
                Factories.UPROTOCOL.create(),
            ).with_ttl(-1).build()
            self.assertTrue("Value out of range: -1" in context.exception)

    def test_validating_publish_validator_with_wrong_messagetype(self):
        attributes = UAttributesBuilder.request(build_source(), build_sink(), UPriority.UPRIORITY_CS6, 1000).build()
        validator = Validators.PUBLISH.validator()
        self.assertEqual("UAttributesValidator.Publish", str(validator))
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual(
            "Wrong Attribute Type [UMESSAGE_TYPE_REQUEST]",
            status.get_message(),
        )

    def test_validating_response_validator_with_wrong_messagetype(self):
        attributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS6).build()

        validator = Validators.RESPONSE.validator()
        self.assertEqual("UAttributesValidator.Response", str(validator))
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual(
            "Wrong Attribute Type [UMESSAGE_TYPE_PUBLISH],Missing Sink,Missing correlationId",
            status.get_message(),
        )

    def test_validating_request_containing_token(self):
        attributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_token("null").build()

        validator = UAttributesValidator.get_validator(attributes)
        self.assertEqual("UAttributesValidator.Publish", str(validator))
        status = validator.validate(attributes)
        self.assertEqual(ValidationResult.success(), status)

    def test_valid_request_methoduri_in_sink(self):
        sink = LongUriSerializer().deserialize("/test.service/1/rpc.method")
        attributes = UAttributesBuilder.request(build_source(), sink, UPriority.UPRIORITY_CS0, 3000).build()
        validator = UAttributesValidator.get_validator(attributes)
        self.assertEqual("UAttributesValidator.Request", str(validator))
        status = validator.validate(attributes)
        self.assertEqual(ValidationResult.success(), status)

    def test_invalid_request_methoduri_in_sink(self):
        sink = LongUriSerializer().deserialize("/test.client/1/test.response")
        attributes = UAttributesBuilder.request(build_source(), sink, UPriority.UPRIORITY_CS0, 3000).build()
        validator = UAttributesValidator.get_validator(attributes)
        self.assertEqual("UAttributesValidator.Request", str(validator))
        status = validator.validate(attributes)
        self.assertEqual(
            "Invalid RPC method uri. Uri should be the method to be called, or method from response.",
            status.get_message(),
        )

    def test_valid_response_uri_in_sink(self):
        sink = LongUriSerializer().deserialize("/test.client/1/rpc.response")
        attributes = UAttributesBuilder.response(
            build_source(),
            sink,
            UPriority.UPRIORITY_CS0,
            Factories.UPROTOCOL.create(),
        ).build()
        validator = UAttributesValidator.get_validator(attributes)
        self.assertEqual("UAttributesValidator.Response", str(validator))
        status = validator.validate(attributes)
        self.assertEqual(ValidationResult.success(), status)

    def test_invalid_response_uri_in_sink(self):
        sink = LongUriSerializer().deserialize("/test.client/1/rpc.method")
        attributes = UAttributesBuilder.response(
            build_source(),
            sink,
            UPriority.UPRIORITY_CS0,
            Factories.UPROTOCOL.create(),
        ).build()
        validator = UAttributesValidator.get_validator(attributes)
        self.assertEqual("UAttributesValidator.Response", str(validator))
        status = validator.validate(attributes)
        self.assertEqual("Invalid RPC response type.", status.get_message())

    def test_publish_validation_without_id(self):
        attributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).build()
        attributes.ClearField("id")
        validator = Validators.PUBLISH.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Missing id", status.get_message())

    def test_notification_validation_without_id(self):
        attributes = UAttributesBuilder.notification(build_source(), build_sink(), UPriority.UPRIORITY_CS0).build()
        attributes.ClearField("id")
        validator = Validators.NOTIFICATION.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Missing id", status.get_message())

    def test_request_validation_without_id(self):
        attributes = UAttributesBuilder.request(build_source(), build_sink(), UPriority.UPRIORITY_CS0, 1000).build()
        attributes.ClearField("id")
        validator = Validators.REQUEST.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Missing id", status.get_message())

    def test_response_validation_without_id(self):
        attributes = UAttributesBuilder.response(
            build_source(),
            build_sink(),
            UPriority.UPRIORITY_CS0,
            Factories.UPROTOCOL.create(),
        ).build()
        attributes.ClearField("id")
        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Missing id", status.get_message())

    def test_publish_validation_invalid_id(self):
        attributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).build()
        attributes.id.CopyFrom(UUID())
        validator = Validators.PUBLISH.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual(
            "Attributes must contain valid uProtocol UUID in id property",
            status.get_message(),
        )

    def test_notification_validation_invalid_id(self):
        attributes = UAttributesBuilder.notification(build_source(), build_sink(), UPriority.UPRIORITY_CS0).build()
        attributes.id.CopyFrom(UUID())
        validator = Validators.NOTIFICATION.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual(
            "Attributes must contain valid uProtocol UUID in id property",
            status.get_message(),
        )

    def test_request_validation_invalid_id(self):
        attributes = UAttributesBuilder.request(build_source(), build_sink(), UPriority.UPRIORITY_CS0, 1000).build()
        attributes.id.CopyFrom(UUID())
        validator = Validators.REQUEST.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual(
            "Attributes must contain valid uProtocol UUID in id property",
            status.get_message(),
        )

    def test_response_validation_invalid_id(self):
        attributes = UAttributesBuilder.response(
            build_source(),
            build_sink(),
            UPriority.UPRIORITY_CS0,
            Factories.UPROTOCOL.create(),
        ).build()
        attributes.id.CopyFrom(UUID())
        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual(
            "Attributes must contain valid uProtocol UUID in id property",
            status.get_message(),
        )

    def test_publish_validation_when_an_invalid_priority(self):
        attributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_UNSPECIFIED).build()
        validator = Validators.PUBLISH.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid UPriority [UPRIORITY_UNSPECIFIED]", status.get_message())

    def test_request_validation_with_invalid_priority(self):
        attributes = UAttributesBuilder.request(
            build_source(), build_sink(), UPriority.UPRIORITY_UNSPECIFIED, 1000
        ).build()
        validator = Validators.REQUEST.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid UPriority [UPRIORITY_UNSPECIFIED]", status.get_message())

    def test_response_validation_with_invalid_priority(self):
        attributes = UAttributesBuilder.response(
            build_source(),
            build_sink(),
            UPriority.UPRIORITY_UNSPECIFIED,
            Factories.UPROTOCOL.create(),
        ).build()
        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid UPriority [UPRIORITY_UNSPECIFIED]", status.get_message())


if __name__ == "__main__":
    unittest.main()
