"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import time
from abc import abstractmethod
from enum import Enum

from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.uuid.factory.uuidutils import UUIDUtils
from uprotocol.v1.uattributes_pb2 import (
    UAttributes,
    UMessageType,
    UPriority,
)
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.uuid_pb2 import UUID
from uprotocol.validation.validationresult import ValidationResult


class UAttributesValidator:
    """
    UAttributes is the class that defines the Payload. It is the place
    for configuring time to live, priority,
    security tokens and more.<br><br>
    Each UAttributes class defines a different type of message payload.
    The payload can represent a simple published
    payload with some state change,Payload representing an RPC
    request or Payload representing an RPC response.<br><br>
    UAttributesValidator is a base class for all UAttribute
    validators, that can help validate that the
    UAttributes object is correctly defined to define the Payload correctly.

    """

    @staticmethod
    def get_validator(attribute: UAttributes):
        """
        Static factory method for getting a validator according to the
        UMessageType defined in the
        UAttributes.<br>
        @param attribute: UAttributes containing the UMessageType.
        @return: returns a UAttributesValidator according to the
        UMessageType defined in the
        UAttributes.
        """
        if attribute.type is None:
            return Validators.PUBLISH.validator()
        elif attribute.type == UMessageType.UMESSAGE_TYPE_RESPONSE:
            return Validators.RESPONSE.validator()
        elif attribute.type == UMessageType.UMESSAGE_TYPE_REQUEST:
            return Validators.REQUEST.validator()
        elif attribute.type == UMessageType.UMESSAGE_TYPE_NOTIFICATION:
            return Validators.NOTIFICATION.validator()
        else:
            return Validators.PUBLISH.validator()

    def validate(self, attributes: UAttributes) -> ValidationResult:
        """
        Take a UAttributes object and run validations.<br><br>
        @param attributes:The UAttriubes to validate.
        @return:Returns a ValidationResult that is success or failed
        with a message containing all validation errors
        for invalid configurations.
        """
        error_messages = [
            self.validate_type(attributes),
            self.validate_ttl(attributes),
            self.validate_sink(attributes),
            self.validate_priority(attributes),
            self.validate_permission_level(attributes),
            self.validate_req_id(attributes),
            self.validate_id(attributes),
        ]

        error_messages = [status.get_message() for status in error_messages if status.is_failure()]

        if error_messages:
            return ValidationResult.failure(",".join(error_messages))
        else:
            return ValidationResult.success()

    @staticmethod
    def is_expired(u_attributes: UAttributes) -> bool:
        """
        Check the time-to-live attribute to see if it has expired. <br>
        The message has expired when the current time is greater
        than the original UUID time
        plus the ttl attribute.
        @param u_attributes UAttributes with time to live value.
        @return Returns a true if the original time plus the ttl
        is less than the current time
        """
        ttl = u_attributes.ttl
        maybe_time = UUIDUtils.get_time(u_attributes.id)

        if maybe_time is None or ttl <= 0:
            return False

        return (maybe_time + ttl) < int(time.time() * 1000)

    @staticmethod
    def validate_ttl(attr: UAttributes) -> ValidationResult:
        """
        Validate the time to live configuration. If the UAttributes
        does not contain a time to live then the
        ValidationResult
        is ok.<br><br>
        @param attr:UAttributes object containing the message time
        to live configuration to validate.
        @return:Returns a  ValidationResult that is success or
        failed with a failure message.
        """
        return ValidationResult.success()

    @abstractmethod
    def validate_sink(self, attr: UAttributes) -> ValidationResult:
        """
        Validate the sink UriPart.
        @param attr:UAttributes object containing the sink to validate.
        @return:Returns a  ValidationResult that is success or
        failed with a failure message.
        """
        pass

    @staticmethod
    def validate_priority(attr: UAttributes):
        """
        Validate the priority value to ensure it is one of the known CS values

        @param attr Attributes object containing the
        Priority to validate.
        @return Returns a ValidationResult that is success or
        failed with a failure message.
        """
        return (
            ValidationResult.success()
            if attr.priority >= UPriority.UPRIORITY_CS0
            else ValidationResult.failure(f"Invalid UPriority [{UPriority.Name(attr.priority)}]")
        )

    @staticmethod
    def validate_permission_level(attr: UAttributes) -> ValidationResult:
        """
        Validate the permissionLevel for the default case. If the
        UAttributes does not contain a permission level
        then the  ValidationResult is ok.<br><br>
        @param attr:UAttributes object containing the permission
        level to validate.
        @return:Returns a  ValidationResult indicating if the
        permissionLevel is valid or not.
        """
        if attr.HasField("permission_level") and attr.permission_level <= 0:
            return ValidationResult.failure("Invalid Permission Level")
        else:
            return ValidationResult.success()

    @staticmethod
    def validate_req_id(attr: UAttributes) -> ValidationResult:
        """
        Validate the correlationId for the default case. Only the response message should have a reqid.
        @param attr:Attributes object containing the request id to validate.
        @return:Returns a  ValidationResult that is
        success or failed with a failure message.
        """

        return (
            ValidationResult.failure("Message should not have a reqid")
            if attr.HasField("reqid")
            else ValidationResult.success()
        )

    @staticmethod
    def validate_id(attr: UAttributes) -> ValidationResult:
        """
        Validate the Id for the default case. If the UAttributes object does
        not contain an Id, the ValidationResult is failed.

        @param attr:Attributes object containing the Id to validate.
        @return:Returns a  ValidationResult that is success or failed
        """
        if not attr.HasField("id"):
            return ValidationResult.failure("Missing id")
        if not UUIDUtils.is_uuid(attr.id):
            return ValidationResult.failure("Attributes must contain valid uProtocol UUID in id property")
        return ValidationResult.success()

    @abstractmethod
    def validate_type(self, attr: UAttributes):
        """
        Validate the UMessageType attribute, it is required.<br><br>
        @param attr:UAttributes object containing the
        message type to validate.
        @return:Returns a  ValidationResult that is success
        or failed with a failure message.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class Publish(UAttributesValidator):
    """
    Implements validations for UAttributes that define a message
    that is meant for publishing state changes.
    """

    def validate_type(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validates that attributes for a message meant to publish
        state changes has the correct type.<br><br>
        @param attributes_value:UAttributes object containing
        the message type to validate.
        @return:Returns a  ValidationResult that is success or
        failed with a failure message.
        """
        return (
            ValidationResult.success()
            if attributes_value.type == UMessageType.UMESSAGE_TYPE_PUBLISH
            else (ValidationResult.failure(f"Wrong Attribute Type [{UMessageType.Name(attributes_value.type)}]"))
        )

    def validate_sink(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validate the sink UriPart for Publish events. Publish should not have a sink.

        @param attributes_value UAttributes object containing the sink to validate.
        @return Returns a ValidationResult that is success or failed with a failure message.
        """
        return (
            ValidationResult.failure("Sink should not be present")
            if attributes_value.HasField("sink")
            else ValidationResult.success()
        )

    def __str__(self):
        return "UAttributesValidator.Publish"


class Request(UAttributesValidator):
    """
    Implements validations for UAttributes that define a message
    that is meant for an RPC request.
    """

    def validate_type(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validates that attributes for a message meant for an
        RPC request has the correct type.<br><br>
        @param attributes_value:UAttributes object containing
        the message type to validate.
        @return:Returns a  ValidationResult that is success
        or failed with a failure message.
        """
        return (
            ValidationResult.success()
            if attributes_value.type == UMessageType.UMESSAGE_TYPE_REQUEST
            else (ValidationResult.failure(f"Wrong Attribute Type [{UMessageType.Name(attributes_value.type)}]"))
        )

    def validate_sink(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validates that attributes for a message meant for an RPC
        request has a destination sink.<br><br> In the case
        of an RPC request, the sink is required.
        @param attributes_value:UAttributes object containing
        the sink to validate.
        @return:Returns a  ValidationResult that is success or
        failed with a failure message.
        """
        return (
            ValidationResult.success()
            if UriValidator.is_rpc_method(attributes_value.sink)
            else ValidationResult.failure("Invalid Sink Uri")
        )

    def validate_ttl(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validate the time to live configuration.<br>In the case of an RPC
        request, the time to live is required.<br><br>
        @param attributes_value:UAttributes object containing the
        time to live to validate.
        @return:Returns a  ValidationResult that is success or
        failed with a failure message.
        """
        if not attributes_value.HasField("ttl"):
            return ValidationResult.failure("Missing TTL")

        return ValidationResult.success()

    def validate_priority(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validate the priority value to ensure it is one of the known CS values

        @param attributes_value Attributes object containing the Priority to validate.
        @return Returns a {@link ValidationResult} that is success or failed with a failure message.
        """
        return (
            ValidationResult.success()
            if attributes_value.priority >= UPriority.UPRIORITY_CS4
            else ValidationResult.failure(f"Invalid UPriority [{UPriority.Name(attributes_value.priority)}]")
        )

    def __str__(self):
        return "UAttributesValidator.Request"


class Response(UAttributesValidator):
    """
    Implements validations for UAttributes that define a message that is
    meant for an RPC response.
    """

    def validate_type(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validates that attributes for a message meant for an RPC
        response has the correct type.<br><br>
        @param attributes_value:UAttributes object containing the
        message type to validate.
        @return:Returns a  ValidationResult that is success or
        failed with a failure message.
        """
        return (
            ValidationResult.success()
            if attributes_value.type == UMessageType.UMESSAGE_TYPE_RESPONSE
            else (ValidationResult.failure(f"Wrong Attribute Type [{UMessageType.Name(attributes_value.type)}]"))
        )

    def validate_sink(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validates that attributes for a message meant for an RPC response
        has a destination sink.<br>In the case of
        an RPC response, the sink is required.<br><br>
        @param attributes_value:UAttributes object containing the sink
        to validate.
        @return:Returns a  ValidationResult that is success or failed
        with a failure message.
        """
        if not attributes_value.HasField("sink") or attributes_value.sink == UUri():
            return ValidationResult.failure("Missing Sink")
        return (
            ValidationResult.success()
            if UriValidator.is_rpc_response(attributes_value.sink)
            else ValidationResult.failure("Invalid Sink Uri")
        )

    def validate_req_id(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validate the correlationId. n the case of an RPC response, the
        correlation id is required.<br><br>
        @param attributes_value:UAttributes object containing the
        correlation id to validate.
        @return:Returns a  ValidationResult that is success or
        failed with a failure message.
        """
        if not attributes_value.HasField("reqid") or attributes_value.reqid == UUID():
            return ValidationResult.failure("Missing correlationId")
        if not UUIDUtils.is_uuid(attributes_value.reqid):
            return ValidationResult.failure("Invalid correlation UUID")
        return ValidationResult.success()

    def validate_priority(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validate the priority value to ensure it is one of the known CS values

        @param attributes_value Attributes object containing the Priority to validate.
        @return Returns a ValidationResult that is success or failed with a failure message.
        """

        return (
            ValidationResult.success()
            if attributes_value.priority >= UPriority.UPRIORITY_CS4
            else ValidationResult.failure(f"Invalid UPriority [{UPriority.Name(attributes_value.priority)}]")
        )

    def __str__(self):
        return "UAttributesValidator.Response"


class Notification(UAttributesValidator):
    """
    Implements validations for UAttributes that define a message that is
    meant for notifications.
    """

    def validate_type(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validates that attributes for a message meant for Notification
        state changes has the correct type.<br><br>
        @param attributes_value:UAttributes object containing the message
        type to validate.
        @return:Returns a ValidationResult that is success or failed with
        a failure message.
        """
        return (
            ValidationResult.success()
            if attributes_value.type == UMessageType.UMESSAGE_TYPE_NOTIFICATION
            else (ValidationResult.failure(f"Wrong Attribute Type [{UMessageType.Name(attributes_value.type)}]"))
        )

    def validate_sink(self, attributes_value: UAttributes) -> ValidationResult:
        """
        Validates that attributes for a message meant for an RPC response
        has a destination sink.<br>In the case of
        an RPC response, the sink is required.<br><br>
        @param attributes_value:UAttributes object containing the
        sink to validate.
        @return:Returns a  ValidationResult that is success or
        failed with a failure message.
        """
        if not attributes_value.HasField("sink") or attributes_value.sink == UUri():
            return ValidationResult.failure("Missing Sink")
        return (
            ValidationResult.success()
            if UriValidator.is_default_resource_id(attributes_value.sink)
            else ValidationResult.failure("Invalid Sink Uri")
        )

    def __str__(self):
        return "UAttributesValidator.Notification"


class Validators(Enum):
    """
    Validators Factory. <br>Example: UAttributesValidator
    validateForPublishMessageType =
    UAttributesValidator.Validators.PUBLISH.validator()
    """

    PUBLISH = Publish()
    REQUEST = Request()
    RESPONSE = Response()
    NOTIFICATION = Notification()

    def validator(self):
        return self.value
