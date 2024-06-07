"""
SPDX-FileCopyrightText: Copyright (c) 2023 Contributors to the 
Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SPDX-FileType: SOURCE
SPDX-License-Identifier: Apache-2.0
"""


from abc import ABC, abstractmethod
from enum import Enum

from cloudevents.http import CloudEvent

from uprotocol.cloudevent.factory.ucloudevent import UCloudEvent
from uprotocol.proto.uprotocol.v1.uattributes_pb2 import UMessageType
from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri
from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.validation.validationresult import ValidationResult


class CloudEventValidator(ABC):

    @staticmethod
    def get_validator(ce: CloudEvent):
        """
        Obtain a CloudEventValidator according to the type
        attribute in the CloudEvent.<br><br>
        @param ce:The CloudEvent with the type attribute.
        @return:Returns a CloudEventValidator according to the
        type attribute in the CloudEvent.
        """
        cloud_event_type = ce.get_attributes().get("type")

        if cloud_event_type is None:
            return Validators.PUBLISH.validator()

        message_type = UCloudEvent.get_message_type(cloud_event_type)

        if message_type == UMessageType.UMESSAGE_TYPE_RESPONSE:
            return Validators.RESPONSE.validator()
        elif message_type == UMessageType.UMESSAGE_TYPE_REQUEST:
            return Validators.REQUEST.validator()
        elif message_type == UMessageType.UMESSAGE_TYPE_NOTIFICATION:
            return Validators.NOTIFICATION.validator()
        else:
            return Validators.PUBLISH.validator()

    def validate(self, ce: CloudEvent) -> ValidationResult:
        """
        Validate the CloudEvent. A CloudEventValidator instance is obtained
        according to the type attribute on the CloudEvent.<br><br> @param
        ce:The CloudEvent to validate. @return:Returns a ValidationResult with
        success or a ValidationResult with failure containing all the errors
        that were found.
        """

        validation_results = [
            self.validate_version(ce),
            self.validate_id(ce),
            self.validate_source(ce),
            self.validate_type(ce),
            self.validate_sink(ce),
        ]

        error_messages = [
            result.get_message()
            for result in validation_results
            if not result.is_success()
        ]
        error_message = ",".join(error_messages)

        if not error_message:
            return ValidationResult.success()
        else:
            return ValidationResult.failure(",".join(error_messages))

    @staticmethod
    def validate_version(ce: CloudEvent) -> ValidationResult:
        return CloudEventValidator.validate_version_spec(
            ce.get_attributes().get("specversion")
        )

    @staticmethod
    def validate_version_spec(version) -> ValidationResult:
        if version == "1.0":
            return ValidationResult.success()
        else:
            return ValidationResult.failure(
                f"Invalid CloudEvent version [{version}]. CloudEvent version must be 1.0."
            )

    @staticmethod
    def validate_id(ce: CloudEvent) -> ValidationResult:
        id = UCloudEvent.extract_string_value_from_attributes("id", ce)
        return (
            ValidationResult.success()
            if UCloudEvent.is_cloud_event_id(ce)
            else ValidationResult.failure(
                f"Invalid CloudEvent Id [{id}]. CloudEvent Id must be of type UUIDv8."
            )
        )

    @abstractmethod
    def validate_source(self, ce: CloudEvent):
        """
        Validate the source value of a cloud event.<br><br>
        @param ce:The cloud
        event containing the source to validate.
        @return:Returns the
        ValidationResult containing a success or a failure with the error
        message.
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def validate_type(self, ce: CloudEvent):
        """
        Validate the type value of a cloud event.<br><br>
        @param ce:The cloud
        event containing the type to validate.
        @return:Returns the
        ValidationResult containing a success or a failure with the error
        message.
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def validate_sink(self, ce: CloudEvent) -> ValidationResult:
        """
        Validate the sink value of a cloud event in the default scenario where
        the sink attribute is optional.<br><br>
        @param ce:The cloud event
        containing the sink to validate.
        @return:Returns the ValidationResult
        containing a success or a failure with the error message.
        """
        raise NotImplementedError("Subclasses must implement this method")

class Publish(CloudEventValidator):
    """
    Implements Validations for a CloudEvent of type Publish.
    """

    def validate_source(self, cl_event: CloudEvent) -> ValidationResult:
        source = cl_event.get_attributes().get("source")
        return (
            ValidationResult.success()
            if UriValidator.is_topic(UriSerializer().deserialize(source)) 
            else ValidationResult.failure(f"Invalid Publish type CloudEvent source [{source}].")
        )

    def validate_type(self, cl_event: CloudEvent) -> ValidationResult:
        type = cl_event.get_attributes().get("type")
        return (
            ValidationResult.success()
            if type == "pub.v1"
            else ValidationResult.failure(
                f"Invalid CloudEvent type [{type}]. CloudEvent of type Publish must have a type of 'pub.v1'",
            )
        )

    def validate_sink(self, cl_event: CloudEvent) -> ValidationResult:
        return (
            ValidationResult.failure("Publish should not have a sink")
            if UCloudEvent.get_sink(cl_event)
            else ValidationResult.success()
        )

    def __str__(self) -> str:
        return "CloudEventValidator.Publish"


class Notification(Publish):
    """
    Implements Validations for a CloudEvent of type Publish that behaves as a
    Notification, meaning it must have a sink.
    """

    def validate_sink(self, cl_event: CloudEvent) -> ValidationResult:
        maybe_sink = UCloudEvent.get_sink(cl_event)
        if not maybe_sink:
            return ValidationResult.failure(
                "Invalid CloudEvent sink. Notification CloudEvent sink must be an  uri.",
            )
        sink = maybe_sink
        return (
            ValidationResult.success()
            if UriValidator.is_default_resource_id(UriSerializer().deserialize(sink))
            else ValidationResult.failure(f"Invalid Notification type CloudEvent sink [{sink}].")
        )

    def validate_source(self, cl_event: CloudEvent) -> ValidationResult:
        source = UCloudEvent.get_source(cl_event)
        return (
            ValidationResult.success()
            if UriValidator.is_topic(UriSerializer().deserialize(source))
            else ValidationResult.failure(f"Invalid Notification type CloudEvent source [{source}].")
        )

    def validate_type(self, cl_event: CloudEvent) -> ValidationResult:
        return (
            ValidationResult.success()
            if UCloudEvent.get_type(cl_event) == "not.v1"
            else ValidationResult.failure(
                f"Invalid CloudEvent type [{UCloudEvent.get_type(cl_event)}]. " +
                "CloudEvent of type Notification must have a type of 'not.v1'",
            )
        )

    def __str__(self):
        return "CloudEventValidator.Notification"


class Request(CloudEventValidator):
    """
    Implements Validations for a CloudEvent for RPC Request.
    """

    def validate_source(self, cl_event: CloudEvent) -> ValidationResult:
        source = cl_event.get_attributes().get("source")
        return (
            ValidationResult.success()
            if UriValidator.is_topic(UriSerializer().deserialize(source))
            else ValidationResult.failure(f"Invalid RPC Request type CloudEvent source [{source}].")
        )

    def validate_sink(self, cl_event: CloudEvent) -> ValidationResult:
        sink = UCloudEvent.get_sink(cl_event)
        if not sink:
            return ValidationResult.failure("Invalid CloudEvent sink. RPC Request CloudEvent sink must be an uri.")
        
        return (
            ValidationResult.success()
            if UriValidator.is_rpc_method(UriSerializer().deserialize(sink))
            else ValidationResult.failure(f"Invalid RPC Request type CloudEvent sink [{sink}].")
        )

    def validate_type(self, cl_event: CloudEvent) -> ValidationResult:
        type = cl_event.get_attributes().get("type")

        return (
            ValidationResult.success()
            if type == "req.v1"
            else ValidationResult.failure(
                f"Invalid CloudEvent type [{type}]. CloudEvent of type Request must have a type of 'req.v1'",
            )
        )

    def __str__(self):
        return "CloudEventValidator.Request"


class Response(CloudEventValidator):
    """
    Implements Validations for a CloudEvent for RPC Response.
    """

    def validate_source(self, cl_event: CloudEvent) -> ValidationResult:
        source = cl_event.get_attributes().get("source")
        return (
            ValidationResult.success()
            if UriValidator.is_rpc_method(UriSerializer().deserialize(source))
            else ValidationResult.failure(f"Invalid RPC Response type CloudEvent source [{source}].")
        )

    def validate_sink(self, cl_event) -> ValidationResult:
        sink = UCloudEvent.get_sink(cl_event)
        if not sink:
            return ValidationResult.failure("Invalid CloudEvent sink. RPC Response CloudEvent sink must be an uri.")
        return (
            ValidationResult.success()
            if UriValidator.is_rpc_response(UriSerializer().deserialize(sink))
            else ValidationResult.failure(f"Invalid RPC Response type CloudEvent sink [{sink}].")
        )

    def validate_type(self, cl_event: CloudEvent) -> ValidationResult:
        type = cl_event.get_attributes().get("type")

        return (
            ValidationResult.success()
            if type == "res.v1"
            else ValidationResult.failure(
                f"Invalid CloudEvent type [{type}]. CloudEvent of type Response must have a type of 'res.v1'",
            )
        )

    def __str__(self):
        return "CloudEventValidator.Response"


class Validators(Enum):
    """
    Enum that hold the implementations of CloudEventValidator according to
    type.
    """

    PUBLISH = Publish()
    NOTIFICATION = Notification()
    REQUEST = Request()
    RESPONSE = Response()

    def __init__(self, cloud_event_validator: CloudEventValidator):
        self.cloud_event_validator = cloud_event_validator

    def validator(self) -> CloudEventValidator:
        return self.cloud_event_validator
