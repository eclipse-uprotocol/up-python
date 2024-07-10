"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.publisher import Publisher
from uprotocol.communication.upayload import UPayload
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.utransport import UTransport
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class SimplePublisher(Publisher):
    def __init__(self, transport: UTransport):
        """
        Constructor for SimplePublisher.

        :param transport: The transport instance to use for sending notifications.
        """
        if transport is None:
            raise ValueError(UTransport.TRANSPORT_NULL_ERROR)
        elif not isinstance(transport, UTransport):
            raise ValueError(UTransport.TRANSPORT_NOT_INSTANCE_ERROR)
        self.transport = transport

    async def publish(
        self, topic: UUri, options: Optional[CallOptions] = None, payload: Optional[UPayload] = None
    ) -> UStatus:
        """
        Publishes a message to a topic using the provided payload.

        :param topic: The topic to publish the message to.
        :param options: Call options for the publish.
        :param payload: The payload to be published.
        :return: An instance of UStatus indicating the status of the publish operation.
        """
        if topic is None:
            raise ValueError("Publish topic missing")

        message = UMessageBuilder.publish(topic).build_from_upayload(payload)
        return await self.transport.send(message)
