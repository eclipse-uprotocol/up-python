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


import json
import os
import unittest

from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.uri.factory.uresource_builder import UResourceBuilder
from uprotocol.validation.validationresult import ValidationResult
from uprotocol.proto.uri_pb2 import UUri, UEntity, UResource, UAuthority


class TestUriValidator(unittest.TestCase):

    def test_validate_blank_uri(self):
        uri = LongUriSerializer().deserialize(None)
        status = UriValidator.validate(uri)
        self.assertTrue(UriValidator.is_empty(uri))
        self.assertEqual("Uri is empty.", status.get_message())

    def test_validate_uri_with_no_entity_getName(self):
        uri = LongUriSerializer().deserialize("//")
        status = UriValidator.validate(uri)
        self.assertTrue(UriValidator.is_empty(uri))
        self.assertEqual("Uri is empty.", status.get_message())

    def test_validate_uri_with_getEntity(self):
        uri = LongUriSerializer().deserialize("/neelam")
        status = UriValidator.validate(uri)
        self.assertTrue(ValidationResult.success().__eq__(status))

    def test_validate_with_malformed_uri(self):
        uri = LongUriSerializer().deserialize("neelam")
        status = UriValidator.validate(uri)
        self.assertTrue(UriValidator.is_empty(uri))
        self.assertEqual("Uri is empty.", status.get_message())

    def test_validate_with_blank_uentity_name_uri(self):
        status = UriValidator.validate(UUri())
        self.assertTrue(status.is_failure())
        self.assertEqual("Uri is empty.", status.get_message())

    def test_validateRpcMethod_with_valid_uri(self):
        uri = LongUriSerializer().deserialize("/neelam//rpc.echo")
        status = UriValidator.validate_rpc_method(uri)
        self.assertTrue(ValidationResult.success().__eq__(status))

    def test_validateRpcMethod_with_invalid_uri(self):
        uri = LongUriSerializer().deserialize("/neelam/echo")
        status = UriValidator.validate_rpc_method(uri)
        self.assertTrue(status.is_failure())
        self.assertEqual("Uri is empty.", status.get_message())

    def test_validateRpcMethod_with_malformed_uri(self):
        uri = LongUriSerializer().deserialize("neelam")
        status = UriValidator.validate_rpc_method(uri)
        self.assertTrue(UriValidator.is_empty(uri))
        self.assertEqual("Uri is empty.", status.get_message())

    def test_validateRpcResponse_with_valid_uri(self):
        uri = LongUriSerializer().deserialize("/neelam//rpc.response")
        status = UriValidator.validate_rpc_response(uri)
        self.assertTrue(ValidationResult.success().__eq__(status))

    def test_validateRpcResponse_with_malformed_uri(self):
        uri = LongUriSerializer().deserialize("neelam")
        status = UriValidator.validate_rpc_response(uri)
        self.assertTrue(UriValidator.is_empty(uri))
        self.assertEqual("Uri is empty.", status.get_message())

    def test_validateRpcResponse_with_rpc_type(self):
        uri = LongUriSerializer().deserialize("/neelam//dummy.wrong")
        status = UriValidator.validate_rpc_response(uri)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid RPC response type.", status.get_message())

    def test_validateRpcResponse_with_invalid_rpc_response_type(self):
        uri = LongUriSerializer().deserialize("/neelam//rpc.wrong")
        status = UriValidator.validate_rpc_response(uri)
        self.assertTrue(status.is_failure())
        self.assertEqual("Invalid RPC response type.", status.get_message())

    def test_topic_uri_with_version_when_it_is_valid_remote(self):
        uri = "//VCU.MY_CAR_VIN/body.access/1/door.front_left#Door"
        status = UriValidator.validate(LongUriSerializer().deserialize(uri))
        self.assertTrue(status.is_success)

    def test_topic_uri_no_version_when_it_is_valid_remote(self):
        uri = "//VCU.MY_CAR_VIN/body.access//door.front_left#Door"
        status = UriValidator.validate(LongUriSerializer().deserialize(uri))
        self.assertTrue(status.is_success)

    def test_topic_uri_with_version_when_it_is_valid_local(self):
        uri = "/body.access/1/door.front_left#Door"
        status = UriValidator.validate(LongUriSerializer().deserialize(uri))
        self.assertTrue(status.is_success)

    def test_topic_uri_no_version_when_it_is_valid_local(self):
        uri = "/body.access//door.front_left#Door"
        status = UriValidator.validate(LongUriSerializer().deserialize(uri))
        self.assertTrue(status.is_success)

    def test_topic_uri_invalid_when_uri_has_schema_only(self):
        uri = ":"
        status = UriValidator.validate(LongUriSerializer().deserialize(uri))
        self.assertTrue(status.is_failure())

    def test_topic_uri_invalid_when_uri_has_empty_use_name_local(self):
        uri = "/"
        status = UriValidator.validate(LongUriSerializer().deserialize(uri))
        self.assertTrue(status.is_failure())

    def test_topic_uri_invalid_when_uri_is_remote_no_authority(self):
        uri = "//"
        status = UriValidator.validate(LongUriSerializer().deserialize(uri))
        self.assertTrue(status.is_failure())

    def test_topic_uri_invalid_when_uri_is_remote_no_authority_with_use(self):
        uri = "///body.access/1/door.front_left#Door"
        status = UriValidator.validate(LongUriSerializer().deserialize(uri))
        self.assertTrue(status.is_failure())

    def test_topic_uri_invalid_when_uri_is_missing_use_remote(self):
        uri = "//VCU.myvin///door.front_left#Door"
        status = UriValidator.validate(LongUriSerializer().deserialize(uri))
        self.assertTrue(status.is_failure())

    def test_topic_uri_invalid_when_uri_is_missing_use_name_remote(self):
        uri = "/1/door.front_left#Door"
        status = UriValidator.validate(LongUriSerializer().deserialize(uri))
        self.assertTrue(status.is_failure())

    def test_topic_uri_invalid_when_uri_is_missing_use_name_local(self):
        uri = "//VCU.myvin//1"
        status = UriValidator.validate(LongUriSerializer().deserialize(uri))
        self.assertTrue(status.is_failure())

    def test_rpc_topic_uri_with_version_when_it_is_valid_remote(self):
        uri = "//bo.cloud/petapp/1/rpc.response"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_success)

    def test_rpc_topic_uri_no_version_when_it_is_valid_remote(self):
        uri = "//bo.cloud/petapp//rpc.response"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_success)

    def test_rpc_topic_uri_with_version_when_it_is_valid_local(self):
        uri = "/petapp/1/rpc.response"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_success)

    def test_rpc_topic_uri_no_version_when_it_is_valid_local(self):
        uri = "/petapp//rpc.response"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_success)

    def test_rpc_topic_uri_invalid_when_uri_has_schema_only(self):
        uri = ":"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_failure())

    def test_rpc_topic_uri_with_version_when_it_is_not_valid_missing_rpc_response_local(self):
        uri = "/petapp/1/dog"
        status = UriValidator.validate_rpc_method(LongUriSerializer().deserialize(uri))
        self.assertTrue(status.is_failure())

    def test_rpc_topic_uri_with_version_when_it_is_not_valid_missing_rpc_response_remote(
        self,
    ):
        uri = "//petapp/1/dog"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_failure())

    def test_rpc_topic_uri_invalid_when_uri_is_remote_no_authority(self):
        uri = "//"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_failure())

    def test_rpc_topic_uri_invalid_when_uri_is_remote_no_authority_with_use(
        self,
    ):
        uri = "///body.access/1"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_failure())

    def test_rpc_topic_uri_invalid_when_uri_is_missing_use(self):
        uri = "//VCU.myvin"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_failure())

    def test_rpc_topic_uri_invalid_when_uri_is_missing_use_name_remote(self):
        uri = "/1"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_failure())

    def test_rpc_topic_uri_invalid_when_uri_is_missing_use_name_local(self):
        uri = "//VCU.myvin//1"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_failure())

    def test_rpc_method_uri_with_version_when_it_is_valid_remote(self):
        uri = "//VCU.myvin/body.access/1/rpc.UpdateDoor"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_success)

    def test_rpc_method_uri_no_version_when_it_is_valid_remote(self):
        uri = "//VCU.myvin/body.access//rpc.UpdateDoor"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_success)

    def test_rpc_method_uri_with_version_when_it_is_valid_local(self):
        uri = "/body.access/1/rpc.UpdateDoor"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_success)

    def test_rpc_method_uri_no_version_when_it_is_valid_local(self):
        uri = "/body.access//rpc.UpdateDoor"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_success)

    def test_rpc_method_uri_invalid_when_uri_has_schema_only(self):
        uri = ":"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_failure())

    def test_rpc_method_uri_with_version_when_it_is_not_valid_not_rpc_method_local(
        self,
    ):
        uri = "/body.access//UpdateDoor"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_failure())

    def test_rpc_method_uri_with_version_when_it_is_not_valid_not_rpc_method_remote(
        self,
    ):
        uri = "//body.access/1/UpdateDoor"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_failure())

    def test_rpc_method_uri_invalid_when_uri_is_remote_no_authority(self):
        uri = "//"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_failure())

    def test_rpc_method_uri_invalid_when_uri_is_remote_no_authority_with_use(
        self,
    ):
        uri = "///body.access/1/rpc.UpdateDoor"
        uuri = LongUriSerializer().deserialize(uri)
        status = UriValidator.validate_rpc_method(uuri)
        self.assertEqual("", str(uuri))
        self.assertTrue(status.is_failure())

    def test_rpc_method_uri_invalid_when_uri_is_remote_missing_authority_remotecase(
        self,
    ):
        uuri = UUri(
            entity=UEntity(name="body.access"),
            resource=UResource(name="rpc", instance="UpdateDoor"),
            authority=UAuthority(),
        )
        status = UriValidator.validate_rpc_method(uuri)
        self.assertTrue(status.is_failure())
        self.assertEqual(
            "Uri is remote missing uAuthority.", status.get_message()
        )

    def test_rpc_method_uri_invalid_when_uri_is_missing_use(self):
        uri = "//VCU.myvin"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_failure())

    def test_rpc_method_uri_invalid_when_uri_is_missing_use_name_local(self):
        uri = "/1/rpc.UpdateDoor"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_failure())

    def test_rpc_method_uri_invalid_when_uri_is_missing_use_name_remote(self):
        uri = "//VCU.myvin//1/rpc.UpdateDoor"
        status = UriValidator.validate_rpc_method(
            LongUriSerializer().deserialize(uri)
        )
        self.assertTrue(status.is_failure())

    def test_all_valid_uris(self):
        # Access the "validUris" array
        valid_uris = self.get_json_object()["validUris"]
        for valid_uri in valid_uris:
            uuri = LongUriSerializer().deserialize(valid_uri)
            status = UriValidator.validate(uuri)
            self.assertTrue(status.is_success())

    def test_all_invalid_uris(self):
        # Access the "invalidUris" array
        invalid_uris = self.get_json_object()["invalidUris"]
        for invalid_uri in invalid_uris:
            uuri = LongUriSerializer().deserialize(invalid_uri["uri"])
            status = UriValidator.validate(uuri)
            self.assertTrue(status.is_failure())
            self.assertEqual(
                status.get_message(), invalid_uri["status_message"]
            )

    def test_all_valid_rpc_uris(self):
        valid_rpc_uris = self.get_json_object()["validRpcUris"]
        for valid_rpc_uri in valid_rpc_uris:
            uuri = LongUriSerializer().deserialize(valid_rpc_uri)
            status = UriValidator.validate_rpc_method(uuri)
            self.assertTrue(status.is_success)

    def test_all_invalid_rpc_uris(self):
        invalid_rpc_uris = self.get_json_object()["invalidRpcUris"]
        for invalid_rpc_uri in invalid_rpc_uris:
            uuri = LongUriSerializer().deserialize(invalid_rpc_uri["uri"])
            status = UriValidator.validate_rpc_method(uuri)
            self.assertTrue(status.is_failure())
            self.assertEqual(
                status.get_message(), invalid_rpc_uri["status_message"]
            )

    def test_all_valid_rpc_response_uris(self):
        valid_rpc_response_uris = self.get_json_object()[
            "validRpcResponseUris"
        ]
        for valid_rpc_response_uri in valid_rpc_response_uris:
            uuri = LongUriSerializer().deserialize(valid_rpc_response_uri)
            status = UriValidator.validate_rpc_response(uuri)
            self.assertTrue(UriValidator.is_rpc_response(uuri))
            self.assertTrue(status.is_success)

    def test_valid_rpc_response_uri(self):
        uuri = UUri(
            entity=UEntity(name="neelam"),
            resource=UResource(name="rpc", id=0, instance="response"),
        )
        status = UriValidator.validate_rpc_response(uuri)
        self.assertTrue(UriValidator.is_rpc_response(uuri))
        self.assertTrue(status.is_success)

    def test_all_invalid_rpc_response_uris(self):
        invalid_rpc_response_uris = self.get_json_object()[
            "invalidRpcResponseUris"
        ]
        for invalid_rpc_response_uri in invalid_rpc_response_uris:
            uuri = LongUriSerializer().deserialize(invalid_rpc_response_uri)
            status = UriValidator.validate_rpc_response(uuri)
            self.assertTrue(status.is_failure())

    def test_invalid_rpc_method_uri(self):
        uuri: UUri = UUri(
            entity=UEntity(name="hello.world"),
            resource=UResource(name="testrpc", instance="SayHello"),
        )
        status = UriValidator.validate_rpc_method(uuri)
        self.assertFalse(UriValidator.is_rpc_method(uuri))
        self.assertFalse(status.is_success())

    def test_invalid_rpc_response_uri(self):
        uuri: UUri = UUri(
            entity=UEntity(name="hartley"),
            resource=UResource(name="rpc", id=19999),
        )
        status = UriValidator.validate_rpc_response(uuri)
        self.assertFalse(UriValidator.is_rpc_response(uuri))
        self.assertFalse(status.is_success())

        uuri: UUri = UUri(
            entity=UEntity(name="hartley"),
            resource=UResource(name="testrpc", instance="response"),
        )
        status = UriValidator.validate_rpc_response(uuri)
        self.assertFalse(UriValidator.is_rpc_response(uuri))
        self.assertFalse(status.is_success())

        uuri: UUri = UUri(
            entity=UEntity(name="hartley"),
            resource=UResource(name="testrpc", instance="response"),
        )
        status = UriValidator.validate_rpc_response(uuri)
        self.assertFalse(UriValidator.is_rpc_response(uuri))
        self.assertFalse(status.is_success())

    @staticmethod
    def get_json_object():
        current_directory = os.getcwd()
        json_file_path = os.path.join(
            current_directory,
            "tests",
            "test_uri",
            "test_validator",
            "uris.json",
        )

        with open(json_file_path, "r") as json_file:
            json_data = json.load(json_file)

        return json_data

    def test_is_rpc_method_with_uresource_and_no_uauthority(self):
        self.assertFalse(UriValidator.is_rpc_method(UUri()))

        uri = UUri(
            entity=UEntity(name="hartley"),
            resource=UResourceBuilder.from_id(0x8000),
        )
        self.assertFalse(UriValidator.is_rpc_method(uri))

    def test_is_rpc_method_passing_null_for_uri(self):
        self.assertFalse(UriValidator.is_rpc_method(None))

    def test_is_rpc_method_passing_null_for_resource(self):
        self.assertFalse(UriValidator.is_rpc_method(None))

    def test_is_rpc_method_for_uresource_without_an_instance(self):
        resource = UResource(name="rpc")
        self.assertFalse(UriValidator.is_rpc_method(resource))

    def test_is_rpc_method_for_uresource_with_an_empty_instance(self):
        resource = UResource(name="rpc", instance="")
        self.assertFalse(UriValidator.is_rpc_method(resource))

    def test_is_rpc_method_for_uresource_with_id_that_is_less_than_min_topic(
        self,
    ):
        resource = UResource(name="rpc", id=0)
        self.assertTrue(UriValidator.is_rpc_method(resource))

    def test_is_rpc_method_for_uresource_with_id_that_is_greater_than_min_topic(
        self,
    ):
        resource = UResource(name="rpc", id=0x8000)
        self.assertFalse(UriValidator.is_rpc_method(resource))

    def test_is_empty_with_null_uri(self):
        self.assertTrue(UriValidator.is_empty(None))

    def test_is_resolved_when_uri_is_long_form_only(self):
        uri = UUri(
            entity=UEntity(name="hartley", version_major=23),
            resource=UResource(name="rpc", instance="echo"),
        )
        self.assertFalse(UriValidator.is_resolved(uri))

    def test_is_local_when_authority_is_null(self):
        self.assertFalse(UriValidator.is_local(None))

    def test_is_remote_when_authority_is_null(self):
        self.assertFalse(UriValidator.is_remote(None))

    # def test_is_remote_when_authority_does_not_have_a_name_but_does_have_a_number_set(self):
    #     authority = UAuthority(id=b"hello Jello")
    #     self.assertTrue(UriValidator.is_remote(authority))
    #     self.assertFalse(authority.name is not None)
    #     self.assertEqual(authority.number_case(), UAuthority.NumberCase.ID)

    # def test_is_remote_when_authority_has_name_and_number_set(self):
    #     authority = UAuthority(name="vcu.veh.steven.gm.com", id=b"hello Jello")
    #     self.assertTrue(UriValidator.is_remote(authority))
    #     self.assertTrue(authority.name is not None)
    #     self.assertEqual(authority.number_case(), UAuthority.NumberCase.ID)

    # def test_is_remote_when_authority_has_name_and_number_is_not_set(self):
    #     authority = UAuthority(name="vcu.veh.steven.gm.com")
    #     self.assertTrue(UriValidator.is_remote(authority))
    #     self.assertTrue(authority.name is not None)
    #     self.assertEqual(authority.number_case(), UAuthority.NumberCase.NUMBER_NOT_SET)


if __name__ == "__main__":
    unittest.main()
