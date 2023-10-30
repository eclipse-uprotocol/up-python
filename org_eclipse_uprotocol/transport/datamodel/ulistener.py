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

from org_eclipse_uprotocol.transport.datamodel.uattributes import UAttributes
from org_eclipse_uprotocol.transport.datamodel.upayload import UPayload
from org_eclipse_uprotocol.transport.datamodel.ustatus import UStatus
from org_eclipse_uprotocol.proto.uri_pb2 import UUri


class UListener(ABC):
    """
    For any implementation that defines some kind of callback or function that will be called to handle incoming
    messages.
    """

    @abstractmethod
    def on_receive(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        """
        Method called to handle/process events.<br><br>
        @param topic: Topic the underlying source of the message.
        @param payload: Payload of the message.
        @param attributes: Transportation attributes.
        @return Returns an Ack every time a message is received and processed.
        """
        pass
