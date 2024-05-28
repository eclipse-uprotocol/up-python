"""
SPDX-FileCopyrightText: Copyright (c) 2023 Contributors to the
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

from abc import ABC, abstractmethod
from multimethod import multimethod

from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri
from uprotocol.transport.ulistener import UListener
from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UStatus
from uprotocol.proto.uprotocol.v1.umessage_pb2 import UMessage


class UTransport(ABC):
    """
    UTransport is the  uP-L1 interface that provides a common API for uE
    developers to send and receive messages.
    UTransport implementations contain the details for connecting to the
    underlying transport technology and sending UMessage using the configured
    technology.
    For more information please refer to the uP-L1 specification in up-spec.
    """

    @abstractmethod
    def send(self, message: UMessage) -> UStatus:
        """
        Send a message (in parts) over the transport.
        @param message the UMessage to be sent.
        @return Returns UStatus with UCode set to the status code
        (successful or failure).
        """
        pass

    @multimethod
    def register_listener(
        self, source_filter: UUri, listener: UListener
    ) -> UStatus:
        """
        Register UListener for UUri source filters to be called when a
        message is received.

        @param source_filter The UAttributes::source address pattern that the
        message to receive needs to match.
        @param listener The UListener that will be execute when the message is
        received on the given UUri.
        @return Returns UStatus with UCode.OK if the listener is registered
        correctly, otherwise it returns with the appropriate failure.
        """
        return UTransport.register_listener(source_filter, UUri(), listener)

    @multimethod
    @abstractmethod
    def register_listener(
        self, source_filter: UUri, sink_filter: UUri, listener: UListener
    ) -> UStatus:
        """
        Register UListener for UUri source and sink filters to be called when
        a message is received.

        @param source_filter The UAttributes::source address pattern that the
        message to receive needs to match.
        @param sink_filter The UAttributes::sink address pattern that the
        message to receive needs to match.
        @param listener The UListener that will be execute when the message is
        received on the given UUri.
        @return Returns UStatus with UCode.OK if the listener is registered
        correctly, otherwise it returns with the appropriate failure.
        """
        pass

    @multimethod
    def unregister_listener(
        self, source_filter: UUri, listener: UListener
    ) -> UStatus:
        """
        Unregister UListener for UUri source filters to be called when a
        message is received.

        @param source_filter The UAttributes::source address pattern that the
        message to receive needs to match.
        @param listener The UListener that will be execute when the message is
        received on the given UUri.
        @return Returns UStatus with UCode.OK if the listener is registered
        correctly, otherwise it returns with the appropriate failure.
        """
        return UTransport.register_listener(source_filter, UUri(), listener)

    @multimethod
    @abstractmethod
    def unregister_listener(
        self, source_filter: UUri, sink_filter: UUri, listener: UListener
    ) -> UStatus:
        """
        Unregister UListener for UUri source and sink filters. Messages
        arriving on this topic will no longer be processed by this listener.

        @param source_filter The UAttributes::source address pattern that the
        message to receive needs to match.
        @param sink_filter The UAttributes::sink address pattern that the
        message to receive needs to match.
        @param listener The UListener that will no longer want to be
        registered to receive messages.
        @return Returns UStatus with UCode.OK if the listener is unregistered
        correctly, otherwise it returns with the appropriate failure.
        """
        pass
