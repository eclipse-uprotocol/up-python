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

from abc import ABC, abstractmethod
from enum import Enum

from cloudevents.sdk.event.v1 import Event
from google.rpc.status_pb2 import Status

from org_eclipse_uprotocol.cloudevent.datamodel.ucloudeventtype import UCloudEventType
from org_eclipse_uprotocol.cloudevent.factory.ucloudevent import UCloudEvent
from org_eclipse_uprotocol.cloudevent.validate.validationresult import ValidationResult
from org_eclipse_uprotocol.uri.datamodel import uuri
from org_eclipse_uprotocol.uri.serializer.longuriserializer import LongUriSerializer


class CloudEventValidator(ABC):
    @staticmethod
    def get_validator(ce: Event):
        cloud_event_type = ce.type
        maybe_type = UCloudEventType(cloud_event_type)
        if maybe_type not in UCloudEventType:
            return Validators.PUBLISH.validator()

        elif maybe_type == UCloudEventType.RESPONSE:
            return Validators.RESPONSE.validator()
        elif maybe_type == UCloudEventType.REQUEST:
            return Validators.REQUEST.validator()
        else:
            return Validators.PUBLISH.validator()

    def validate(self, ce: Event) -> Status:
        validation_results = [self.validate_version(ce), self.validate_id(ce), self.validate_source(ce),
                              self.validate_type(ce), self.validate_sink(ce)]

        error_messages = [result.get_message() for result in validation_results if not result.is_success()]
        error_message = ", ".join(error_messages)

        if not error_message:
            return ValidationResult.success().to_status()
        else:
            return ValidationResult.failure(", ".join(error_messages))

    def validate_version(self, ce: Event) -> ValidationResult:
        return self.validate_version_spec(ce.specversion)

    @staticmethod
    def validate_version_spec(version) -> ValidationResult:
        if version == "1.0":
            return ValidationResult.success()
        else:
            return ValidationResult.failure(f"Invalid CloudEvent version [{version}]. CloudEvent version must be 1.0.")

    def validate_id(self, ce: Event) -> ValidationResult:
        return (ValidationResult.success() if UCloudEvent.is_cloud_event_id(ce) else ValidationResult.failure(
            f"Invalid CloudEvent Id [{ce.id}]. CloudEvent Id must be of type UUIDv8."))

    @abstractmethod
    def validate_source(self, ce: Event):
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def validate_type(self, ce: Event):
        raise NotImplementedError("Subclasses must implement this method")

    def validate_sink(self, ce: Event) -> ValidationResult:
        maybe_sink = UCloudEvent.get_sink(ce)
        if maybe_sink:
            sink = maybe_sink
            check_sink = self.validate_u_entity_uri(sink)
            if check_sink.is_failure():
                return ValidationResult.failure(f"Invalid CloudEvent sink [{sink}]. {check_sink.get_message()}")

        return ValidationResult.success()

    @staticmethod
    def validate_u_entity_uri(uri: str) -> ValidationResult:  # from uri string
        # UUri
        # Uri = LongUriSerializer.instance().deserialize(uri)
        # return validateUEntityUri(Uri)
        uri = LongUriSerializer().deserialize(uri)
        # Uri = UriFactory.parse_from_uri(uri)
        return CloudEventValidator.validate_u_entity_uri_from_UURI(uri)

    @staticmethod
    def validate_u_entity_uri_from_UURI(uri: uuri) -> ValidationResult:  # from uuri
        u_authority = uri.u_authority
        if u_authority.is_marked_remote:
            if not u_authority.device:
                return ValidationResult.failure("Uri is configured to be remote and is missing uAuthority device name.")

        if not uri.u_entity.name:
            return ValidationResult.failure("Uri is missing uSoftware Entity name.")

        return ValidationResult.success()

    @staticmethod
    def validate_topic_uri(uri: str) -> ValidationResult:  # from uri string
        Uri = LongUriSerializer().deserialize(uri)
        return CloudEventValidator.validate_topic_uri_from_UURI(Uri)

    @staticmethod
    def validate_topic_uri_from_UURI(uri: uuri) -> ValidationResult:  # from uuri
        validationResult = CloudEventValidator.validate_u_entity_uri_from_UURI(uri)
        if validationResult.is_success():
            return validationResult

        u_resource = uri.u_resource
        if not u_resource.name:
            return ValidationResult.failure("Uri is missing uResource name.")

        if not u_resource.message:
            return ValidationResult.failure("Uri is missing Message information.")

        return ValidationResult.success()

    @staticmethod
    def validate_rpc_topic_uri(uri: str) -> ValidationResult:  # from uri string
        Uri = LongUriSerializer.deserialize(uri)
        return CloudEventValidator.validate_rpc_topic_uri_from_uuri(Uri)

    @staticmethod
    def validate_rpc_topic_uri_from_uuri(uri: uuri) -> ValidationResult:  # from uuri
        validationResult = CloudEventValidator.validate_u_entity_uri_from_UURI(uri)
        if validationResult.is_failure():
            return ValidationResult.failure(
                f"Invalid RPC uri application response topic. {validationResult.get_message()}")

        u_resource = uri.u_resource
        topic = f"{u_resource.name}.{u_resource.instance}" if u_resource.instance else f"{u_resource.name}"
        if topic != "rpc.response":
            return ValidationResult.failure("Invalid RPC uri application response topic. Uri is missing rpc.response.")

        return ValidationResult.success()

    @staticmethod
    def validate_rpc_method(uri: str) -> ValidationResult:  # string uri
        Uri = LongUriSerializer.deserialize(uri)
        validationResult = CloudEventValidator.validate_u_entity_uri_from_UURI(Uri)
        if validationResult.is_failure():
            return ValidationResult.failure(f"Invalid RPC method uri. {validationResult.get_message()}")

        u_resource = Uri.u_resource
        if not u_resource.is_rpc_method:
            return ValidationResult.failure(
                "Invalid RPC method uri. Uri should be the method to be called, or method from response.")

        return ValidationResult.success()


class Publish(CloudEventValidator):
    def validate_source(self, cl_event: Event) -> ValidationResult:
        source = cl_event.source
        check_source = self.validate_topic_uri(source)
        if check_source.is_failure():
            return ValidationResult.failure(
                f"Invalid Publish type CloudEvent source [{source}]. {check_source.get_message()}")

        return ValidationResult.success()

    def validate_type(self, cl_event: Event) -> ValidationResult:
        return (ValidationResult.success() if cl_event.type == "pub.v1" else ValidationResult.failure(
            f"Invalid CloudEvent type [{cl_event.type}]. CloudEvent of type Publish must have a type of 'pub.v1'"))

    def __str__(self) -> str:
        return "CloudEventValidator.Publish"


class Notification(Publish):
    def validate_sink(self, cl_event: Event) -> ValidationResult:
        maybe_sink = UCloudEvent.get_sink(cl_event)
        if not maybe_sink:
            return ValidationResult.failure("Invalid CloudEvent sink. Notification CloudEvent sink must be an  uri.")
        else:
            sink = maybe_sink
            check_sink = self.validate_u_entity_uri(sink)
            if check_sink.is_failure():
                return ValidationResult.failure(
                    f"Invalid Notification type CloudEvent sink [{sink}]. {check_sink.get_message()}")

        return ValidationResult.success()

    def __str__(self):
        return "CloudEventValidator.Notification"


class Request(CloudEventValidator):
    def validate_source(self, cl_event: Event) -> ValidationResult:
        source = cl_event.source
        check_source = self.validate_rpc_topic_uri(source)
        if check_source.is_failure():
            return ValidationResult.failure(
                f"Invalid RPC Request CloudEvent source [{source}]. {check_source.get_message()}")
        return ValidationResult.success()

    def validate_sink(self, cl_event: Event) -> ValidationResult:
        maybe_sink = UCloudEvent.get_sink(cl_event)
        if not maybe_sink:
            return ValidationResult.failure(
                "Invalid RPC Request CloudEvent sink. Request CloudEvent sink must be uri for the method to be called.")
        else:
            sink = maybe_sink
            check_sink = self.validate_rpc_method(sink)
            if check_sink.is_failure():
                return ValidationResult.failure(
                    f"Invalid RPC Request CloudEvent sink [{sink}]. {check_sink.get_message()}")

        return ValidationResult.success()

    def validate_type(self, cl_event: Event) -> ValidationResult:
        return (ValidationResult.success() if cl_event.type == "req.v1" else ValidationResult.failure(
            f"Invalid CloudEvent type [{cl_event.type}]. CloudEvent of type Request must have a type of 'req.v1'"))

    def __str__(self):
        return "CloudEventValidator.Request"


class Response(CloudEventValidator):
    def validate_source(self, cl_event: Event) -> ValidationResult:
        source = cl_event.source
        check_source = self.validate_rpc_method(source)
        if check_source.is_failure():
            return ValidationResult.failure(
                f"Invalid RPC Response CloudEvent source [{source}]. {check_source.get_message()}")

        return ValidationResult.success()

    def validate_sink(self, cl_event) -> ValidationResult:
        maybe_sink = UCloudEvent.get_sink(cl_event)
        if not maybe_sink:
            return ValidationResult.failure(
                "Invalid CloudEvent sink. Response CloudEvent sink must be uri the destination of the response.")
        else:
            sink = maybe_sink
            check_sink = self.validate_rpc_topic_uri(sink)
            if check_sink.is_failure():
                return ValidationResult.failure(
                    f"Invalid RPC Response CloudEvent sink [{sink}]. {check_sink.get_message()}")

        return ValidationResult.success()

    def validate_type(self, cl_event: Event) -> ValidationResult:
        return (ValidationResult.success() if cl_event.type == "res.v1" else ValidationResult.failure(
            f"Invalid CloudEvent type [{cl_event.type}]. CloudEvent of type Response must have a type of 'res.v1'"))

    def __str__(self):
        return "CloudEventValidator.Response"


class Validators(Enum):
    PUBLISH = Publish()
    NOTIFICATION = Notification()
    REQUEST = Request()
    RESPONSE = Response()

    def __init__(self, cloud_event_validator: CloudEventValidator):
        self.cloud_event_validator = cloud_event_validator

    def validator(self) -> CloudEventValidator:
        return self.cloud_event_validator
