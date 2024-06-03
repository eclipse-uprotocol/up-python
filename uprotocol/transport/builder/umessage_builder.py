"""
SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to the
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

from multimethod import multimethod

from google.protobuf.message import Message
from google.protobuf.any_pb2 import Any

from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri
from uprotocol.proto.uprotocol.v1.uuid_pb2 import UUID
from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UCode
from uprotocol.proto.uprotocol.v1.uattributes_pb2 import (
    UMessageType,
    UPriority,
    UPayloadFormat,
    UAttributes,
)
from uprotocol.proto.uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.uuid.factory.uuidfactory import Factories

SOURCE_ERROR = "source cannot be null."
SINK_ERROR = "sink cannot be null."
REQID_ERROR = "reqid cannot be null."
REQUEST_ERROR = "request cannot be null."
TTL_ERROR = "ttl cannot be null."


class UMessageBuilder:
    """
    Builder for easy construction of the UAttributes object.
    """

    # private final UUri source;
    # private final UUID id;
    # private final UMessageType type;
    # private UPriority priority;
    # private Integer ttl;
    # private String token;
    # private UUri sink;
    # private Integer plevel;
    # private UCode commstatus;
    # private UUID reqid;
    # private String traceparent;

    # private UPayloadFormat format;
    # private ByteString payload;

    @staticmethod
    def publish(source: UUri) -> "UMessageBuilder":
        """
        Construct a UMessageBuilder for a publish message.

        @param source   Source address of the message.
        @return Returns the UMessageBuilder with the configured priority.
        """
        if source is None:
            raise ValueError(SOURCE_ERROR)
        return UMessageBuilder(
            source,
            Factories.UPROTOCOL.create(),
            UMessageType.UMESSAGE_TYPE_PUBLISH,
        )

    @staticmethod
    def notification(source: UUri, sink: UUri) -> "UMessageBuilder":
        """
        Construct a UMessageBuilder for a notification message.

        @param source   Source address of the message.
        @param sink The destination URI.
        @return Returns the UMessageBuilder with the configured priority
        and sink.
        """
        if source is None:
            raise ValueError(SOURCE_ERROR)
        if sink is None:
            raise ValueError(SINK_ERROR)
        return UMessageBuilder(
            source,
            Factories.UPROTOCOL.create(),
            UMessageType.UMESSAGE_TYPE_NOTIFICATION,
        ).with_sink(sink)

    @staticmethod
    def request(source: UUri, sink: UUri, ttl: int) -> "UMessageBuilder":
        """
        Construct a UMessageBuilder for a request message.

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
        return (
            UMessageBuilder(
                source,
                Factories.UPROTOCOL.create(),
                UMessageType.UMESSAGE_TYPE_REQUEST,
            )
            .with_ttl(ttl)
            .with_sink(sink)
        )

    @multimethod
    def response(source: UUri, sink: UUri, reqid: UUID) -> "UMessageBuilder":
        """
        Construct a UMessageBuilder for a response message.

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

        return (
            UMessageBuilder(
                source,
                Factories.UPROTOCOL.create(),
                UMessageType.UMESSAGE_TYPE_RESPONSE,
            )
            .with_sink(sink)
            .with_reqid(reqid)
        )

    @multimethod
    def response(request: UAttributes) -> "UMessageBuilder":
        """
        Construct a UMessageBuilder for a response message using an
        existing request.
        @param request The original request UAttributes used to correlate
        the response to the request.
        @return Returns the UMessageBuilder with the configured source, sink,
        priority, and reqid.
        """
        if request is None:
            raise ValueError(REQUEST_ERROR)
        return (
            UMessageBuilder(
                request.sink,
                Factories.UPROTOCOL.create(),
                UMessageType.UMESSAGE_TYPE_RESPONSE,
            )
            .with_priority(UPriority.UPRIORITY_CS4)
            .with_sink(request.sink)
            .with_reqid(request.id)
        )

    def __init__(self, source: UUri, id_val: UUID, type_val: UMessageType):
        """
        Construct the UMessageBuilder with the configurations that are
        required for every payload transport.

        @param source   Source address of the message.
        @param id       Unique identifier for the message.
        @param type     Message type such as Publish a state change,
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

    def with_ttl(self, ttl: int) -> "UMessageBuilder":
        """
        Add the time to live in milliseconds.

        @param ttl the time to live in milliseconds.
        @return Returns the UMessageBuilder with the configured ttl.
        """
        self.ttl = ttl
        return self

    def with_token(self, token: str) -> "UMessageBuilder":
        """
        Add the authorization token used for TAP.

        @param token the authorization token used for TAP.
        @return Returns the UMessageBuilder with the configured token.
        """
        self.token = token
        return self

    def with_priority(self, priority: UPriority) -> "UMessageBuilder":
        """
        Add the priority level of the message.

        @param priority the priority level of the message.
        @return Returns the UMessageBuilder with the configured priority.
        """
        self.priority = priority
        return self

    def with_permission_level(self, plevel: int) -> "UMessageBuilder":
        """
        Add the permission level of the message.

        @param plevel the permission level of the message.
        @return Returns the UMessageBuilder with the configured plevel.
        """
        self.plevel = plevel
        return self

    def with_traceparent(self, traceparent: str) -> "UMessageBuilder":
        """
        Add the traceprent.

        @param traceparent the trace parent.
        @return Returns the UMessageBuilder with the configured traceparent.
        """
        self.traceparent = traceparent
        return self

    def with_commstatus(self, commstatus: UCode) -> "UMessageBuilder":
        """
        Add the communication status of the message.

        @param commstatus the communication status of the message.
        @return Returns the UMessageBuilder with the configured commstatus.
        """
        self.commstatus = commstatus
        return self

    def with_reqid(self, reqid: UUID) -> "UMessageBuilder":
        """
        Add the request ID.

        @param reqid the request ID.
        @return Returns the UMessageBuilder with the configured reqid.
        """
        self.reqid = reqid
        return self

    def with_sink(self, sink: UUri) -> "UMessageBuilder":
        """
        Add the explicit destination URI.

        @param sink the explicit destination URI.
        @return Returns the UMessageBuilder with the configured sink.
        """
        self.sink = sink
        return self

    def _build_static(self):
        """
        Construct the UMessage from the builder.

        @return Returns a constructed
        """
        message_builder = UMessage()

        attributes_builder = UAttributes(
            source=self.source, id=self.id, type=self.type
        )

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

    def build(self, arg1=None, arg2=None):
        if arg1 is None and arg2 is None:
            return self._build_static()
        elif isinstance(arg1, Any) and arg2 is None:
            if arg1 is None:
                raise ValueError("Any cannot be null.")
            self.format = (
                UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY
            )
            self.payload = arg1.SerializeToString()
            return self._build_static()
        elif isinstance(arg1, Message) and arg2 is None:
            if arg1 is None:
                raise ValueError("Protobuf Message cannot be null.")
            self.format = UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF
            self.payload = arg1.SerializeToString()
            return self._build_static()
        elif isinstance(arg2, bytes):
            if arg1 is None:
                raise ValueError("Format cannot be null.")
            if arg2 is None:
                raise ValueError("Payload cannot be null.")
            self.format = arg1
            self.payload = arg2
            return self._build_static()

    def _calculate_priority(self):
        if self.type in [
            UMessageType.UMESSAGE_TYPE_REQUEST,
            UMessageType.UMESSAGE_TYPE_RESPONSE,
        ]:
            return (
                self.priority
                if self.priority is not None
                and self.priority >= UPriority.UPRIORITY_CS4
                else UPriority.UPRIORITY_CS4
            )
        else:
            return (
                self.priority
                if self.priority is not None
                and self.priority >= UPriority.UPRIORITY_CS1
                else UPriority.UPRIORITY_CS1
            )
