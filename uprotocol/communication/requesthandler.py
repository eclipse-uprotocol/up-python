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
from uprotocol.v1.umessage_pb2 import UMessage


class RequestHandler(ABC):
    """
    RequestHandler is used by the RpcServer to handle incoming requests and automatically sends
    back the response to the client.

    The service must implement the `handle_request` method to handle the request and then return
    the response payload.
    """

    @abstractmethod
    def handle_request(self, message: UMessage) -> UPayload:
        """
        Method called to handle/process request messages.

        :param message: The request message received.
        :return: The response payload.
        :raises UStatusError: If the service encounters an error processing the request.
        """
        pass
