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
    def __init__(self, id: UUID, type: UMessageType, priority: UPriority, ttl: int, token: str, sink: UUri, plevel: int,
                 commstatus: int, reqid: UUID):
        self.id = id
        self.type = type
        self.priority = priority
        self.ttl = ttl
        self.token = token
        self.sink = sink
        self.plevel = plevel
        self.commstatus = commstatus
        self.reqid = reqid

    @staticmethod
    def empty():
        return UAttributes(None, None, None, None, None, None, None, None, None)

    @staticmethod
    def for_rpc_request(id: UUID, sink: UUri) -> UAttributesBuilder:
        return UAttributesBuilder(id, UMessageType.REQUEST, UPriority.REALTIME_INTERACTIVE).with_sink(sink)

    @staticmethod
    def for_rpc_response(id: UUID, sink: UUri, reqid: UUID) -> UAttributesBuilder:
        return UAttributesBuilder(id, UMessageType.RESPONSE, UPriority.REALTIME_INTERACTIVE).with_sink(sink).with_reqid(
            reqid)
