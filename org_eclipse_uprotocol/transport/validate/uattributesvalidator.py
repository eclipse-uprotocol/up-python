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

from abc import abstractmethod
from datetime import datetime
from enum import Enum

from org_eclipse_uprotocol.transport.datamodel.uattributes import UAttributes
from org_eclipse_uprotocol.transport.datamodel.umessagetype import UMessageType
from org_eclipse_uprotocol.transport.datamodel.ustatus import UStatus, Code
from org_eclipse_uprotocol.uri.validator.urivalidator import UriValidator
from org_eclipse_uprotocol.uuid.factory.uuidutils import UUIDUtils


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
        elif attribute.type == UMessageType.RESPONSE:
            return Validators.RESPONSE.validator()
        elif attribute.type == UMessageType.REQUEST:
            return Validators.REQUEST.validator()
        else:
            return Validators.PUBLISH.validator()

    @staticmethod
    def validate_id(attr: UAttributes) -> UStatus:
        """
        Validate the id attribute, it is required.<br><br>
        @param attr:UAttributes object containing the id to validate.
        @return:Returns a UStatus that is success or failed with a failure message.
        """
        attr_id = attr.id
        if UUIDUtils.isuuid(attr_id):
            return UStatus.ok()
        else:
            return UStatus.failed_with_msg_and_code("Invalid UUID [{}]".format(attr_id), Code.INVALID_ARGUMENT)

    @staticmethod
    def validate_priority(attr: UAttributes) -> UStatus:
        """
        Validate the UPriority since it is required.<br><br>
        @param attr:UAttributes object containing the message priority to validate.
        @return:Returns a UStatus that is success or failed with a failure message.
        """
        return UStatus.failed_with_msg_and_code("Priority is missing",
                                                Code.INVALID_ARGUMENT) if attr.priority is None else UStatus.ok()

    @staticmethod
    def validate_ttl(attr: UAttributes) -> UStatus:
        """
        Validate the time to live configuration. If the UAttributes does not contain a time to live then the UStatus
        is ok.<br><br>
        @param attr:UAttributes object containing the message time to live configuration to validate.
        @return:Returns a UStatus that is success or failed with a failure message.
        """
        if attr.ttl and attr.ttl <= 0:
            return UStatus.failed_with_msg_and_code(f"Invalid TTL [{attr.ttl}]", Code.INVALID_ARGUMENT)
        else:
            return UStatus.ok()

    @staticmethod
    def validate_sink(attr: UAttributes) -> UStatus:
        """
        Validate the sink UriPart for the default case. If the UAttributes does not contain a sink then the UStatus
        is ok.<br><br>
        @param attr:UAttributes object containing the sink to validate.
        @return:Returns a UStatus that is success or failed with a failure message.
        """
        return UriValidator.validate(attr.sink) if attr.sink else UStatus.ok()

    @staticmethod
    def validate_permission_level(attr: UAttributes) -> UStatus:
        """
        Validate the permissionLevel for the default case. If the UAttributes does not contain a permission level
        then the UStatus is ok.<br><br>
        @param attr:UAttributes object containing the permission level to validate.
        @return:Returns a UStatus indicating if the permissionLevel is valid or not.
        """
        if attr.plevel and attr.plevel > 0:
            return UStatus.ok()
        else:
            return UStatus.failed_with_msg_and_code("Invalid Permission Level", Code.INVALID_ARGUMENT)

    @staticmethod
    def validate_comm_status(attr: UAttributes) -> UStatus:
        """
        Validate the commStatus for the default case. If the UAttributes does not contain a comm status then the
        UStatus is ok.<br><br>
        @param attr:UAttributes object containing the comm status to validate.
        @return:Returns a UStatus that is success or failed with a failure message.
        """
        return UStatus.ok() if attr.commstatus else UStatus.failed_with_msg_and_code(
            "Invalid Communication Status Code", Code.INVALID_ARGUMENT)

    @staticmethod
    def validate_req_id(attr: UAttributes) -> UStatus:
        """
        Validate the correlationId for the default case. If the UAttributes does not contain a request id then the
        UStatus is ok.<br><br>
        @param attr:Attributes object containing the request id to validate.
        @return:Returns a UStatus that is success or failed with a failure message.
        """
        return UStatus.failed_with_msg_and_code("Invalid UUID",
                                                Code.INVALID_ARGUMENT) if attr.reqid and not UUIDUtils.isuuid(
            attr.reqid) else UStatus.ok()

    @abstractmethod
    def validate_type(self, attr: UAttributes):
        """
        Validate the UMessageType attribute, it is required.<br><br>
        @param attr:UAttributes object containing the message type to validate.
        @return:Returns a UStatus that is success or failed with a failure message.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate(self, attributes: UAttributes):
        """
        Take a UAttributes object and run validations.<br><br>
        @param attributes:The UAttriubes to validate.
        @return:Returns a UStatus that is success or failed with a message containing all validation errors
        for invalid configurations.
        """
        error_messages = [self.validate_id(attributes), self.validate_type(attributes),
                          self.validate_priority(attributes), self.validate_ttl(attributes),
                          self.validate_sink(attributes), self.validate_comm_status(attributes),
                          self.validate_permission_level(attributes), self.validate_req_id(attributes)]

        error_messages = [status.msg() for status in error_messages if
                          status and status.getCode() == Code.INVALID_ARGUMENT]

        if error_messages:
            return UStatus.failed_with_msg_and_code(",".join(error_messages), Code.INVALID_ARGUMENT)
        else:
            return UStatus.ok()

    def is_expired(self, u_attributes: UAttributes):
        """
        Indication if the Payload with these UAttributes is expired.<br><br>
        @param u_attributes:UAttributes with time to live value.
        @return: Returns a UStatus that is success meaning not expired or failed with a validation message or
        expiration.
        """
        maybe_ttl = u_attributes.ttl
        maybe_time = UUIDUtils.getTime(u_attributes.id)

        if maybe_time is None:
            return UStatus.failed_with_msg_and_code("Invalid Time", Code.INVALID_ARGUMENT)

        if maybe_ttl is None:
            return UStatus.ok_with_ack_id("Not Expired")

        ttl = maybe_ttl
        if ttl <= 0:
            return UStatus.ok_with_ack_id("Not Expired")
        delta = int((datetime.now() - maybe_time).total_seconds() * 1000)
        return UStatus.failed_with_msg_and_code("Payload is expired",
                                                Code.DEADLINE_EXCEEDED) if delta >= ttl else UStatus.ok_with_ack_id(
            "Not Expired")


class Publish(UAttributesValidator):
    """
     Implements validations for UAttributes that define a message that is meant for publishing state changes.
    """

    def validate_type(self, attributes_value: UAttributes) -> UStatus:
        """
        Validates that attributes for a message meant to publish state changes has the correct type.<br><br>
        @param attributes_value:UAttributes object containing the message type to validate.
        @return:Returns a UStatus that is success or failed with a failure message.
        """
        return UStatus.ok() if attributes_value.type == UMessageType.PUBLISH else UStatus.failed_with_msg_and_code(
            f"Wrong Attribute Type [{attributes_value.type}]", Code.INVALID_ARGUMENT)

    def __str__(self):
        return "UAttributesValidator.Publish"


class Request(UAttributesValidator):
    """
    Implements validations for UAttributes that define a message that is meant for an RPC request.
    """

    def validate_type(self, attributes_value: UAttributes) -> UStatus:
        """
        Validates that attributes for a message meant for an RPC request has the correct type.<br><br>
        @param attributes_value:UAttributes object containing the message type to validate.
        @return:Returns a UStatus that is success or failed with a failure message.
        """
        return UStatus.ok() if attributes_value.type == UMessageType.REQUEST else UStatus.failed_with_msg_and_code(
            f"Wrong Attribute Type [{attributes_value.type}]", Code.INVALID_ARGUMENT)

    def validate_sink(self, attributes_value: UAttributes) -> UStatus:
        """
        Validates that attributes for a message meant for an RPC request has a destination sink.<br><br> In the case
        of an RPC request, the sink is required.
        @param attributes_value:UAttributes object containing the sink to validate.
        @return:Returns a UStatus that is success or failed with a failure message.
        """
        return UriValidator.validate_rpc_response(
            attributes_value.sink) if attributes_value.sink else UStatus.failed_with_msg_and_code("Missing Sink",
                                                                                                  Code.INVALID_ARGUMENT)

    def validate_ttl(self, attributes_value: UAttributes) -> UStatus:
        """
        Validate the time to live configuration.<br>In the case of an RPC request, the time to live is required.<br><br>
        @param attributes_value:UAttributes object containing the time to live to validate.
        @return:Returns a UStatus that is success or failed with a failure message.
        """
        return UStatus.ok() if attributes_value.ttl and attributes_value.ttl > 0 else UStatus.failed_with_msg_and_code(
            "Missing TTL", Code.INVALID_ARGUMENT)

    def __str__(self):
        return "UAttributesValidator.Request"


class Response(UAttributesValidator):
    """
    Implements validations for UAttributes that define a message that is meant for an RPC response.
    """

    def validate_type(self, attributes_value: UAttributes) -> UStatus:
        """
        Validates that attributes for a message meant for an RPC response has the correct type.<br><br>
        @param attributes_value:UAttributes object containing the message type to validate.
        @return:Returns a UStatus that is success or failed with a failure message.
        """
        return UStatus.ok() if attributes_value.type == UMessageType.RESPONSE else UStatus.failed_with_msg_and_code(
            f"Wrong Attribute Type [{attributes_value.type}]", Code.INVALID_ARGUMENT)

    def validate_sink(self, attributes_value: UAttributes) -> UStatus:
        """
        Validates that attributes for a message meant for an RPC response has a destination sink.<br>In the case of
        an RPC response, the sink is required.<br><br>
        @param attributes_value:UAttributes object containing the sink to validate.
        @return:Returns a UStatus that is success or failed with a failure message.
        """
        return UriValidator.validate_rpc_method(
            attributes_value.sink) if attributes_value.sink else UStatus.failed_with_msg_and_code("Missing Sink",
                                                                                                  Code.INVALID_ARGUMENT)

    def validate_req_id(self, attributes_value: UAttributes) -> UStatus:
        """
        Validate the correlationId. n the case of an RPC response, the correlation id is required.<br><br>
        @param attributes_value:UAttributes object containing the correlation id to validate.
        @return:Returns a UStatus that is success or failed with a failure message.
        """
        return UStatus.ok() if attributes_value.reqid and UUIDUtils.isuuid(
            attributes_value.reqid) else UStatus.failed_with_msg_and_code("Missing correlationId",
                                                                          Code.INVALID_ARGUMENT)

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
