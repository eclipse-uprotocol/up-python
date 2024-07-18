"""
SPDX-FileCopyrightText: 2023 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from abc import ABC, abstractmethod

from uprotocol.transport.ulistener import UListener
from uprotocol.uri.factory.uri_factory import UriFactory
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class UTransport(ABC):
    """UTransport is the  uP-L1 interface that provides a common API for uE developers to send and receive
    messages.<br>UTransport implementations contain the details for connecting to the underlying transport technology
    and sending UMessage using the configured technology.<br>For more information please refer to
    https://github.com/eclipse-uprotocol/uprotocol-spec/blob/main/up-l1/README.adoc
    """

    TRANSPORT_NULL_ERROR = "Transport cannot be null"
    TRANSPORT_NOT_INSTANCE_ERROR = "Transport must be an instance of UTransport"

    @abstractmethod
    async def send(self, message: UMessage) -> UStatus:
        """Send a message (in parts) over the transport.
        @param message the UMessage to be sent.
        @return Returns UStatus with UCode set to the status code (successful or failure).
        """
        pass

    @abstractmethod
    async def register_listener(
        self, source_filter: UUri, listener: UListener, sink_filter: UUri = UriFactory.ANY
    ) -> UStatus:
        """Register UListener for UUri source and sink filters to be called when
        a message is received.

        @param source_filter The UAttributes source address pattern that the
        message to receive needs to match.
        @param sink_filter The UAttributes sink address pattern that the
        message to receive needs to match or None to match messages that do not contain any sink address.
        @param listener The UListener that will execute when the message is

        received on the given UUri.
        @return Returns UStatus with UCode.OK if the listener is registered
        correctly, otherwise it returns with the appropriate failure.
        """
        pass

    @abstractmethod
    async def unregister_listener(
        self, source_filter: UUri, listener: UListener, sink_filter: UUri = UriFactory.ANY
    ) -> UStatus:
        """Unregister UListener for UUri source and sink filters. Messages
        arriving at this topic will no longer be processed by this listener.

        @param source_filter The UAttributes source address pattern that the
        message to receive needs to match.
        @param sink_filter The UAttributes sink address pattern that the
        message to receive needs to match or None to match messages that do not contain any sink address.
        @param listener The UListener that will no longer want to be registered to receive
        messages.
        @return Returns UStatus with UCode.OK if the listener is unregistered
        correctly, otherwise it returns with the appropriate failure.
        """
        pass

    @abstractmethod
    def get_source(self) -> UUri:
        """Get the source URI of the transport.This URI represents the uE that is using the transport.

        @return Returns the source URI of the transport.
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        Close the connection to the transport that will trigger any registered listeners
        to be unregistered.
        """
        pass
