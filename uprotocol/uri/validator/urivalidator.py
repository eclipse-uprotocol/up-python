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


from uprotocol.proto.uri_pb2 import UAuthority
from uprotocol.proto.uri_pb2 import UEntity
from uprotocol.proto.uri_pb2 import UResource
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.validation.validationresult import ValidationResult
from multipledispatch import dispatch

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
        '''
        Indicates that this  URI is an empty as it does not contain authority, entity, and resource.
        @param uri UUri to check if it is empty
        @return Returns true if this  URI is an empty container and has no valuable information in building uProtocol sinks or sources.
        '''
        return uri is not None and not uri.HasField('authority') and not uri.HasField('entity') and not uri.HasField('resource')


    @staticmethod
    def is_rpc_method(uri: UUri) -> bool:
        """
        Returns true if this resource specifies an RPC method call or RPC response.<br><br>
        @param uri:
        @return:Returns true if this resource specifies an RPC method call or RPC response.
        """
        return not UriValidator.is_empty(uri) and uri.resource.name == "rpc" and (
                uri.resource.HasField('instance') and uri.resource.instance.strip() != "" or (
                uri.resource.HasField('id') and uri.resource.id != 0))

    @staticmethod
    def is_resolved(uri: UUri) -> bool:

        return uri is not None and not UriValidator.is_empty(uri) and \
            UriValidator.is_long_form(uri) and UriValidator.is_micro_form(uri)

    @staticmethod
    def is_rpc_response(uri: UUri) -> bool:
        if uri is None:
            return False
        
        resource = uri.resource

        return "rpc" in resource.name and uri.HasField("resource") and "response" in resource.instance and resource.HasField("id") and resource.id == 0

    @staticmethod
    @dispatch(UUri)
    def is_micro_form(uri: UUri) -> bool:
        """
        Determines if this UUri can be serialized into a micro form UUri.<br><br>
        @param uuri: An UUri proto message object
        @return:Returns true if this UUri can be serialized into a micro form UUri.
        """

        return uri is not None and not UriValidator.is_empty(uri) and uri.entity.HasField('id') \
            and uri.resource.HasField('id') and UriValidator.is_micro_form(uri.authority)
            
    @staticmethod
    @dispatch(UAuthority)
    def is_micro_form(authority: UAuthority) -> bool:
        '''
        check if UAuthority can be represented in micro format. Micro UAuthorities are local or ones 
        that contain IP address or IDs.
        @param authority UAuthority to check
        @return Returns true if UAuthority can be represented in micro format
        '''


        return UriValidator.is_local(authority) or (authority.HasField('ip') or (authority.HasField('id')))

    @staticmethod
    @dispatch(UUri)
    def is_long_form(uri: UUri) -> bool:
        """
        Determines if this UUri can be serialized into a long form UUri.<br><br>
        @param uuri: An UUri proto message object
        @return:Returns true if this UUri can be serialized into a long form UUri.
        """

        return uri is not None and not UriValidator.is_empty(uri) and UriValidator.is_long_form(uri.authority) and \
            uri.entity.name.strip() != "" and uri.resource.name.strip() != ""
            
    @staticmethod
    @dispatch(UAuthority)
    def is_long_form(authority: UAuthority) -> bool:
        '''
        Returns true if UAuthority contains names so that it can be serialized into long format.
        @param authority UAuthority to check
        @return Returns true if URI contains names so that it can be serialized into long format.
        '''
        return authority is not None and authority.HasField('name') and authority.name.strip() != ""
    
    @staticmethod
    def is_local(authority: UAuthority) -> bool:
        '''
        Returns true if UAuthority is local meaning there is no name/ip/id set.
        @param authority UAuthority to check if it is local or not
        @return Returns true if UAuthority is local meaning the Authority is not populated with name, ip and id
        '''
        return (authority is None) or (authority == UAuthority())

    @staticmethod
    def is_remote(authority: UAuthority) -> bool:
        '''
        Returns true if UAuthority is remote meaning the name and/or ip/id is populated.
        @param authority UAuthority to check if it is remote or not
        @return Returns true if UAuthority is remote meaning the name and/or ip/id is populated.
        '''
        return (authority is not None) and (not authority == UAuthority()) and \
            (UriValidator.is_long_form(authority) or UriValidator.is_micro_form(authority))