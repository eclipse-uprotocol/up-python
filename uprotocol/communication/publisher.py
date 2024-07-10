"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from abc import ABC, abstractmethod

from uprotocol.communication.upayload import UPayload
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class Publisher(ABC):
    """
    uP-L2 interface and data models for Python.

    uP-L1 interfaces implement the core uProtocol across various communication middlewares
    and programming languages while uP-L2 API are the client-facing APIs that wrap the transport
    functionality into easy-to-use, language-specific APIs to do the most common functionality
    of the protocol (subscribe, publish, notify, invoke a method, or handle RPC requests).
    """

    @abstractmethod
    async def publish(self, topic: UUri, payload: UPayload) -> UStatus:
        """
        Publish a message to a topic passing UPayload as the payload.

        :param topic: The topic to publish to.
        :param payload: The UPayload to publish.
        :return: An instance of UStatus indicating the status of the publish operation.
        """
        pass
