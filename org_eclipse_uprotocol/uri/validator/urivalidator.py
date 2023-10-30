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

# -------------------------------------------------------------------------

from org_eclipse_uprotocol.transport.datamodel.ustatus import UStatus, Code

from org_eclipse_uprotocol.proto.uri_pb2 import UUri
from org_eclipse_uprotocol.uri.factory.uresource_factory import UResourceFactory
from org_eclipse_uprotocol.uri.factory.uuri_factory import UUriFactory


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
        if UUriFactory.is_empty(uri):
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

        u_resource = uri.resource
        if not UResourceFactory.is_rpc_method(u_resource):
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
        if not (UResourceFactory.is_rpc_method(
                u_resource) and u_resource.instance == UResourceFactory.for_rpc_response().instance):
            return UStatus.failed_with_msg_and_code("Invalid RPC response type.", Code.INVALID_ARGUMENT)

        return UStatus.ok()
