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

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UEntity
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.transport.ulistener import UListener
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.ustatus_pb2 import UStatus

class UTransport(ABC):
    """
    UTransport is the  uP-L1 interface that provides a common API for uE developers to send and receive
    messages.<br>UTransport implementations contain the details for connecting to the underlying transport technology
    and sending UMessage using the configured technology.<br>For more information please refer to
    <a href =https://github.com/eclipse-uprotocol/uprotocol-spec/blob/main/up-l1/README.adoc>link</a>
    """

    @abstractmethod
    def send(self, source: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        """
        Send a message (in parts) over the transport.
        @param source The source address for the message, (ex. publish topic, the return address 
        for rpc-request, or the rpc method for rpc response
        @param payload Actual message payload.
        @param attributes uProtocol header attributes.
        @return Returns {@link UStatus} with {@link UCode} set to the status code (successful or failure).
        """
        pass

    @abstractmethod
    def register_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Register {@code UListener} for {@code UUri} topic to be called when a message is received.
        @param topic {@code UUri} to listen for messages from.
        @param listener The {@code UListener} that will be execute when the message is 
        received on the given {@code UUri}.
        @return Returns {@link UStatus} with {@link UCode.OK} if the listener is registered
        correctly, otherwise it returns with the appropriate failure.
        """
        pass

    @abstractmethod
    def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Unregister {@code UListener} for {@code UUri} topic. Messages arriving on this topic will
        no longer be processed by this listener.
        @param topic {@code UUri} to the listener was registered for.
        @param listener The {@code UListener} that will no longer want to be registered to receive
        messages.
        @return Returns {@link UStatus} with {@link UCode.OK} if the listener is unregistered
        correctly, otherwise it returns with the appropriate failure.
        """
        pass
