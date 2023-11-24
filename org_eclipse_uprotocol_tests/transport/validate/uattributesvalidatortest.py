# -------------------------------------------------------------------------
#
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
#
# -------------------------------------------------------------------------

import time
import unittest

from org_eclipse_uprotocol.proto.uattributes_pb2 import UPriority
from org_eclipse_uprotocol.proto.uri_pb2 import UUri, UAuthority, UEntity
from org_eclipse_uprotocol.proto.ustatus_pb2 import UCode
from org_eclipse_uprotocol.proto.uuid_pb2 import UUID
from org_eclipse_uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from org_eclipse_uprotocol.transport.validate.uattributesvalidator import UAttributesValidator, Validators
from org_eclipse_uprotocol.uri.builder.uresource_builder import UResourceBuilder
from org_eclipse_uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from org_eclipse_uprotocol.uuid.factory.uuidfactory import Factories
from org_eclipse_uprotocol.validation.validationresult import ValidationResult


def build_sink():
    return UUri(authority=UAuthority(name="vcu.someVin.veh.ultifi.gm.com"),
                entity=UEntity(name="petapp.ultifi.gm.com", version_major=1),
                resource=UResourceBuilder.for_rpc_response())


class UAttributesValidatorTest(unittest.TestCase):

    def test_fetching_validator_for_valid_types(self):
        publish = UAttributesValidator.get_validator(UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).build())
        self.assertEqual("UAttributesValidator.Publish", str(publish))

        request = UAttributesValidator.get_validator(
            UAttributesBuilder.request(UPriority.UPRIORITY_CS4, UUri(), 1000).build())
        self.assertEqual("UAttributesValidator.Request", str(request))

        response = UAttributesValidator.get_validator(
            UAttributesBuilder.response(UPriority.UPRIORITY_CS4, UUri(), Factories.UPROTOCOL.create()).build())
        self.assertEqual("UAttributesValidator.Response", str(response))

    def test_validate_uAttributes_for_publish_message_payload(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).build()
        validator = Validators.PUBLISH.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validate_uAttributes_for_publish_message_payload_alls(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withTtl(1000).withSink(
            build_sink()).withPermissionLevel(2).withCommStatus(3).withReqId(Factories.UPROTOCOL.create()).build()

        validator = Validators.PUBLISH.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validate_uAttributes_for_publish_message_payload_invalid_type(self):
        attributes = UAttributesBuilder.response(UPriority.UPRIORITY_CS0, build_sink(),
                                                 Factories.UPROTOCOL.create()).build()
        validator = Validators.PUBLISH.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Wrong Attribute Type [UMESSAGE_TYPE_RESPONSE]", status.get_message())

    def test_validate_uAttributes_for_publish_message_payload_invalid_ttl(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withTtl(-1).build()

        validator = Validators.PUBLISH.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid TTL [-1]", status.get_message())

    def test_validate_uAttributes_for_publish_message_payload_invalid_sink(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withSink(UUri()).build()
        validator = Validators.PUBLISH.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Uri is empty.", status.get_message())

    def test_validate_uAttributes_for_publish_message_payload_invalid_permission_level(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withPermissionLevel(-42).build()
        validator = Validators.PUBLISH.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid Permission Level", status.get_message())

    def test_validate_uAttributes_for_publish_message_payload_invalid_communication_status(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withCommStatus(-42).build()
        validator = Validators.PUBLISH.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid Communication Status Code", status.get_message())

    # def test_validate_uAttributes_for_publish_message_payload_invalid_request_id(self):
    #     uuid = java.util.UUID.randomUUID()
    #     attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withReqId(
    #         UUID.newBuilder().setMsb(uuid_java.getMostSignificantBits()).setLsb(uuid_java.getLeastSignificantBits())
    #         .build()).build()
    #
    #     validator = Validators.PUBLISH.validator()
    #     status = validator.validate(attributes)
    #     self.assertTrue(status.is_failure())
    #     self.assertEqual("Invalid UUID", status.get_message())

    def test_validate_uAttributes_for_rpc_request_message_payload(self):
        attributes = UAttributesBuilder.request(UPriority.UPRIORITY_CS4, build_sink(), 1000).build()
        validator = Validators.REQUEST.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validate_uAttributes_for_rpc_request_message_payload_alls(self):
        attributes = UAttributesBuilder.request(UPriority.UPRIORITY_CS4, build_sink(), 1000).withPermissionLevel(
            2).withCommStatus(3).withReqId(Factories.UPROTOCOL.create()).build()

        validator = Validators.REQUEST.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validate_uAttributes_for_rpc_request_message_payload_invalid_type(self):
        attributes = UAttributesBuilder.response(UPriority.UPRIORITY_CS4, build_sink(),
                                                 Factories.UPROTOCOL.create()).withTtl(1000).build()

        validator = Validators.REQUEST.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Wrong Attribute Type [UMESSAGE_TYPE_RESPONSE]", status.get_message())

    def test_validate_uAttributes_for_rpc_request_message_payload_invalid_ttl(self):
        attributes = UAttributesBuilder.request(UPriority.UPRIORITY_CS4, build_sink(), -1).build()

        validator = Validators.REQUEST.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid TTL [-1]", status.get_message())

    def test_validate_uAttributes_for_rpc_request_message_payload_invalid_sink(self):
        attributes = UAttributesBuilder.request(UPriority.UPRIORITY_CS4, UUri(), 1000).build()

        validator = Validators.REQUEST.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Uri is empty.", status.get_message())

    def test_validate_uAttributes_for_rpc_request_message_payload_invalid_permission_level(self):
        attributes = UAttributesBuilder.request(UPriority.UPRIORITY_CS4, build_sink(), 1000).withPermissionLevel(
            -42).build()

        validator = Validators.REQUEST.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid Permission Level", status.get_message())

    def test_validate_uAttributes_for_rpc_request_message_payload_invalid_communication_status(self):
        attributes = UAttributesBuilder.request(UPriority.UPRIORITY_CS4, build_sink(), 1000).withCommStatus(-42).build()

        validator = Validators.REQUEST.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid Communication Status Code", status.get_message())

    # def test_validate_uAttributes_for_rpc_request_message_payload_invalid_request_id(self):
    #     uuid_java = java.util.UUID.randomUUID()
    #     attributes = UAttributesBuilder.request(UPriority.UPRIORITY_CS4, build_sink(), 1000).withReqId(
    #         UUID.newBuilder().setMsb(uuid_java.getMostSignificantBits()).setLsb(uuid_java.getLeastSignificantBits())
    #         .build()).build()
    #
    #     validator = Validators.REQUEST.validator()
    #     status = validator.validate(attributes)
    #     self.assertTrue(status.is_failure())
    #     self.assertEqual("Invalid UUID", status.get_message())

    def test_validate_uAttributes_for_rpc_response_message_payload(self):
        attributes = UAttributesBuilder.response(UPriority.UPRIORITY_CS4, build_sink(),
                                                 Factories.UPROTOCOL.create()).build()

        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validate_uAttributes_for_rpc_response_message_payload_alls(self):
        attributes = UAttributesBuilder.response(UPriority.UPRIORITY_CS4, build_sink(),
                                                 Factories.UPROTOCOL.create()).withPermissionLevel(2).withCommStatus(
            3).build()

        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validate_uAttributes_for_rpc_response_message_payload_invalid_type(self):
        attributes = UAttributesBuilder.notification(UPriority.UPRIORITY_CS4, build_sink()).build()

        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Wrong Attribute Type [UMESSAGE_TYPE_PUBLISH],Missing correlationId", status.get_message())

    def test_validate_uAttributes_for_rpc_response_message_payload_invalid_ttl(self):
        attributes = UAttributesBuilder.response(UPriority.UPRIORITY_CS4, build_sink(),
                                                 Factories.UPROTOCOL.create()).withTtl(-1).build()

        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid TTL [-1]", status.get_message())

    def test_validate_uAttributes_for_rpc_response_message_payload_missing_sink_and_missing_requestId(self):
        attributes = UAttributesBuilder.response(UPriority.UPRIORITY_CS4, UUri(), UUID()).build()

        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Missing Sink,Missing correlationId", status.get_message())

    def test_validate_uAttributes_for_rpc_response_message_payload_invalid_permission_level(self):
        attributes = UAttributesBuilder.response(UPriority.UPRIORITY_CS4, build_sink(),
                                                 Factories.UPROTOCOL.create()).withPermissionLevel(-42).build()

        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid Permission Level", status.get_message())

    def test_validate_uAttributes_for_rpc_response_message_payload_invalid_communication_status(self):
        attributes = UAttributesBuilder.response(UPriority.UPRIORITY_CS4, build_sink(),
                                                 Factories.UPROTOCOL.create()).withCommStatus(-42).build()

        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid Communication Status Code", status.get_message())

    def test_validate_uAttributes_for_rpc_response_message_payload_missing_request_id(self):
        attributes = UAttributesBuilder.response(UPriority.UPRIORITY_CS4, build_sink(), UUID()).build()

        validator = Validators.RESPONSE.validator()
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Missing correlationId", status.get_message())

    # def test_validate_uAttributes_for_rpc_response_message_payload_invalid_request_id(self):
    #     uuid_java = java.util.UUID.randomUUID()
    #     reqid = UUID.newBuilder().setMsb(uuid_java.getMostSignificantBits()).setLsb(
    #         uuid_java.getLeastSignificantBits()).build()
    #     attributes = UAttributesBuilder.response(UPriority.UPRIORITY_CS4, build_sink(), reqid).build()
    #
    #     validator = Validators.RESPONSE.validator()
    #     status = validator.validate(attributes)
    #     self.assertTrue(status.is_failure())
    #     self.assertEqual(f"Invalid correlationId [{reqid}]", status.get_message())

    # ----
    def test_validate_uAttributes_for_publish_message_payload_not_expired(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).build()

        validator = Validators.PUBLISH.validator()
        status = validator.is_expired(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validate_uAttributes_for_publish_message_payload_not_expired_withTtl_zero(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withTtl(0).build()

        validator = Validators.PUBLISH.validator()
        status = validator.is_expired(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validate_uAttributes_for_publish_message_payload_not_expired_withTtl(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withTtl(10000).build()

        validator = Validators.PUBLISH.validator()
        status = validator.is_expired(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validate_uAttributes_for_publish_message_payload_expired_withTtl(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withTtl(1).build()

        time.sleep(0.8)

        validator = Validators.PUBLISH.validator()
        status = validator.is_expired(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Payload is expired", status.get_message())

    # ----

    def test_validating_publish_invalid_ttl_attribute(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withTtl(-1).build()

        validator = Validators.PUBLISH.validator()
        status = validator.validate_ttl(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid TTL [-1]", status.get_message())

    def test_validating_valid_ttl_attribute(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withTtl(100).build()

        validator = Validators.PUBLISH.validator()
        status = validator.validate_ttl(attributes)
        self.assertEqual(ValidationResult.success(), status)

    def test_validating_invalid_sink_attribute(self):
        uri = LongUriSerializer().deserialize("//")
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withSink(uri).build()
        validator = Validators.PUBLISH.validator()
        status = validator.validate_sink(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Uri is empty.", status.get_message())

    def test_validating_valid_sink_attribute(self):
        uri = UUri(authority=UAuthority(name="vcu.someVin.veh.ultifi.gm.com"),
                   entity=UEntity(name="petapp.ultifi.gm.com", version_major=1),
                   resource=UResourceBuilder.for_rpc_response())
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withSink(uri).build()

        validator = Validators.PUBLISH.validator()
        status = validator.validate_sink(attributes)
        self.assertEqual(ValidationResult.success(), status)

    # def test_validating_invalid_ReqId_attribute(self):
    #     uuid_java = java.util.UUID.randomUUID()
    #
    #     attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).with_req_id(
    #         UUID.newBuilder().setMsb(uuid_java.getMostSignificantBits()).setLsb(uuid_java.getLeastSignificantBits())
    #         .build()).build()
    #
    #     validator = Validators.PUBLISH.validator()
    #     status = validator.validate_req_id(attributes)
    #     self.assertTrue(status.is_failure())
    #     self.assertEqual("Invalid UUID", status.get_message())

    def test_validating_valid_ReqId_attribute(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withReqId(
            Factories.UPROTOCOL.create()).build()

        validator = Validators.PUBLISH.validator()
        status = validator.validate_req_id(attributes)
        self.assertEqual(ValidationResult.success(), status)

    def test_validating_invalid_PermissionLevel_attribute(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withPermissionLevel(-1).build()

        validator = Validators.PUBLISH.validator()
        status = validator.validate_permission_level(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid Permission Level", status.get_message())

    def test_validating_valid_PermissionLevel_attribute(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withPermissionLevel(3).build()

        validator = Validators.PUBLISH.validator()
        status = validator.validate_permission_level(attributes)
        self.assertEqual(ValidationResult.success(), status)

    def test_validating_valid_PermissionLevel_attribute_invalid(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withPermissionLevel(0).build()

        validator = Validators.PUBLISH.validator()
        status = validator.validate_permission_level(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid Permission Level", status.get_message())

    def test_validating_invalid_commstatus_attribute(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withCommStatus(100).build()

        validator = Validators.PUBLISH.validator()
        status = validator.validate_comm_status(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid Communication Status Code", status.get_message())

    def test_validating_valid_commstatus_attribute(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withCommStatus(UCode.ABORTED).build()

        validator = Validators.PUBLISH.validator()
        status = validator.validate_comm_status(attributes)
        self.assertEqual(ValidationResult.success(), status)

    def test_validating_request_message_types(self):
        attributes = UAttributesBuilder.request(UPriority.UPRIORITY_CS6, build_sink(), 100).build()

        validator = UAttributesValidator.get_validator(attributes)
        self.assertEqual("UAttributesValidator.Request", str(validator))
        status = validator.validate(attributes)
        self.assertTrue(status.is_success())
        self.assertEqual("", status.get_message())

    def test_validating_request_validator_with_wrong_messagetype(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS6).build()

        validator = Validators.REQUEST.validator()
        self.assertEqual("UAttributesValidator.Request", str(validator))
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Wrong Attribute Type [UMESSAGE_TYPE_PUBLISH],Missing TTL,Missing Sink", status.get_message())

    def test_validating_request_validator_with_wrong_bad_ttl(self):
        attributes = UAttributesBuilder.request(UPriority.UPRIORITY_CS6,
                                                LongUriSerializer().deserialize("/hartley/1/rpc.response"), -1).build()

        validator = Validators.REQUEST.validator()
        self.assertEqual("UAttributesValidator.Request", str(validator))
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid TTL [-1]", status.get_message())

    def test_validating_response_validator_with_wrong_bad_ttl(self):
        attributes = UAttributesBuilder.response(UPriority.UPRIORITY_CS6,
                                                 LongUriSerializer().deserialize("/hartley/1/rpc.response"),
                                                 Factories.UPROTOCOL.create()).withTtl(-1).build()

        validator = Validators.RESPONSE.validator()
        self.assertEqual("UAttributesValidator.Response", str(validator))
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid TTL [-1]", status.get_message())

    def test_validating_publish_validator_with_wrong_messagetype(self):
        attributes = UAttributesBuilder.request(UPriority.UPRIORITY_CS6, build_sink(), 1000).build()
        validator = Validators.PUBLISH.validator()
        self.assertEqual("UAttributesValidator.Publish", str(validator))
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Wrong Attribute Type [UMESSAGE_TYPE_REQUEST]", status.get_message())

    def test_validating_response_validator_with_wrong_messagetype(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS6).build()

        validator = Validators.RESPONSE.validator()
        self.assertEqual("UAttributesValidator.Response", str(validator))
        status = validator.validate(attributes)
        self.assertTrue(status.is_failure())
        self.assertEqual("Wrong Attribute Type [UMESSAGE_TYPE_PUBLISH],Missing Sink,Missing correlationId",
                         status.get_message())

    def test_validating_request_containing_token(self):
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS0).withToken("null").build()

        validator = UAttributesValidator.get_validator(attributes)
        self.assertEqual("UAttributesValidator.Publish", str(validator))
        status = validator.validate(attributes)
        self.assertEqual(ValidationResult.success(), status)


if __name__ == '__main__':
    unittest.main()
