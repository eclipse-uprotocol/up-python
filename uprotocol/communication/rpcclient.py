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

from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.upayload import UPayload
from uprotocol.v1.uri_pb2 import UUri


class RpcClient(ABC):
    """
    Communication Layer (uP-L2) RPC Client Interface.

    Clients use this API to invoke a method (send a request and wait for a reply).
    """

    @abstractmethod
    async def invoke_method(self, method_uri: UUri, request_payload: UPayload, options: CallOptions) -> UPayload:
        """
        API for clients to invoke a method (send an RPC request) and receive the response.

        :param method_uri: The method URI to be invoked.
        :param request_payload: The request payload to be sent to the server.
        :param options: RPC method invocation call options.
        :return: Returns the response payload.
        :raises UStatus: If the RPC invocation fails for any reason.
        """
        pass
