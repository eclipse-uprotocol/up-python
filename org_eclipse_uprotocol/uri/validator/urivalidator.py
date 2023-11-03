# -------------------------------------------------------------------------

# Copyright (c) 2023 General Motors GTO LLC

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from org_eclipse_uprotocol.proto.uri_pb2 import UAuthority
# -------------------------------------------------------------------------
from org_eclipse_uprotocol.proto.uri_pb2 import UEntity
from org_eclipse_uprotocol.proto.uri_pb2 import UResource
from org_eclipse_uprotocol.proto.uri_pb2 import UUri
from org_eclipse_uprotocol.transport.datamodel.ustatus import UStatus, Code


class UriValidator:
    """
    Class for validating Uris.
    """

    @staticmethod
    def validate(uri: UUri) -> UStatus:
        """
        Validate a UUri to ensure that it has at least a name for the uEntity.<br><br>
        @param uri:UUri to validate.
        @return:Returns UStatus containing a success or a failure with the error message.
        """
        if UriValidator.is_empty(uri):
            return UStatus.failed_with_msg_and_code("Uri is empty.", Code.INVALID_ARGUMENT)

        if uri.entity.name.strip() == "":
            return UStatus.failed_with_msg_and_code("Uri is missing uSoftware Entity name.", Code.INVALID_ARGUMENT)

        return UStatus.ok()

    @staticmethod
    def validate_rpc_method(uri: UUri) -> UStatus:
        """
        Validate a UUri that is meant to be used as an RPC method URI. Used in Request sink values and Response
        source values.<br><br>
        @param uri:UUri to validate.
        @return:Returns UStatus containing a success or a failure with the error message.
        """
        status = UriValidator.validate(uri)
        if status.isFailed():
            return status

        if not UriValidator.is_rpc_method(uri):
            return UStatus.failed_with_msg_and_code(
                "Invalid RPC method uri. Uri should be the method to be called, or method from response.",
                Code.INVALID_ARGUMENT)

        return UStatus.ok()

    @staticmethod
    def validate_rpc_response(uri: UUri) -> UStatus:
        """
        Validate a UUri that is meant to be used as an RPC response URI. Used in Request source values and
        Response sink values.<br><br>
        @param uri:UUri to validate.
        @return:Returns UStatus containing a success or a failure with the error message.
        """
        status = UriValidator.validate(uri)
        if status.isFailed():
            return status

        u_resource = uri.resource
        if not (UriValidator.is_rpc_method(
                u_resource) and u_resource.instance == UResource.for_rpc_response().instance):
            return UStatus.failed_with_msg_and_code("Invalid RPC response type.", Code.INVALID_ARGUMENT)

        return UStatus.ok()

    @staticmethod
    def is_empty(uuri: UUri) -> bool:
        """
        Indicates that this  URI is an empty container and has no valuable information in building uProtocol sinks or
        sources.<br><br>
        @param uuri: An UUri proto message object
        @return:Returns true if this  URI is an empty container and has no valuable information in building uProtocol
        sinks or sources.
        """
        return (UriValidator.is_authority_empty(uuri.authority) and UriValidator.is_entity_empty(
            uuri.entity) and UriValidator.is_resource_empty(uuri.resource))

    @staticmethod
    def is_authority_empty(authority: UAuthority) -> bool:
        return all([authority.name.strip() == "", len(authority.ip) == 0, len(authority.id) == 0])

    @staticmethod
    def is_entity_empty(entity: UEntity) -> bool:
        return all([entity.name.strip() == "", entity.version_major == 0, entity.id == 0, entity.version_minor == 0])

    @staticmethod
    def is_resource_empty(resource: UResource) -> bool:
        return resource.name.strip() == "" or resource.name == "rpc" and not (
                resource.instance.strip() != "" or resource.message.strip() != "" or resource.id != 0)

    @staticmethod
    def is_rpc_method(uuri: UUri) -> bool:
        """
        Returns true if this resource specifies an RPC method call or RPC response.<br><br>
        @param uresource: UResource protobuf message
        @return:Returns true if this resource specifies an RPC method call or RPC response.
        """
        return not UriValidator.is_empty(uuri) and uuri.resource.name == "rpc" and (
                uuri.resource.instance.strip() != "" or uuri.resource.id != 0)

    @staticmethod
    def is_resolved(uuri: UUri) -> bool:
        if uuri is None:
            raise ValueError("Uri cannot be None.")

        return not UriValidator.is_empty(uuri)

    @staticmethod
    def is_rpc_response(uuri: UUri) -> bool:
        if uuri is None:
            raise ValueError("Uri cannot be None.")

        resource = uuri.get_resource()
        return UriValidator.is_rpc_method(uuri) and (
                (uuri.resource.instance.strip() != "" and "response" in resource.Instance) or resource.get_id() != 0)

    @staticmethod
    def is_micro_form(uuri: UUri) -> bool:
        """
        Determines if this UUri can be serialized into a micro form UUri.<br><br>
        @param uuri: An UUri proto message object
        @return:Returns true if this UUri can be serialized into a micro form UUri.
        """
        return not UriValidator.is_empty(uuri) and (
                    UriValidator.is_authority_empty(uuri.authority) or len(uuri.authority.ip) != 0 or len(
                uuri.authority.id) != 0) and uuri.entity.id != 0 and uuri.resource.id != 0

    @staticmethod
    def is_long_form(uuri: UUri) -> bool:
        """
        Determines if this UUri can be serialized into a long form UUri.<br><br>
        @param uuri: An UUri proto message object
        @return:Returns true if this UUri can be serialized into a long form UUri.
        """
        return (
                    uuri.authority.name.strip() != "" and uuri.entity.name.strip() != "" and
                    uuri.resource.name.strip() != "")

    @staticmethod
    def is_remote(uuri: UUri) -> bool:
        return not UriValidator.is_authority_empty(uuri.authority)
