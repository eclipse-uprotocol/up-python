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


from org_eclipse_uprotocol.proto.uattributes_pb2 import UAttributes, UPriority, UMessageType
from org_eclipse_uprotocol.proto.uri_pb2 import *
from org_eclipse_uprotocol.proto.uuid_pb2 import UUID
from org_eclipse_uprotocol.uuid.factory.uuidfactory import *


class UAttributesBuilder:
    """
    Construct the UAttributesBuilder with the configurations that are required for every payload transport.

    @param id       Unique identifier for the message.
    @param type     Message type such as Publish a state change, RPC request or RPC response.
    @param priority uProtocol Prioritization classifications.
    """

    def __init__(self, id: UUID, type: UMessageType, priority: UPriority):
        self.id = id
        self.type = type
        self.priority = priority
        self.ttl = None
        self.token = None
        self.sink = None
        self.plevel = None
        self.commstatus = None
        self.reqid = None

    @staticmethod
    def publish(priority: UPriority):
        """
        Construct a UAttributesBuilder for a publish message.
        @param priority The priority of the message.
        @return Returns the UAttributesBuilder with the configured priority.
        """
        if priority is None:
            raise ValueError("Uri cannot be None.")
        return UAttributesBuilder(Factories.UPROTOCOL.create(), UMessageType.UMESSAGE_TYPE_PUBLISH, priority)

    @staticmethod
    def notification(priority: UPriority, sink: UUri):
        """
        Construct a UAttributesBuilder for a notification message.
        @param priority The priority of the message.
        @param sink The destination URI.
        @return Returns the UAttributesBuilder with the configured priority and sink.
        """
        if priority is None:
            raise ValueError("UPriority cannot be null.")
        if sink is None:
            raise ValueError("sink cannot be null.")
        return UAttributesBuilder(Factories.UPROTOCOL.create(), UMessageType.UMESSAGE_TYPE_PUBLISH, priority).withSink(
            sink)

    @staticmethod
    def request(priority: UPriority, sink: UUri, ttl: int):
        """
        Construct a UAttributesBuilder for a request message.
        @param priority The priority of the message.
        @param sink The destination URI.
        @param ttl The time to live in milliseconds.
        @return Returns the UAttributesBuilder with the configured priority, sink and ttl.
        """
        if priority is None:
            raise ValueError("UPriority cannot be null.")
        if sink is None:
            raise ValueError("sink cannot be null.")
        if ttl is None:
            raise ValueError("ttl cannot be null.")

        return UAttributesBuilder(Factories.UPROTOCOL.create(), UMessageType.UMESSAGE_TYPE_REQUEST, priority).withTtl(
            ttl).withSink(sink)

    @staticmethod
    def response(priority: UPriority, sink: UUri, reqid: UUID):
        """
        Construct a UAttributesBuilder for a response message.
        @param priority The priority of the message.
        @param sink The destination URI.
        @param reqid The original request UUID used to correlate the response to the request.
        @return Returns the UAttributesBuilder with the configured priority, sink and reqid.
        """
        if priority is None:
            raise ValueError("UPriority cannot be null.")
        if sink is None:
            raise ValueError("sink cannot be null.")
        if reqid is None:
            raise ValueError("reqid cannot be null.")

        return UAttributesBuilder(Factories.UPROTOCOL.create(), UMessageType.UMESSAGE_TYPE_RESPONSE, priority).withSink(
            sink).withReqId(reqid)

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

    def withCommStatus(self, commstatus: int):
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

    def build(self):
        """
        Construct the UAttributes from the builder.

        @return Returns a constructed
        """
        attributes = UAttributes(id=self.id, type=self.type, priority=self.priority)
        if self.sink is not None:
            if self.sink.HasField('authority'):
                if self.sink.authority.HasField('id'):
                    attributes.sink.authority.id = self.sink.authority.id
                if self.sink.authority.HasField('name'):
                    attributes.sink.authority.name = self.sink.authority.name
                if self.sink.authority.HasField('ip'):
                    attributes.sink.authority.ip = self.sink.authority.ip
            if self.sink.HasField('entity'):
                attributes.sink.entity.name = self.sink.entity.name
                if self.sink.entity.HasField('id'):
                    attributes.sink.entity.id = self.sink.entity.id
                if self.sink.entity.HasField('version_major'):
                    attributes.sink.entity.version_major = self.sink.entity.version_major
                if self.sink.entity.HasField('version_minor'):
                    attributes.sink.entity.version_minor = self.sink.entity.version_minor
            if self.sink.HasField('resource'):
                attributes.sink.resource.name = self.sink.resource.name
                if self.sink.resource.HasField('id'):
                    attributes.sink.resource.id = self.sink.resource.id
                if self.sink.resource.HasField('instance'):
                    attributes.sink.resource.instance = self.sink.resource.instance
                if self.sink.resource.HasField('message'):
                    attributes.sink.resource.message = self.sink.resource.message
        if self.ttl is not None:
            attributes.ttl = self.ttl
        if self.plevel is not None:
            attributes.permission_level = self.plevel
        if self.commstatus is not None:
            attributes.commstatus = self.commstatus
        if self.reqid is not None:
            attributes.reqid = self.reqid
        if self.token != None:
            attributes.token = self.token
        return attributes
