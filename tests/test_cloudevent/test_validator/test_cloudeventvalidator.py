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

from uprotocol.cloudevent.datamodel.ucloudeventattributes import UCloudEventAttributesBuilder
from uprotocol.cloudevent.factory.cloudeventfactory import CloudEventFactory
from uprotocol.cloudevent.factory.ucloudevent import UCloudEvent
from uprotocol.cloudevent.validate.cloudeventvalidator import CloudEventValidator, Validators
from uprotocol.cloudevent.cloudevents_pb2 import CloudEvent
from uprotocol.proto.uattributes_pb2 import UPriority, UMessageType
from uprotocol.proto.uri_pb2 import UUri, UEntity, UResource
from uprotocol.proto.ustatus_pb2 import UCode
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.uuid.serializer.longuuidserializer import LongUuidSerializer
from uprotocol.validation.validationresult import ValidationResult


def build_base_cloud_event_for_test():
    # uri
    source = build_long_uri_for_test()

    # fake payload
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

    pass


def build_proto_payload_for_test():
    ce_proto = CloudEvent(spec_version="1.0", source="https://example.com", id="hello", type="example.demo",
                          proto_data=any_pb2.Any())

    any_obj = any_pb2.Any()
    any_obj.Pack(ce_proto)
    return any_obj


def build_uuri_for_test():
    return UUri(entity=UEntity(name="body.access"),
                resource=UResource(name="door", instance="front_left", message="Door"))


def build_long_uri_for_test():
    return LongUriSerializer().serialize(build_uuri_for_test())


class TestCloudEventValidator(unittest.TestCase):

    def test_get_a_publish_cloud_event_validator(self):
        cloud_event = build_base_cloud_event_for_test()
        validator = CloudEventValidator.get_validator(cloud_event)
        status = validator.validate_type(cloud_event).to_status()
        self.assertEqual(status, ValidationResult.STATUS_SUCCESS)
        self.assertEqual("CloudEventValidator.Publish", str(validator))

    def test_get_a_notification_cloud_event_validator(self):
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("sink", "//bo.cloud/petapp")
        validator = Validators.NOTIFICATION.validator()
        status = validator.validate_type(cloud_event).to_status()
        self.assertEqual(status, ValidationResult.STATUS_SUCCESS)
        self.assertEqual("CloudEventValidator.Notification", str(validator))

    def test_publish_cloud_event_type(self):
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("type", "res.v1")
        validator = Validators.PUBLISH.validator()
        status = validator.validate_type(cloud_event).to_status()
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)
        self.assertEqual("Invalid CloudEvent type [res.v1]. CloudEvent of type Publish must have a type of 'pub.v1'",
                          status.message)

    def test_notification_cloud_event_type(self):
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("type", "res.v1")
        validator = Validators.NOTIFICATION.validator()
        status = validator.validate_type(cloud_event).to_status()
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)
        self.assertEqual("Invalid CloudEvent type [res.v1]. CloudEvent of type Publish must have a type of 'pub.v1'",
                          status.message)

    def test_get_a_request_cloud_event_validator(self):
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("type", "req.v1")
        validator = CloudEventValidator.get_validator(cloud_event)
        status = validator.validate_type(cloud_event).to_status()
        self.assertEqual(status, ValidationResult.STATUS_SUCCESS)
        self.assertEqual("CloudEventValidator.Request", str(validator))

    def test_request_cloud_event_type(self):
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("type", "pub.v1")
        validator = Validators.REQUEST.validator()
        status = validator.validate_type(cloud_event).to_status()
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)
        self.assertEqual("Invalid CloudEvent type [pub.v1]. CloudEvent of type Request must have a type of 'req.v1'",
                          status.message)

    def test_get_a_response_cloud_event_validator(self):
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("type", "res.v1")
        validator = CloudEventValidator.get_validator(cloud_event)
        status = validator.validate_type(cloud_event).to_status()
        self.assertEqual(status, ValidationResult.STATUS_SUCCESS)
        self.assertEqual("CloudEventValidator.Response", str(validator))

    def test_response_cloud_event_type(self):
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("type", "pub.v1")
        validator = Validators.RESPONSE.validator()
        status = validator.validate_type(cloud_event).to_status()
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)
        self.assertEqual("Invalid CloudEvent type [pub.v1]. CloudEvent of type Response must have a type of 'res.v1'",
                          status.message)

    def test_get_a_publish_cloud_event_validator_when_cloud_event_type_is_unknown(self):
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("type", "lala.v1")
        validator = CloudEventValidator.get_validator(cloud_event)
        status = validator.validate_type(cloud_event).to_status()
        self.assertEqual("CloudEventValidator.Publish", str(validator))

    def test_validate_cloud_event_version_when_valid(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("type", "pub.v1")
        cloud_event.__setitem__("id", str_uuid)
        status = CloudEventValidator.validate_version(cloud_event).to_status()
        self.assertEqual(status, ValidationResult.STATUS_SUCCESS)

    def test_validate_cloud_event_version_when_not_valid(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("specversion", "0.3")
        cloud_event.__setitem__("id", str_uuid)
        status = CloudEventValidator.validate_version(cloud_event).to_status()
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)
        self.assertEqual("Invalid CloudEvent version [0.3]. CloudEvent version must be 1.0.", status.message)

    def test_validate_cloud_event_id_when_valid(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "pub.v1")
        status = CloudEventValidator.validate_version(cloud_event).to_status()
        self.assertEqual(status, ValidationResult.STATUS_SUCCESS)

    def test_validate_cloud_event_id_when_not_uuidv8_type_id(self):
        str_uuid = "1dd9200c-d41b-4658-8102-3101f0b91378"
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "pub.v1")
        status = CloudEventValidator.validate_id(cloud_event).to_status()
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)
        self.assertEqual("Invalid CloudEvent Id [" + str_uuid + "]. CloudEvent Id must be of type UUIDv8.",
                          status.message)

    def test_validate_cloud_event_id_when_not_valid(self):
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", "testme")
        cloud_event.__setitem__("type", "pub.v1")
        status = CloudEventValidator.validate_id(cloud_event).to_status()
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)
        self.assertEqual("Invalid CloudEvent Id [testme]. CloudEvent Id must be of type UUIDv8.", status.message)

    def test_publish_type_cloudevent_is_valid_when_everything_is_valid_local(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "pub.v1")
        cloud_event.__setitem__("source", "/body.access/1/door.front_left#Door")
        validator = Validators.PUBLISH.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(ValidationResult.success(), result)

    def test_publish_type_cloudevent_is_valid_when_everything_is_valid_remote(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "pub.v1")
        cloud_event.__setitem__("source", "//VCU.myvin/body.access/1/door.front_left#Door")
        validator = Validators.PUBLISH.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(ValidationResult.success(), result)

    def test_publish_type_cloudevent_is_valid_when_everything_is_valid_remote_with_a_sink(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "pub.v1")
        cloud_event.__setitem__("source", "//VCU.myvin/body.access/1/door.front_left#Door")
        cloud_event.__setitem__("sink", "//bo.cloud/petapp")
        validator = Validators.PUBLISH.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(ValidationResult.success(), result)

    def test_publish_type_cloudevent_is_not_valid_when_remote_with_invalid_sink(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "pub.v1")
        cloud_event.__setitem__("source", "//VCU.myvin/body.access/1/door.front_left#Door")
        cloud_event.__setitem__("sink", "//bo.cloud")
        validator = Validators.PUBLISH.validator()
        result = validator.validate(cloud_event)
        self.assertEqual("Invalid CloudEvent sink [//bo.cloud]. Uri is missing uSoftware Entity name.",
                          result.get_message())

    def test_publish_type_cloudevent_is_not_valid_when_source_is_empty(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("source", "/")
        validator = Validators.PUBLISH.validator()
        result = validator.validate(cloud_event)
        self.assertEqual("Invalid Publish type CloudEvent source [/]. Uri is empty.", result.get_message())

    def test_publish_type_cloudevent_is_not_valid_when_source_is_missing_authority(self):
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", "testme")
        cloud_event.__setitem__("type", "pub.v1")
        cloud_event.__setitem__("source", "/body.access")
        validator = Validators.PUBLISH.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(
            "Invalid CloudEvent Id [testme]. CloudEvent Id must be of type UUIDv8.," + "Invalid Publish type " +
            "CloudEvent source [/body.access]. UriPart is missing uResource name.",
            result.get_message())

    def test_publish_type_cloudevent_is_not_valid_when_source_is_missing_message_info(self):
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", "testme")
        cloud_event.__setitem__("type", "pub.v1")
        cloud_event.__setitem__("source", "/body.access/1/door.front_left")
        validator = Validators.PUBLISH.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(
            "Invalid CloudEvent Id [testme]. CloudEvent Id must be of type UUIDv8.," + "Invalid Publish type " +
            "CloudEvent source [/body.access/1/door.front_left]. UriPart is missing Message information.",
            result.get_message())

    def test_notification_type_cloudevent_is_valid_when_everything_is_valid(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "pub.v1")
        cloud_event.__setitem__("source", "/body.access/1/door.front_left#Door")
        cloud_event.__setitem__("sink", "//bo.cloud/petapp")
        validator = Validators.NOTIFICATION.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(ValidationResult.success(), result)

    def test_notification_type_cloudevent_is_not_valid_missing_sink(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "pub.v1")
        cloud_event.__setitem__("source", "/body.access/1/door.front_left#Door")
        validator = Validators.NOTIFICATION.validator()
        result = validator.validate(cloud_event)
        self.assertEqual("Invalid CloudEvent sink. Notification CloudEvent sink must be an  uri.",
                          result.get_message())

    def test_notification_type_cloudevent_is_not_valid_invalid_sink(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "pub.v1")
        cloud_event.__setitem__("sink", "//bo.cloud")
        cloud_event.__setitem__("source", "/body.access/1/door.front_left#Door")
        validator = Validators.NOTIFICATION.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(
            "Invalid Notification type CloudEvent sink [//bo.cloud]. Uri is missing uSoftware Entity name.",
            result.get_message())

    def test_request_type_cloudevent_is_valid_when_everything_is_valid(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "req.v1")
        cloud_event.__setitem__("sink", "//VCU.myvin/body.access/1/rpc.UpdateDoor")
        cloud_event.__setitem__("source", "//bo.cloud/petapp//rpc.response")
        validator = Validators.REQUEST.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(ValidationResult.success(), result)

    def test_request_type_cloudevent_is_not_valid_invalid_source(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "req.v1")
        cloud_event.__setitem__("sink", "//VCU.myvin/body.access/1/rpc.UpdateDoor")
        cloud_event.__setitem__("source", "//bo.cloud/petapp//dog")
        validator = Validators.REQUEST.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(
            "Invalid RPC Request CloudEvent source [//bo.cloud/petapp//dog]. " + "Invalid RPC uri application " +
            "response topic. UriPart is missing rpc.response.",
            result.get_message())

    def test_request_type_cloudevent_is_not_valid_missing_sink(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "req.v1")
        cloud_event.__setitem__("source", "//bo.cloud/petapp//rpc.response")
        validator = Validators.REQUEST.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(
            "Invalid RPC Request CloudEvent sink. Request CloudEvent sink must be uri for the method to be called.",
            result.get_message())

    def test_request_type_cloudevent_is_not_valid_invalid_sink_not_rpc_command(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "req.v1")
        cloud_event.__setitem__("source", "//bo.cloud/petapp//rpc.response")
        cloud_event.__setitem__("sink", "//VCU.myvin/body.access/1/UpdateDoor")
        validator = Validators.REQUEST.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(
            "Invalid RPC Request CloudEvent sink [//VCU.myvin/body.access/1/UpdateDoor]. " + "Invalid RPC method " +
            "uri. UriPart should be the method to be called, or method from response.",
            result.get_message())

    def test_response_type_cloudevent_is_valid_when_everything_is_valid(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "res.v1")
        cloud_event.__setitem__("sink", "//bo.cloud/petapp//rpc.response")
        cloud_event.__setitem__("source", "//VCU.myvin/body.access/1/rpc.UpdateDoor")
        validator = Validators.RESPONSE.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(ValidationResult.success(), result)

    def test_response_type_cloudevent_is_not_valid_invalid_source(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "res.v1")
        cloud_event.__setitem__("sink", "//bo.cloud/petapp//rpc.response")
        cloud_event.__setitem__("source", "//VCU.myvin/body.access/1/UpdateDoor")
        validator = Validators.RESPONSE.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(
            "Invalid RPC Response CloudEvent source [//VCU.myvin/body.access/1/UpdateDoor]. " + "Invalid RPC " +
            "method uri. UriPart should be the method to be called, or method from response.",
            result.get_message())

    def test_response_type_cloudevent_is_not_valid_missing_sink_and_invalid_source(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "res.v1")
        cloud_event.__setitem__("source", "//VCU.myvin/body.access/1/UpdateDoor")
        validator = Validators.RESPONSE.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(
            "Invalid RPC Response CloudEvent source [//VCU.myvin/body.access/1/UpdateDoor]. " + "Invalid RPC " +
            "method uri. UriPart should be the method to be called, or method from response.," + "Invalid" + " CloudEvent sink. Response CloudEvent sink must be uri the destination of the response.",
            result.get_message())

    def test_response_type_cloudevent_is_not_valid_invalid_sink(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "res.v1")
        cloud_event.__setitem__("sink", "//bo.cloud")
        cloud_event.__setitem__("source", "//VCU.myvin")
        validator = Validators.RESPONSE.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(
            "Invalid RPC Response CloudEvent source [//VCU.myvin]. Invalid RPC method uri. Uri is missing " +
            "uSoftware Entity name.,Invalid RPC Response CloudEvent sink [//bo.cloud]. Invalid RPC uri " +
            "application response topic. Uri is missing uSoftware Entity name.",
            result.get_message())

    def test_response_type_cloudevent_is_not_valid_invalid_source_not_rpc_command(self):
        uuid = Factories.UPROTOCOL.create()
        str_uuid = LongUuidSerializer.instance().serialize(uuid)
        cloud_event = build_base_cloud_event_for_test()
        cloud_event.__setitem__("id", str_uuid)
        cloud_event.__setitem__("type", "res.v1")
        cloud_event.__setitem__("source", "//bo.cloud/petapp/1/dog")
        cloud_event.__setitem__("sink", "//VCU.myvin/body.access/1/UpdateDoor")
        validator = Validators.RESPONSE.validator()
        result = validator.validate(cloud_event)
        self.assertEqual(
            "Invalid RPC Response CloudEvent source [//bo.cloud/petapp/1/dog]. Invalid RPC method uri. UriPart " +
            "should be the method to be called, or method from response.," + "Invalid RPC Response " + "CloudEvent "
                                                                                                       "sink ["
                                                                                                       "//VCU.myvin/body.access/1/UpdateDoor]. " + "Invalid RPC uri application " + "response topic. UriPart is missing rpc.response.",
            result.get_message())

    def test_create_a_v6_cloudevent_and_validate_it_against_sdk(self):
        source = build_long_uri_for_test()
        uuid = Factories.UUIDV6.create()
        id = LongUuidSerializer.instance().serialize(uuid)
        proto_payload=build_proto_payload_for_test()
        # additional attributes
        u_cloud_event_attributes = UCloudEventAttributesBuilder().with_priority(
            UPriority.UPRIORITY_CS0).with_ttl(1000).build()
        # build the cloud event
        cloud_event = CloudEventFactory.build_base_cloud_event(id, source, proto_payload.SerializeToString(),
                                                               proto_payload.type_url, u_cloud_event_attributes,
                                                               UCloudEvent.get_event_type(
                                                                   UMessageType.UMESSAGE_TYPE_PUBLISH))
        validator = Validators.PUBLISH.validator()
        result = validator.validate(cloud_event)
        self.assertTrue(result.is_success())
        self.assertFalse(UCloudEvent.is_expired(cloud_event))
