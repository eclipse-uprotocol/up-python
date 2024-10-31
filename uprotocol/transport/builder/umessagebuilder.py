"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from uprotocol.communication.upayload import UPayload
from uprotocol.transport.validator.uattributesvalidator import UAttributesValidator
from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.uuid.validator.uuidvalidator import Validators
from uprotocol.v1.uattributes_pb2 import (
    UAttributes,
    UMessageType,
    UPriority,
)
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.uuid_pb2 import UUID

SOURCE_ERROR = "source cannot be null."
SINK_ERROR = "sink cannot be null."
REQID_ERROR = "reqid cannot be null."
REQUEST_ERROR = "request cannot be null."
TTL_ERROR = "ttl cannot be null."


class UMessageBuilder:
    """Builder for easy construction of the UAttributes object."""

    @staticmethod
    def publish(source: UUri):
        """Construct a UMessageBuilder for a publish message.

        @param source:   Source address of the message.
        @return Returns the UMessageBuilder with the configured priority.
        """
        if source is None:
            raise ValueError(SOURCE_ERROR)
        # Validate the source
        if not UriValidator.is_topic(source):
            raise ValueError("source must be a topic.")
        return UMessageBuilder(
            source,
            Factories.UPROTOCOL.create(),
            UMessageType.UMESSAGE_TYPE_PUBLISH,
        )

    @staticmethod
    def notification(source: UUri, sink: UUri):
        """Construct a UMessageBuilder for a notification message.

        @param source   Source address of the message.
        @param sink The destination URI.
        @return Returns the UMessageBuilder with the configured priority
        and sink.
        """
        if source is None:
            raise ValueError(SOURCE_ERROR)
        if sink is None:
            raise ValueError(SINK_ERROR)
        # Validate the source and sink
        if not (UriValidator.is_topic(source) and UriValidator.is_rpc_response(sink)):
            raise ValueError("source must be a topic and sink must be a response.")
        return UMessageBuilder(
            source,
            Factories.UPROTOCOL.create(),
            UMessageType.UMESSAGE_TYPE_NOTIFICATION,
        ).with_sink(sink)

    @staticmethod
    def request(source: UUri, sink: UUri, ttl: int):
        """Construct a UMessageBuilder for a request message.

        @param source   Source address of the message.
        @param sink The destination URI.
        @param ttl The time to live in milliseconds.
        @return Returns the UMessageBuilder with the configured priority,
        sink and ttl.
        """
        if source is None:
            raise ValueError(SOURCE_ERROR)
        if sink is None:
            raise ValueError(SINK_ERROR)
        if ttl is None:
            raise ValueError(TTL_ERROR)
        # Validate the source and sink
        if not (UriValidator.is_rpc_method(sink) and UriValidator.is_rpc_response(source)):
            raise ValueError("source must be a response and sink must be an rpc method.")
        # Validate the ttl
        if ttl <= 0:
            raise ValueError("ttl must be greater than 0.")

        return (
            UMessageBuilder(
                source,
                Factories.UPROTOCOL.create(),
                UMessageType.UMESSAGE_TYPE_REQUEST,
            )
            .with_ttl(ttl)
            .with_sink(sink)
        )

    @staticmethod
    def response(source: UUri, sink: UUri, reqid: UUID):  # noqa: N805
        """Construct a UMessageBuilder for a response message.

        @param source   Source address of the message.
        @param sink The destination URI.
        @param reqid The original request UUID used to correlate the
        response to the request.
        @return Returns the UMessageBuilder with the configured source,
        sink, priority, and reqid.
        """
        if source is None:
            raise ValueError(SOURCE_ERROR)
        if sink is None:
            raise ValueError(SINK_ERROR)
        if reqid is None:
            raise ValueError(REQID_ERROR)
        # Validate the source and sink
        if not (UriValidator.is_rpc_response(sink) and UriValidator.is_rpc_method(source)):
            raise ValueError("sink must be a response and source must be an rpc method.")
        if Validators.UPROTOCOL.validator().validate(reqid).code != UCode.OK:
            raise ValueError("reqid is not a valid UUID.")

        return (
            UMessageBuilder(
                source,
                Factories.UPROTOCOL.create(),
                UMessageType.UMESSAGE_TYPE_RESPONSE,
            )
            .with_sink(sink)
            .with_reqid(reqid)
        )

    @staticmethod
    def response_for_request(request: UAttributes):  # noqa: N805
        """Construct a UMessageBuilder for a response message using an
        existing request.
        @param request The original request UAttributes used to correlate
        the response to the request.
        @return Returns the UMessageBuilder with the configured source, sink,
        priority, and reqid.
        """
        if request is None:
            raise ValueError(REQUEST_ERROR)
        if UAttributesValidator.get_validator(request).validate(request).is_failure():
            raise ValueError("request must contain valid request attributes.")
        return (
            UMessageBuilder(
                request.sink,
                Factories.UPROTOCOL.create(),
                UMessageType.UMESSAGE_TYPE_RESPONSE,
            )
            .with_priority(request.priority)
            .with_sink(request.source)
            .with_reqid(request.id)
        )

    def __init__(self, source: UUri, id_val: UUID, type_val: UMessageType):
        """Construct the UMessageBuilder with the configurations that are
        required for every payload transport.

        @param source   Source address of the message.
        @param id_val       Unique identifier for the message.
        @param type_val     Message type such as Publish a state change,

        RPC request or RPC response.
        """
        self.source = source
        self.id = id_val
        self.type = type_val
        self.sink = None
        self.priority = None
        self.ttl = None
        self.plevel = None
        self.commstatus = None
        self.reqid = None
        self.token = None
        self.traceparent = None
        self.format = None
        self.payload = None

    def with_ttl(self, ttl: int):
        """Add the time to live in milliseconds.

        @param ttl the time to live in milliseconds.
        @return Returns the UMessageBuilder with the configured ttl.
        """
        self.ttl = ttl
        return self

    def with_token(self, token: str):
        """Add the authorization token used for TAP.

        @param token the authorization token used for TAP.
        @return Returns the UMessageBuilder with the configured token.
        """
        self.token = token
        return self

    def with_priority(self, priority: UPriority):
        """Add the priority level of the message.

        @param priority the priority level of the message.
        @return Returns the UMessageBuilder with the configured priority.
        """
        self.priority = priority
        return self

    def with_permission_level(self, plevel: int):
        """Add the permission level of the message.

        @param plevel the permission level of the message.
        @return Returns the UMessageBuilder with the configured plevel.
        """
        self.plevel = plevel
        return self

    def with_traceparent(self, traceparent: str):
        """Add the traceprent.

        @param traceparent the trace parent.
        @return Returns the UMessageBuilder with the configured traceparent.
        """
        self.traceparent = traceparent
        return self

    def with_commstatus(self, commstatus: UCode):
        """Add the communication status of the message.

        @param commstatus the communication status of the message.
        @return Returns the UMessageBuilder with the configured commstatus.
        """
        self.commstatus = commstatus
        return self

    def with_reqid(self, reqid: UUID):
        """Add the request ID.

        @param reqid the request ID.
        @return Returns the UMessageBuilder with the configured reqid.
        """
        self.reqid = reqid
        return self

    def with_sink(self, sink: UUri):
        """Add the explicit destination URI.

        @param sink the explicit destination URI.
        @return Returns the UMessageBuilder with the configured sink.
        """
        self.sink = sink
        return self

    def build(self):
        """Construct the UMessage from the builder.

        @return Returns a constructed
        """
        message_builder = UMessage()

        attributes_builder = UAttributes(source=self.source, id=self.id, type=self.type)

        priority = self._calculate_priority()
        attributes_builder.priority = priority

        if self.sink is not None:
            attributes_builder.sink.CopyFrom(self.sink)
        if self.ttl is not None:
            attributes_builder.ttl = self.ttl
        if self.plevel is not None:
            attributes_builder.permission_level = self.plevel
        if self.commstatus is not None:
            attributes_builder.commstatus = self.commstatus
        if self.reqid is not None:
            attributes_builder.reqid.CopyFrom(self.reqid)
        if self.token is not None:
            attributes_builder.token = self.token
        if self.traceparent is not None:
            attributes_builder.traceparent = self.traceparent
        if self.format is not None:
            attributes_builder.payload_format = self.format

        message_builder.attributes.CopyFrom(attributes_builder)
        if self.payload is not None:
            message_builder.payload = self.payload
        return message_builder

    def build_from_upayload(self, payload: UPayload):
        if payload is not None:
            self.payload = payload.data
            self.format = payload.format
        return self.build()

    def _calculate_priority(self):
        if self.type in [
            UMessageType.UMESSAGE_TYPE_REQUEST,
            UMessageType.UMESSAGE_TYPE_RESPONSE,
        ]:
            return (
                self.priority
                if self.priority is not None and self.priority >= UPriority.UPRIORITY_CS4
                else UPriority.UPRIORITY_CS4
            )
        else:
            return (
                self.priority
                if self.priority is not None and self.priority >= UPriority.UPRIORITY_CS1
                else UPriority.UPRIORITY_CS1
            )
