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
from concurrent.futures import Future

from uprotocol.proto.uattributes_pb2 import CallOptions
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UUri


class RpcClient(ABC):
    """
    RpcClient is an interface used by code generators for uProtocol services
    defined in proto files such as the core
    uProtocol services found in
    <a href=https://github.com/eclipse-uprotocol/uprotocol-core-api>here
    </a>.<br> The interface provides a clean contract for all transports
    to implement to be able to support RPC on their platform.<br>
    Each platform MUST implement this interface.<br>
    """

    @abstractmethod
    def invoke_method(self, method_uri: UUri, request_payload: UPayload, options: CallOptions) -> Future:
        """
        API for clients to invoke a method (send an RPC request) and
        receive the response (the returned Future UMessage. <br>
        Client will set method to be the URI of the method they want to invoke,
        payload to the request message, and attributes
        with the various metadata for the method invocation.
        @param method_uri The method URI to be invoked,
        ex (long form): /example.hello_world/1/rpc.SayHello.
        @param requestPayload The request
        message to be sent to the server.
        @param options RPC method invocation call options, see CallOptions
        @return: Returns the CompletableFuture with the result or exception.
        """
        pass
