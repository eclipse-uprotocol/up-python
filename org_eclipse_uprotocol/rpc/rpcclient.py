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
from concurrent.futures import Future

from org_eclipse_uprotocol.transport.datamodel.uattributes import UAttributes
from org_eclipse_uprotocol.transport.datamodel.upayload import UPayload
from org_eclipse_uprotocol.proto.uri_pb2 import UUri


class RpcClient(ABC):
    """
    RpcClient is an interface used by code generators for uProtocol services defined in proto files such as the core
    uProtocol services found in <a href=https://github.com/eclipse-uprotocol/uprotocol-core-api>here</a>.<br> The
    interface provides a
    clean contract for all transports to implement to be able to support RPC on their platform.<br> Each platform MUST
    implement this interface.<br> For more details please refer to<br>
    <a href=https://github.com/eclipse-uprotocol/uprotocol-spec/blob/main/up-l2/README.adoc>[RpcClient
    Specifications]</a>
    """

    @abstractmethod
    def invoke_method(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> Future:
        """
        Support for RPC method invocation.<br><br>

        @param topic: topic of the method to be invoked (i.e. the name of the API we are calling).
        @param payload:The request message to be sent to the server.
        @param attributes:etadata for the method invocation (i.e. priority, timeout, etc.)
        @return: Returns the CompletableFuture with the result or exception.
        """
        pass
