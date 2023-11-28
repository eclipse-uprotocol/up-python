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


from org_eclipse_uprotocol.proto.uri_pb2 import UAuthority
from org_eclipse_uprotocol.proto.uri_pb2 import UEntity
from org_eclipse_uprotocol.proto.uri_pb2 import UResource
from org_eclipse_uprotocol.proto.uri_pb2 import UUri
from org_eclipse_uprotocol.validation.validationresult import ValidationResult


class UriValidator:
    """
    Class for validating Uris.
    """

    @staticmethod
    def validate(uri: UUri) -> ValidationResult:
        """
        Validate a UUri to ensure that it has at least a name for the uEntity.<br><br>
        @param uri:UUri to validate.
        @return:Returns UStatus containing a success or a failure with the error message.
        """
        if UriValidator.is_empty(uri):
            return ValidationResult.failure("Uri is empty.")

        if uri.HasField('authority') and not UriValidator.is_remote(uri.authority):
            return ValidationResult.failure("Uri is remote missing uAuthority.")

        if uri.entity.name.strip() == "":
            return ValidationResult.failure("Uri is missing uSoftware Entity name.")

        return ValidationResult.success()

    @staticmethod
    def validate_rpc_method(uri: UUri) -> ValidationResult:
        """
        Validate a UUri that is meant to be used as an RPC method URI. Used in Request sink values and Response
        source values.<br><br>
        @param uri:UUri to validate.
        @return:Returns UStatus containing a success or a failure with the error message.
        """
        status = UriValidator.validate(uri)
        if status.is_failure():
            return status

        if not UriValidator.is_rpc_method(uri):
            return ValidationResult.failure(
                "Invalid RPC method uri. Uri should be the method to be called, or method from response.")

        return ValidationResult.success()

    @staticmethod
    def validate_rpc_response(uri: UUri) -> ValidationResult:
        """
        Validate a UUri that is meant to be used as an RPC response URI. Used in Request source values and
        Response sink values.<br><br>
        @param uri:UUri to validate.
        @return:Returns UStatus containing a success or a failure with the error message.
        """
        status = UriValidator.validate(uri)
        if status.is_failure():
            return status

        if not UriValidator.is_rpc_response(uri):
            return ValidationResult.failure("Invalid RPC response type.")

        return ValidationResult.success()

    @staticmethod
    def is_empty(uri: UUri) -> bool:
        if uri is None:
            raise ValueError("Uri cannot be None.")
        return not uri.HasField('authority') and not uri.HasField('entity') and not uri.HasField('resource')


    @staticmethod
    def is_rpc_method(uri: UUri) -> bool:
        """
        Returns true if this resource specifies an RPC method call or RPC response.<br><br>
        @param uri:
        @return:Returns true if this resource specifies an RPC method call or RPC response.
        """
        if uri is None:
            raise ValueError("Uri cannot be None.")
        return not UriValidator.is_empty(uri) and uri.resource.name == "rpc" and (
                uri.resource.HasField('instance') and uri.resource.instance.strip() != "" or (
                uri.resource.HasField('id') and uri.resource.id != 0))

    @staticmethod
    def is_resolved(uuri: UUri) -> bool:
        if uuri is None:
            raise ValueError("Uri cannot be None.")

        return not UriValidator.is_empty(uuri)

    @staticmethod
    def is_rpc_response(uuri: UUri) -> bool:
        if uuri is None:
            raise ValueError("Uri cannot be None.")

        return UriValidator.is_rpc_method(uuri) and (
                (uuri.resource.HasField('instance') and "response" in uuri.resource.instance) or (
                uuri.resource.HasField('id') and uuri.resource.id != 0))

    @staticmethod
    def is_micro_form(uuri: UUri) -> bool:
        """
        Determines if this UUri can be serialized into a micro form UUri.<br><br>
        @param uuri: An UUri proto message object
        @return:Returns true if this UUri can be serialized into a micro form UUri.
        """
        if uuri is None:
            raise ValueError("Uri cannot be None.")
        return not UriValidator.is_empty(uuri) and uuri.entity.HasField('id') and uuri.resource.HasField('id') and (
                not uuri.HasField('authority') or uuri.authority.HasField('ip') or uuri.authority.HasField('id'))

    @staticmethod
    def is_long_form(uuri: UUri) -> bool:
        """
        Determines if this UUri can be serialized into a long form UUri.<br><br>
        @param uuri: An UUri proto message object
        @return:Returns true if this UUri can be serialized into a long form UUri.
        """
        if uuri is None:
            raise ValueError("Uri cannot be None.")
        return not UriValidator.is_empty(uuri) and not (uuri.HasField('authority') and uuri.authority.HasField(
            'name')) and not uuri.entity.name.strip() == '' and not uuri.resource.name.strip() == ''

    @staticmethod
    def is_remote(authority: UAuthority) -> bool:
        if authority is None:
            raise ValueError("Authority cannot be None.")
        return not all([authority.name.strip() == "", len(authority.ip) == 0, len(authority.id) == 0])
