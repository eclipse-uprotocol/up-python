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

from multimethod import multimethod
from google.protobuf.message import Message

from uprotocol.client.transport_wrapper import TransportWrapper
from uprotocol.transport.builder.umessage_builder import UMessageBuilder
from uprotocol.client.upayload import UPayload

from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UStatus
from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri


class Publisher(TransportWrapper):
    """
    uP-L2 interface and data models for Python.

    uP-L1 interfaces implements the core uProtocol across various the
    communication middlewares and programming languages while uP-L2 API
    are the client-facing APIs that wrap the transport functionality into
    easy to use, language specific, APIs to do the most common functionality
    of the protocol (subscribe, publish, notify,
    invoke a Method, or handle RPC requests).
    """

    @multimethod
    def publish(self, topic: UUri) -> UStatus:
        """
        Publish a message to a topic with no payload.

        @param topic The topic to publish to.
        @return Returns the status of the publish operation.
        """
        return self.get_transport().send(
            UMessageBuilder.publish(topic).build()
        )

    @multimethod
    def publish(self, topic: UUri, message: Message) -> UStatus:
        """
        Publish a message to a topic with a payload that is of type Message

        @param topic The topic to publish to.
        @param message The message to publish.
        @return Returns the status of the publish operation.
        """
        return self.get_transport().send(
            UMessageBuilder.publish(topic).build(message)
        )

    @multimethod
    def publish(self, topic: UUri, payload: UPayload) -> UStatus:
        """
        Publish a message to a topic passing UPayload as the payload.

        @param topic The topic to publish to.
        @param payload The {@link UPayload} to publish.
        @return
        """
        return self.get_transport().send(
            UMessageBuilder.publish(topic).build(payload.format, payload.data)
        )
