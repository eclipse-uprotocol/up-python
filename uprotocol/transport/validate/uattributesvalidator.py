# -------------------------------------------------------------------------
import time
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


from abc import abstractmethod
from enum import Enum
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.uattributes_pb2 import UAttributes, UMessageType
from uprotocol.proto.ustatus_pb2 import UCode
from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.uuid.factory.uuidutils import UUIDUtils
from uprotocol.validation.validationresult import ValidationResult


class UAttributesValidator:
    """
    UAttributes is the class that defines the Payload. It is the place for configuring time to live, priority,
    security tokens and more.<br><br>
    Each UAttributes class defines a different type of message payload. The payload can represent a simple published
    payload with some state change,Payload representing an RPC request or Payload representing an RPC response.<br><br>
    UAttributesValidator is a base class for all UAttribute validators, that can help validate that the
    UAttributes object is correctly defined to define the Payload correctly.

    """

    @staticmethod
    def get_validator(attribute: UAttributes):
        """
        Static factory method for getting a validator according to the UMessageType defined in the
        UAttributes.<br>
        @param attribute: UAttributes containing the UMessageType.
        @return: returns a UAttributesValidator according to the UMessageType defined in the
        UAttributes.
        """
        if attribute.type is None:
            return Validators.PUBLISH.validator()
        elif attribute.type == UMessageType.UMESSAGE_TYPE_RESPONSE:
            return Validators.RESPONSE.validator()
        elif attribute.type == UMessageType.UMESSAGE_TYPE_REQUEST:
            return Validators.REQUEST.validator()
        else:
            return Validators.PUBLISH.validator()

    def validate(self, attributes: UAttributes) -> ValidationResult:
        """
        Take a UAttributes object and run validations.<br><br>
        @param attributes:The UAttriubes to validate.
        @return:Returns a ValidationResult that is success or failed with a message containing all validation errors
        for invalid configurations.
        """
        error_messages = [self.validate_type(attributes),
                          self.validate_ttl(attributes),
                          self.validate_sink(attributes), self.validate_comm_status(attributes),
                          self.validate_permission_level(attributes), self.validate_req_id(attributes)]

        error_messages = [status.get_message() for status in error_messages if
                          status.is_failure()]

        if error_messages:
            return ValidationResult.failure(",".join(error_messages))
        else:
            return ValidationResult.success()

    @staticmethod
    def is_expired(u_attributes: UAttributes) -> bool:
        '''
        Check the time-to-live attribute to see if it has expired. <br>
        8The message has expired when the current time is greater than the original UUID time
        plus the ttl attribute.
        @param uAttributes UAttributes with time to live value.
        @return Returns a true if the original time plus the ttl is less than the current time
        '''
        ttl = u_attributes.ttl
        maybe_time = UUIDUtils.getTime(u_attributes.id)

        if not u_attributes.HasField('ttl') or maybe_time is None or ttl <=0:
            return False
    
        return (maybe_time + ttl) < int(time.time() * 1000)

    @staticmethod
    def validate_ttl(attr: UAttributes) -> ValidationResult:
        """
        Validate the time to live configuration. If the UAttributes does not contain a time to live then the
        ValidationResult
        is ok.<br><br>
        @param attr:UAttributes object containing the message time to live configuration to validate.
        @return:Returns a  ValidationResult that is success or failed with a failure message.
        """
        if attr.HasField('ttl') and attr.ttl <= 0:
            return ValidationResult.failure(f"Invalid TTL [{attr.ttl}]")
        else:
            return ValidationResult.success()

    @staticmethod
    def validate_sink(attr: UAttributes) -> ValidationResult:
        """
        Validate the sink UriPart for the default case. If the UAttributes does not contain a sink then the
        ValidationResult
        is ok.<br><br>
        @param attr:UAttributes object containing the sink to validate.
        @return:Returns a  ValidationResult that is success or failed with a failure message.
        """
        return UriValidator.validate(attr.sink) if attr.HasField('sink') else ValidationResult.success()

    @staticmethod
    def validate_permission_level(attr: UAttributes) -> ValidationResult:
        """
        Validate the permissionLevel for the default case. If the UAttributes does not contain a permission level
        then the  ValidationResult is ok.<br><br>
        @param attr:UAttributes object containing the permission level to validate.
        @return:Returns a  ValidationResult indicating if the permissionLevel is valid or not.
        """
        if attr.HasField('permission_level') and attr.permission_level <= 0:
            return ValidationResult.failure("Invalid Permission Level")
        else:
            return ValidationResult.success()

    @staticmethod
    def validate_comm_status(attr: UAttributes) -> ValidationResult:
        """
        Validate the commStatus for the default case. If the UAttributes does not contain a comm status then the
         ValidationResult is ok.<br><br>
        @param attr:UAttributes object containing the comm status to validate.
        @return:Returns a  ValidationResult that is success or failed with a failure message.
        """
        if attr.HasField('commstatus'):
            try:
                UCode.Name(attr.commstatus)
            except ValueError:
                return ValidationResult.failure("Invalid Communication Status Code")

        return ValidationResult.success()

    @staticmethod
    def validate_req_id(attr: UAttributes) -> ValidationResult:
        """
        Validate the correlationId for the default case. If the UAttributes does not contain a request id then the
         ValidationResult is ok.<br><br>
        @param attr:Attributes object containing the request id to validate.
        @return:Returns a  ValidationResult that is success or failed with a failure message.
        """

        if attr.HasField('reqid') and not UUIDUtils.isuuid(attr.reqid):
            return ValidationResult.failure("Invalid UUID")
        else:
            return ValidationResult.success()

    @abstractmethod
    def validate_type(self, attr: UAttributes):
        """
        Validate the UMessageType attribute, it is required.<br><br>
        @param attr:UAttributes object containing the message type to validate.
        @return:Returns a  ValidationResult that is success or failed with a failure message.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class Publish(UAttributesValidator):
    """
     Implements validations for UAttributes that define a message that is meant for publishing state changes.
    """

    def validate_type(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validates that attributes for a message meant to publish state changes has the correct type.<br><br>
        @param attributes_value:UAttributes object containing the message type to validate.
        @return:Returns a  ValidationResult that is success or failed with a failure message.
        """
        return ValidationResult.success() if attributes_value.type == UMessageType.UMESSAGE_TYPE_PUBLISH else (
            ValidationResult.failure(
                f"Wrong Attribute Type [{UMessageType.Name(attributes_value.type)}]"))

    def __str__(self):
        return "UAttributesValidator.Publish"


class Request(UAttributesValidator):
    """
    Implements validations for UAttributes that define a message that is meant for an RPC request.
    """

    def validate_type(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validates that attributes for a message meant for an RPC request has the correct type.<br><br>
        @param attributes_value:UAttributes object containing the message type to validate.
        @return:Returns a  ValidationResult that is success or failed with a failure message.
        """
        return ValidationResult.success() if attributes_value.type == UMessageType.UMESSAGE_TYPE_REQUEST else (
            ValidationResult.failure(
                f"Wrong Attribute Type [{UMessageType.Name(attributes_value.type)}]"))

    def validate_sink(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validates that attributes for a message meant for an RPC request has a destination sink.<br><br> In the case
        of an RPC request, the sink is required.
        @param attributes_value:UAttributes object containing the sink to validate.
        @return:Returns a  ValidationResult that is success or failed with a failure message.
        """
        return UriValidator.validate_rpc_method(
            attributes_value.sink) if attributes_value.HasField('sink') else ValidationResult.failure("Missing Sink")

    def validate_ttl(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validate the time to live configuration.<br>In the case of an RPC request, the time to live is required.<br><br>
        @param attributes_value:UAttributes object containing the time to live to validate.
        @return:Returns a  ValidationResult that is success or failed with a failure message.
        """
        if not attributes_value.HasField('ttl'):
            return ValidationResult.failure("Missing TTL")
        if attributes_value.ttl <= 0:
            return ValidationResult.failure(f"Invalid TTL [{attributes_value.ttl}]")

        return ValidationResult.success()

    def __str__(self):
        return "UAttributesValidator.Request"


class Response(UAttributesValidator):
    """
    Implements validations for UAttributes that define a message that is meant for an RPC response.
    """

    def validate_type(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validates that attributes for a message meant for an RPC response has the correct type.<br><br>
        @param attributes_value:UAttributes object containing the message type to validate.
        @return:Returns a  ValidationResult that is success or failed with a failure message.
        """
        return ValidationResult.success() if attributes_value.type == UMessageType.UMESSAGE_TYPE_RESPONSE else (
            ValidationResult.failure(
                f"Wrong Attribute Type [{UMessageType.Name(attributes_value.type)}]"))

    def validate_sink(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validates that attributes for a message meant for an RPC response has a destination sink.<br>In the case of
        an RPC response, the sink is required.<br><br>
        @param attributes_value:UAttributes object containing the sink to validate.
        @return:Returns a  ValidationResult that is success or failed with a failure message.
        """
        if not attributes_value.HasField('sink') or attributes_value.sink == UUri():
            return ValidationResult.failure("Missing Sink")
        result = UriValidator.validate_rpc_response(attributes_value.sink)
        return result


    def validate_req_id(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validate the correlationId. n the case of an RPC response, the correlation id is required.<br><br>
        @param attributes_value:UAttributes object containing the correlation id to validate.
        @return:Returns a  ValidationResult that is success or failed with a failure message.
        """
        return ValidationResult.success() if attributes_value.reqid and UUIDUtils.isuuid(
            attributes_value.reqid) else ValidationResult.failure("Missing correlationId")

    def __str__(self):
        return "UAttributesValidator.Response"


class Validators(Enum):
    """
    Validators Factory. <br>Example: UAttributesValidator validateForPublishMessageType =
    UAttributesValidator.Validators.PUBLISH.validator()
    """
    PUBLISH = Publish()
    REQUEST = Request()
    RESPONSE = Response()

    def validator(self):
        return self.value
