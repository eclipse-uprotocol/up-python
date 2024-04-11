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

from multimethod import multimethod
from typing import Union

from uprotocol.proto.uattributes_pb2 import (
    UAttributes,
    UPriority,
    UMessageType,
)
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UCode
from uprotocol.proto.uuid_pb2 import UUID
from uprotocol.uuid.factory.uuidfactory import Factories


class UAttributesBuilder:
    """
    Construct the UAttributesBuilder with the configurations that are
    required for every payload transport.

    @param id       Unique identifier for the message.
    @param type     Message type such as Publish a state change,
    RPC request or RPC response.
    @param priority uProtocol Prioritization classifications.
    """

    def __init__(
        self, source: UUri, id: UUID, type: UMessageType, priority: UPriority
    ):
        self.source = source
        self.id = id
        self.type = UMessageType.Name(type)
        self.priority = priority
        self.ttl = None
        self.token = None
        self.sink = None
        self.plevel = None
        self.commstatus = None
        self.reqid = None
        self.traceparent = None

    @staticmethod
    def publish(source: UUri, priority: UPriority):
        """
        Construct a UAttributesBuilder for a publish message.
        @param source   Source address of the message.
        @param priority The priority of the message.
        @return Returns the UAttributesBuilder with the configured priority.
        """
        if source is None:
            raise ValueError("Source cannot be None.")
        if priority is None:
            raise ValueError("UPriority cannot be None.")
        return UAttributesBuilder(
            source,
            Factories.UPROTOCOL.create(),
            UMessageType.UMESSAGE_TYPE_PUBLISH,
            priority,
        )

    @staticmethod
    def notification(source: UUri, sink: UUri, priority: UPriority):
        """
        Construct a UAttributesBuilder for a notification message.
        @param source   Source address of the message.
        @param sink     The destination URI.
        @param priority The priority of the message.
        @return Returns the UAttributesBuilder with the configured source,
        priority and sink.
        """
        if source is None:
            raise ValueError("Source cannot be None.")
        if priority is None:
            raise ValueError("UPriority cannot be null.")
        if sink is None:
            raise ValueError("sink cannot be null.")
        return UAttributesBuilder(
            source,
            Factories.UPROTOCOL.create(),
            UMessageType.UMESSAGE_TYPE_NOTIFICATION,
            priority,
        ).withSink(sink)

    @staticmethod
    def request(source: UUri, sink: UUri, priority: UPriority, ttl: int):
        """
        Construct a UAttributesBuilder for a request message.
        @param source   Source address of the message.
        @param sink     The destination URI.
        @param priority The priority of the message.
        @param ttl      The time to live in milliseconds.
        @return Returns the UAttributesBuilder with the configured
        priority, sink and ttl.
        """
        if source is None:
            raise ValueError("Source cannot be None.")
        if priority is None:
            raise ValueError("UPriority cannot be null.")
        if sink is None:
            raise ValueError("sink cannot be null.")
        if ttl is None:
            raise ValueError("ttl cannot be null.")

        return (
            UAttributesBuilder(
                source,
                Factories.UPROTOCOL.create(),
                UMessageType.UMESSAGE_TYPE_REQUEST,
                priority,
            )
            .withTtl(ttl)
            .withSink(sink)
        )

    @multimethod
    def response(
        source: Union[UUri, None],
        sink: Union[UUri, None],
        priority: Union[int, None],
        reqid: Union[UUID, None],
    ):
        """
        Construct a UAttributesBuilder for a response message.
        @param source   Source address of the message.
        @param sink     The destination URI.
        @param priority The priority of the message.
        @param reqid    The original request UUID used to correlate the
        response to the request.
        @return Returns the UAttributesBuilder with the configured priority,
        sink and reqid.
        """
        if priority is None:
            raise ValueError("UPriority cannot be null.")
        if sink is None:
            raise ValueError("sink cannot be null.")
        if reqid is None:
            raise ValueError("reqid cannot be null.")

        return (
            UAttributesBuilder(
                source,
                Factories.UPROTOCOL.create(),
                UMessageType.UMESSAGE_TYPE_RESPONSE,
                priority,
            )
            .withSink(sink)
            .withReqId(reqid)
        )

    @multimethod
    def response(request: Union[UAttributes, None]):
        if request is None:
            raise ValueError("request cannot be null.")
        return UAttributesBuilder.response(
            request.sink, request.source, request.priority, request.id
        )

    def withTtl(self, ttl: int):
        """
        Add the time to live in milliseconds.

        @param ttl the time to live in milliseconds.
        @return Returns the UAttributesBuilder with the configured ttl.
        """
        self.ttl = ttl
        return self

    def withToken(self, token: str):
        """
        dd the authorization token used for TAP.

        @param token the authorization token used for TAP.
        @return Returns the UAttributesBuilder with the configured token.
        """
        self.token = token
        return self

    def withSink(self, sink: UUri):
        """
        Add the explicit destination URI.

        @param sink the explicit destination URI.
        @return Returns the UAttributesBuilder with the configured sink.
        """
        self.sink = sink
        return self

    def withPermissionLevel(self, plevel: int):
        """
        Add the permission level of the message.

        @param plevel the permission level of the message.
        @return Returns the UAttributesBuilder with the configured plevel.
        """
        self.plevel = plevel
        return self

    def withCommStatus(self, commstatus: UCode):
        """
        Add the communication status of the message.

        @param commstatus the communication status of the message.
        @return Returns the UAttributesBuilder with the configured commstatus.
        """
        self.commstatus = commstatus
        return self

    def withReqId(self, reqid: UUID):
        """
        Add the request ID.

        @param reqid the request ID.
        @return Returns the UAttributesBuilder with the configured reqid.
        """
        self.reqid = reqid
        return self

    def withTraceparent(self, traceparent: str):
        """
        Add the traceparent.

        @param reqid    the traceparent.
        @return Returns the UAttributesBuilder with the configured
        traceparent.
        """
        self.traceparent = traceparent
        return self

    def build(self):
        """
        Construct the UAttributes from the builder.

        @return Returns a constructed
        """
        attributes = UAttributes(
            source=self.source,
            id=self.id,
            type=self.type,
            priority=self.priority,
        )
        if self.sink is not None:
            attributes.sink.CopyFrom(self.sink)
        if self.ttl is not None:
            attributes.ttl = self.ttl
        if self.plevel is not None:
            attributes.permission_level = self.plevel
        if self.commstatus is not None:
            attributes.commstatus = self.commstatus
        if self.reqid is not None:
            attributes.reqid.CopyFrom(self.reqid)
        if self.traceparent is not None:
            attributes.traceparent = self.traceparent
        if self.token is not None:
            attributes.token = self.token
        return attributes
