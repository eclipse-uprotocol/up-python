"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import unittest
from unittest.mock import AsyncMock

from uprotocol.client.utwin.v2.simpleutwinclient import SimpleUTwinClient
from uprotocol.communication.rpcclient import RpcClient
from uprotocol.communication.upayload import UPayload
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.core.utwin.v2.utwin_pb2 import GetLastMessagesResponse
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.uri_pb2 import UUri, UUriBatch


class SimpleUTwinClientTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Mocking RpcClient
        self.rpc_client = AsyncMock(spec=RpcClient)

        # Creating a sample UUri for tests
        self.topic = UUri(authority_name="test", ue_id=3, ue_version_major=1, resource_id=0x8000)

    async def test_get_last_messages(self):
        """
        Test calling get_last_messages() with valid topics.
        """
        # Creating a UUriBatch with one topic
        topics = UUriBatch(uris=[self.topic])

        # Mocking RpcClient's invoke_method to return a successful response
        self.rpc_client.invoke_method.return_value = UPayload.pack(GetLastMessagesResponse())

        client = SimpleUTwinClient(self.rpc_client)
        response = await client.get_last_messages(topics)

        self.assertIsNotNone(response)
        self.assertIsInstance(response, GetLastMessagesResponse)

    async def test_get_last_messages_empty_topics(self):
        """
        Test calling get_last_messages() with empty topics.
        """
        # Creating an empty UUriBatch
        topics = UUriBatch()

        client = SimpleUTwinClient(self.rpc_client)

        with self.assertRaises(UStatusError) as context:
            await client.get_last_messages(topics)

        # Asserting the exception type and message
        self.assertEqual(context.exception.status.code, UCode.INVALID_ARGUMENT)
        self.assertEqual(context.exception.status.message, "topics must not be empty")

    async def test_get_last_messages_exception(self):
        """
        Test calling get_last_messages() when the RpcClient completes exceptionally.
        """
        # Creating a UUriBatch with one topic
        topics = UUriBatch(uris=[self.topic])

        # Mocking RpcClient's invoke_method to raise an exception
        exception = UStatusError.from_code_message(UCode.NOT_FOUND, "Not found")
        self.rpc_client.invoke_method.return_value = exception

        client = SimpleUTwinClient(self.rpc_client)

        with self.assertRaises(UStatusError) as context:
            await client.get_last_messages(topics)

        # Asserting the exception type and message
        self.assertEqual(context.exception.status.code, UCode.NOT_FOUND)
        self.assertEqual(context.exception.status.message, "Not found")


if __name__ == "__main__":
    unittest.main()
