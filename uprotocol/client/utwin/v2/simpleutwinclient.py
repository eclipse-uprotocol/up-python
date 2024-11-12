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
from uprotocol.communication.rpcclient import RpcClient
from uprotocol.communication.rpcmapper import RpcMapper
from uprotocol.communication.upayload import UPayload
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.core.utwin.v2 import utwin_pb2
from uprotocol.core.utwin.v2.utwin_pb2 import GetLastMessagesRequest, GetLastMessagesResponse
from uprotocol.uri.factory.uri_factory import UriFactory
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.uri_pb2 import UUriBatch


class SimpleUTwinClient:
    """
    The uTwin client implementation using the RpcClient uP-L2 communication layer interface.
    """

    descriptor = utwin_pb2.DESCRIPTOR.services_by_name['uTwin']
    # TODO: The following items eventually need to be pulled from generated code
    getlastmessage_method = UriFactory.from_proto(descriptor, 1)

    def __init__(self, rpc_client: RpcClient):
        """
        Create a new instance of the uTwin client passing in the RPCClient to use for communication.

        :param rpc_client: The RPC client to use for communication.
        """
        self.rpc_client = rpc_client

    async def get_last_messages(
        self, topics: UUriBatch, options: Optional[CallOptions] = CallOptions.DEFAULT
    ) -> GetLastMessagesResponse:
        """
        Fetch the last messages for a batch of topics.

        :param topics: UUriBatch - Batch of 1 or more topics to fetch the last messages for.
        :param options: CallOptions - The call options.
        :return: An asyncio.Future that completes successfully with GetLastMessagesResponse if uTwin was able
                 to fetch the topics or raises UStatusException with the failure reason such as UCode.NOT_FOUND,
                 UCode.PERMISSION_DENIED, etc.
        """
        if topics is None:
            raise ValueError("topics must not be null")
        if options is None:
            options = CallOptions.DEFAULT

        # Check if topics is empty
        if topics == UUriBatch():
            raise UStatusError.from_code_message(UCode.INVALID_ARGUMENT, "topics must not be empty")

        request = GetLastMessagesRequest(topics=topics)
        result = await RpcMapper.map_response(
            self.rpc_client.invoke_method(self.getlastmessage_method, UPayload.pack(request), options),
            GetLastMessagesResponse,
        )
        return result
