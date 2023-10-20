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

import time
from abc import abstractmethod
from enum import Enum

from org_eclipse_uprotocol.transport.datamodel.uattributes import UAttributes
from org_eclipse_uprotocol.transport.datamodel.umessagetype import UMessageType
from org_eclipse_uprotocol.transport.datamodel.ustatus import UStatus, Code
from org_eclipse_uprotocol.uri.validator.urivalidator import UriValidator
from org_eclipse_uprotocol.uuid.factory.uuidutils import UUIDUtils


class UAttributesValidator:
    @staticmethod
    def get_validator(attribute: UAttributes):
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
        attr_id = attr.id
        try:
            if UUIDUtils.isuuid(attr_id):
                return UStatus.ok()
            else:
                return UStatus.failed_with_msg_and_code(f"Invalid UUID [{attr_id}]", Code.INVALID_ARGUMENT)
        except Exception as e:
            return UStatus.failed_with_msg_and_code(f"Invalid UUID [{attr_id}] [{str(e)}]", Code.INVALID_ARGUMENT)

    @staticmethod
    def validate_priority(attr: UAttributes) -> UStatus:
        return UStatus.failed_with_msg_and_code("Priority is missing",
                                                Code.INVALID_ARGUMENT) if attr.priority is None else UStatus.ok()

    @staticmethod
    def validate_ttl(attr: UAttributes) -> UStatus:
        if attr.ttl and attr.ttl <= 0:
            return UStatus.failed_with_msg_and_code(f"Invalid TTL [{attr.ttl}]", Code.INVALID_ARGUMENT)
        else:
            return UStatus.ok()

    @staticmethod
    def validate_sink(attr: UAttributes) -> UStatus:
        return UriValidator.validate(attr.sink) if attr.sink else UStatus.ok()

    @staticmethod
    def validate_permission_level(attr: UAttributes) -> UStatus:
        if attr.plevel and attr.plevel > 0:
            return UStatus.ok()
        else:
            return UStatus.failed_with_msg_and_code("Invalid Permission Level", Code.INVALID_ARGUMENT)

    @staticmethod
    def validate_comm_status(attr: UAttributes) -> UStatus:
        return UStatus.ok() if attr.commstatus else UStatus.failed_with_msg_and_code(
            "Invalid Communication Status Code", Code.INVALID_ARGUMENT)

    @staticmethod
    def validate_req_id(attr: UAttributes) -> UStatus:
        return UStatus.failed_with_msg_and_code("Invalid UUID",
                                                Code.INVALID_ARGUMENT) if attr.reqid and not UUIDUtils.isuuid(
            attr.reqid) else UStatus.ok()

    @abstractmethod
    def validate_type(self, attr: UAttributes):
        raise NotImplementedError("Subclasses must implement this method.")

    def validate(self, attributes: UAttributes):
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

    def is_expired(u_attributes: UAttributes):
        try:
            maybe_ttl = u_attributes.ttl
            maybe_time = UUIDUtils.getTime(u_attributes.id)

            if maybe_time is None:
                return UStatus.failed_with_msg_and_code("Invalid Time", Code.INVALID_ARGUMENT)

            if maybe_ttl is None or maybe_ttl <= 0:
                return UStatus.ok_with_ack_id("Not Expired")

            delta = time.time() * 1000 - maybe_time

            return UStatus.failed_with_msg_and_code("Payload is expired",
                                                    Code.DEADLINE_EXCEEDED) if delta >= maybe_ttl else UStatus.ok_with_ack_id(
                "Not Expired")
        except Exception:
            return UStatus.ok_with_ack_id("Not Expired")


class Publish(UAttributesValidator):
    def validate_type(self, attributes_value: UAttributes) -> UStatus:
        return UStatus.ok() if attributes_value.type == UMessageType.PUBLISH else UStatus.failed_with_msg_and_code(
            f"Wrong Attribute Type [{attributes_value.type}]", Code.INVALID_ARGUMENT)

    def __str__(self):
        return "UAttributesValidator.Publish"


class Request(UAttributesValidator):
    def validate_type(self, attributes_value: UAttributes) -> UStatus:
        return UStatus.ok() if attributes_value.type == UMessageType.REQUEST else UStatus.failed_with_msg_and_code(
            f"Wrong Attribute Type [{attributes_value.type}]", Code.INVALID_ARGUMENT)

    def validate_sink(self, attributes_value: UAttributes) -> UStatus:
        return UriValidator.validate_rpc_response(
            attributes_value.sink) if attributes_value.sink else UStatus.failed_with_msg_and_code("Missing Sink",
                                                                                                  Code.INVALID_ARGUMENT)

    def validate_ttl(self, attributes_value: UAttributes) -> UStatus:
        return UStatus.ok() if attributes_value.ttl and attributes_value.ttl > 0 else UStatus.failed_with_msg_and_code(
            "Missing TTL", Code.INVALID_ARGUMENT)

    def __str__(self):
        return "UAttributesValidator.Request"


class Response(UAttributesValidator):
    def validate_type(self, attributes_value: UAttributes) -> UStatus:
        return UStatus.ok() if attributes_value.type == UMessageType.RESPONSE else UStatus.failed_with_msg_and_code(
            f"Wrong Attribute Type [{attributes_value.type}]", Code.INVALID_ARGUMENT)

    def validate_sink(self, attributes_value: UAttributes) -> UStatus:
        return UriValidator.validate_rpc_method(
            attributes_value.sink) if attributes_value.sink else UStatus.failed_with_msg_and_code("Missing Sink",
                                                                                                  Code.INVALID_ARGUMENT)

    def validate_req_id(self, attributes_value: UAttributes) -> UStatus:
        return UStatus.ok() if attributes_value.reqid and UUIDUtils.isuuid(
            attributes_value.reqid) else UStatus.failed_with_msg_and_code("Missing correlationId",
                                                                          Code.INVALID_ARGUMENT)

    def __str__(self):
        return "UAttributesValidator.Response"


class Validators(Enum):
    PUBLISH = Publish()
    REQUEST = Request()
    RESPONSE = Response()

    def validator(self):
        return self.value
