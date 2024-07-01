"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import asyncio
import time
import unittest
from unittest.mock import MagicMock

from tests.test_communication.mock_utransport import MockUTransport
from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.requesthandler import RequestHandler
from uprotocol.communication.uclient import UClient
from uprotocol.communication.upayload import UPayload
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri

transport = MockUTransport()

upclient = UClient(transport)


class MyRequestHandler(RequestHandler):
    def handle_request(self, message: UMessage) -> UPayload:
        print('receive request')
        return UPayload.pack_from_data_and_format(message.payload, message.attributes.payload_format)


class TextRpcServer(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.method_uri = UUri(authority_name="Neelam", ue_id=1, ue_version_major=1, resource_id=1)
        cls.handler = MyRequestHandler()

    async def test_happy_path(self):
        self.handler.handle_request = MagicMock(side_effect=self.handler.handle_request)
        uri = UUri(authority_name="Neelam", ue_id=2, ue_version_major=1, resource_id=1)
        self.assertEqual(upclient.register_request_handler(uri, self.handler).code, UCode.OK)
        future_result = asyncio.ensure_future(upclient.invoke_method(uri, UPayload.pack(None), CallOptions()))
        response = await future_result
        print('response', response)
        time.sleep(0.5)
        self.handler.handle_request.assert_called_once()

        self.assertEqual(upclient.unregister_request_handler(uri, self.handler).code, UCode.OK)

    def test_register_request_handler(self):
        self.assertEqual(upclient.register_request_handler(self.method_uri, self.handler).code, UCode.OK)

    def test_unregister_request_handler(self):
        random_uri = UUri(authority_name="Kushwah", ue_id=2, ue_version_major=1, resource_id=1)

        self.assertEqual(upclient.unregister_request_handler(random_uri, self.handler).code, UCode.NOT_FOUND)

    def test_register_and_unregister_request_handler(self):
        self.assertEqual(upclient.register_request_handler(self.method_uri, self.handler).code, UCode.OK)
        self.assertEqual(upclient.unregister_request_handler(self.method_uri, self.handler).code, UCode.OK)


if __name__ == '__main__':
    unittest.main()
