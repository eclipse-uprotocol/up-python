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


from abc import ABC, abstractmethod
from enum import Enum

from cloudevents.http import CloudEvent

from uprotocol.cloudevent.factory.ucloudevent import UCloudEvent
from uprotocol.proto.uattributes_pb2 import UMessageType
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
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
        self.validate_source(ce)
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

    def validate_sink(self, ce: CloudEvent) -> ValidationResult:
        """
        Validate the sink value of a cloud event in the default scenario where
        the sink attribute is optional.<br><br>
        @param ce:The cloud event
        containing the sink to validate.
        @return:Returns the ValidationResult
        containing a success or a failure with the error message.
        """
        maybe_sink = UCloudEvent.get_sink(ce)
        if maybe_sink:
            sink = maybe_sink
            check_sink = self.validate_u_entity_uri(sink)
            if check_sink.is_failure():
                return ValidationResult.failure(
                    f"Invalid CloudEvent sink [{sink}]. {check_sink.get_message()}"
                )

        return ValidationResult.success()

    @staticmethod
    def validate_u_entity_uri(uri: str) -> ValidationResult:
        """
        Validate an  UriPart for an  Software Entity must have an authority in
        the case of a microRemote uri, and must contain the name of the
        USE.<br><br>
        @param uri:uri string to validate.
        @return:Returns the
        ValidationResult containing a success or a failure with the error
        message.
        """
        uri = LongUriSerializer().deserialize(uri)
        return CloudEventValidator.validate_u_entity_uri_from_UURI(uri)

    @staticmethod
    def validate_u_entity_uri_from_UURI(uri: UUri) -> ValidationResult:
        return UriValidator.validate(uri)

    @staticmethod
    def validate_topic_uri(uri: str) -> ValidationResult:
        """
        Validate a UriPart that is to be used as a topic in publish scenarios
        for events such as publish, file and notification.<br><br>
        @param uri:String UriPart to validate
        @return:Returns the
        ValidationResult containing a success or a failure with the error
        message.
        """
        Uri = LongUriSerializer().deserialize(uri)
        return CloudEventValidator.validate_topic_uri_from_UURI(Uri)

    @staticmethod
    def validate_topic_uri_from_UURI(uri: UUri) -> ValidationResult:
        """
        Validate a UriPart that is to be used as a topic in publish scenarios
        for events such as publish, file and notification.<br><br>
        @param uri:
        UriPart to validate.
        @return:Returns the ValidationResult containing a
        success or a failure with the error message.
        """
        validationResult = CloudEventValidator.validate_u_entity_uri_from_UURI(
            uri
        )
        if validationResult.is_failure():
            return validationResult

        u_resource = uri.resource
        if not u_resource.name:
            return ValidationResult.failure(
                "UriPart is missing uResource name."
            )

        if not u_resource.message:
            return ValidationResult.failure(
                "UriPart is missing Message information."
            )

        return ValidationResult.success()

    @staticmethod
    def validate_rpc_topic_uri(uri: str) -> ValidationResult:
        """
        Validate a UriPart that is meant to be used as the application response
        topic for rpc calls. <br>Used in Request source values and Response
        sink values.<br><br>
        @param uri:String UriPart to validate.
        @return:Returns the ValidationResult containing a success or a failure
        with the error message.
        """
        Uri = LongUriSerializer().deserialize(uri)
        return CloudEventValidator.validate_rpc_topic_uri_from_uuri(Uri)

    @staticmethod
    def validate_rpc_topic_uri_from_uuri(uri: UUri) -> ValidationResult:
        """
        Validate a UriPart that is meant to be used as the application response
        topic for rpc calls. <br>Used in Request source values and Response
        sink values.<br><br>
        @param uri:UriPart to validate.
        @return:Returns
        the ValidationResult containing a success or a failure with the error
        message.
        """
        validationResult = CloudEventValidator.validate_u_entity_uri_from_UURI(
            uri
        )
        if validationResult.is_failure():
            return ValidationResult.failure(
                f"Invalid RPC uri application response topic. {validationResult.get_message()}",
            )

        u_resource = uri.resource
        topic = (
            f"{u_resource.name}.{u_resource.instance}"
            if u_resource.instance
            else f"{u_resource.name}"
        )
        if topic != "rpc.response":
            return ValidationResult.failure(
                "Invalid RPC uri application response topic. UriPart is missing rpc.response.",
            )

        return ValidationResult.success()

    @staticmethod
    def validate_rpc_method(uri: str) -> ValidationResult:
        """
        Validate a UriPart that is meant to be used as an RPC method URI. Used in Request sink values and Response
        source values.<br><br>
        @param uri: String UriPart to validate
        @return:Returns the ValidationResult containing a success or a failure with the error message.
        """
        uuri = LongUriSerializer().deserialize(uri)
        validationResult = CloudEventValidator.validate_u_entity_uri_from_UURI(
            uuri
        )
        if validationResult.is_failure():
            return ValidationResult.failure(
                f"Invalid RPC method uri. {validationResult.get_message()}"
            )

        if not UriValidator.is_rpc_method(uuri):
            return ValidationResult.failure(
                "Invalid RPC method uri. UriPart should be the method to be called, or method from response.",
            )

        return ValidationResult.success()


class Publish(CloudEventValidator):
    """
    Implements Validations for a CloudEvent of type Publish.
    """

    def validate_source(self, cl_event: CloudEvent) -> ValidationResult:
        source = cl_event.get_attributes().get("source")
        check_source = self.validate_topic_uri(source)
        if check_source.is_failure():
            return ValidationResult.failure(
                f"Invalid Publish type CloudEvent source [{source}]. {check_source.get_message()}",
            )

        return ValidationResult.success()

    def validate_type(self, cl_event: CloudEvent) -> ValidationResult:
        type = cl_event.get_attributes().get("type")
        return (
            ValidationResult.success()
            if type == "pub.v1"
            else ValidationResult.failure(
                f"Invalid CloudEvent type [{type}]. CloudEvent of type Publish must have a type of 'pub.v1'",
            )
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
        else:
            sink = maybe_sink
            check_sink = self.validate_u_entity_uri(sink)
            if check_sink.is_failure():
                return ValidationResult.failure(
                    f"Invalid Notification type CloudEvent sink [{sink}]. {check_sink.get_message()}",
                )

        return ValidationResult.success()

    def validate_source(self, cl_event: CloudEvent) -> ValidationResult:
        source = UCloudEvent.get_source(cl_event)
        check_source = self.validate_topic_uri(source)
        if check_source.is_failure():
            return ValidationResult.failure(
                f"Invalid Notification type CloudEvent source [{source}], {check_source.get_message()}",
            )
        return ValidationResult.success()

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
        check_source = self.validate_rpc_topic_uri(source)
        if check_source.is_failure():
            return ValidationResult.failure(
                f"Invalid RPC Request CloudEvent source [{source}]. {check_source.get_message()}",
            )
        return ValidationResult.success()

    def validate_sink(self, cl_event: CloudEvent) -> ValidationResult:
        maybe_sink = UCloudEvent.get_sink(cl_event)
        if not maybe_sink:
            return ValidationResult.failure(
                "Invalid RPC Request CloudEvent sink. Request CloudEvent sink must be uri for the method to be called."
            )
        else:
            sink = maybe_sink
            check_sink = self.validate_rpc_method(sink)
            if check_sink.is_failure():
                return ValidationResult.failure(
                    f"Invalid RPC Request CloudEvent sink [{sink}]. {check_sink.get_message()}",
                )

        return ValidationResult.success()

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
        check_source = self.validate_rpc_method(source)
        if check_source.is_failure():
            return ValidationResult.failure(
                f"Invalid RPC Response CloudEvent source [{source}]. {check_source.get_message()}",
            )

        return ValidationResult.success()

    def validate_sink(self, cl_event) -> ValidationResult:
        maybe_sink = UCloudEvent.get_sink(cl_event)
        if not maybe_sink:
            return ValidationResult.failure(
                "Invalid CloudEvent sink. Response CloudEvent sink must be uri the destination of the response.",
            )
        else:
            sink = maybe_sink
            check_sink = self.validate_rpc_topic_uri(sink)
            if check_sink.is_failure():
                return ValidationResult.failure(
                    f"Invalid RPC Response CloudEvent sink [{sink}]. {check_sink.get_message()}",
                )

        return ValidationResult.success()

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
