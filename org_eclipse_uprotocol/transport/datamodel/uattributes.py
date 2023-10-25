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

from org_eclipse_uprotocol.transport.datamodel.umessagetype import UMessageType
from org_eclipse_uprotocol.transport.datamodel.upriority import UPriority
from org_eclipse_uprotocol.uri.datamodel.uuri import UUri
from org_eclipse_uprotocol.uuid.factory import UUID


class UAttributesBuilder:

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

    def with_ttl(self, ttl: int):
        self.ttl = ttl
        return self

    def with_token(self, token: str):
        self.token = token
        return self

    def with_sink(self, sink: UUri):
        self.sink = sink
        return self

    def with_permission_level(self, plevel: int):
        self.plevel = plevel
        return self

    def with_comm_status(self, commstatus: int):
        self.commstatus = commstatus
        return self

    def with_reqid(self, reqid: UUID):
        self.reqid = reqid
        return self

    def build(self):
        return UAttributes(self.id, self.type, self.priority, self.ttl, self.token, self.sink, self.plevel,
                           self.commstatus, self.reqid)


class UAttributes:
    """
     When sending data over uTransport the basic API for send uses a source topic and the UPayload as the
     data.<br>Any other information about the message is placed in the UAttributes class.<br>The UAttributes class
     holds the additional information along with business methods for understanding more about the actual message
     sent. UAttributes is the class that defines the Payload. It is the place for configuring time to live,
     priority, security tokens and more.<br>Each UAttributes class defines a different type of message payload. The
     payload can represent a simple published payload with some state change, Payload representing an RPC request or
     Payload representing an RPC response.
    """

    def __init__(self, id: UUID, type: UMessageType, priority: UPriority, ttl: int, token: str, sink: UUri, plevel: int,
                 commstatus: int, reqid: UUID):
        """
        Construct the transport UAttributes object.<br><br>
        @param id:Unique identifier for the message. Required.
        @param type:Message type such as Publish a state change, RPC request or RPC response. Required.
        @param priority:Message priority. Required.
        @param ttl:Time to live in milliseconds.
        @param token:Authorization token used for TAP.
        @param sink:Explicit destination URI, used in notifications and RPC messages.
        @param plevel:Permission Level.
        @param commstatus:Communication Status, used to indicate platform communication errors that occurred during
        delivery.
        @param reqid: Request ID, used to indicate the id of the RPC request that matches this RPC response.
        """

        # Required Attributes
        self.id = id
        self.type = type
        self.priority = priority
        # Optional Attributes
        self.ttl = ttl
        self.token = token
        self.sink = sink
        self.plevel = plevel
        self.commstatus = commstatus
        self.reqid = reqid

    @staticmethod
    def empty():
        """
        Static factory method for creating an empty attributes object, to avoid working with null.<br><br>
        @return: Returns an empty attributes that indicates that there are no added additional attributes to
        configure.<br>  An empty UAttributes is not valid, in the same way null is not valid, this is because
        UAttributes has 3 required values - id, type and priority.
        """
        return UAttributes(None, None, None, None, None, None, None, None, None)

    @staticmethod
    def for_rpc_request(id: UUID, sink: UUri) -> UAttributesBuilder:
        """
        Static factory method for creating a base UAttributes for an RPC request.<br><br>
        @param id:id Unique identifier for the RPC request message.
        @param sink:UUri describing the exact RPC command.
        @return:Returns a base UAttributes that can be used to build an RPC request.
        """
        return UAttributesBuilder(id, UMessageType.REQUEST, UPriority.REALTIME_INTERACTIVE).with_sink(sink)

    @staticmethod
    def for_rpc_response(id: UUID, sink: UUri, reqid: UUID) -> UAttributesBuilder:
        """
        Static factory method for creating a base UAttributes for an RPC response.<br><br>
        @param id:Unique identifier for the RPC response message.
        @param sink:UUri describing where the response needs to go.
        @param reqid:The UUID of the message that this response is responding to.
        @return: Returns a base UAttributes that can be used to build an RPC response.
        """
        return UAttributesBuilder(id, UMessageType.RESPONSE, UPriority.REALTIME_INTERACTIVE).with_sink(sink).with_reqid(
            reqid)
