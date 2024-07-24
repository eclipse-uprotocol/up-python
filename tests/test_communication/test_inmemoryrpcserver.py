"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import copy
import unittest
from typing import Dict
from unittest.mock import AsyncMock, MagicMock

from tests.test_communication.mock_utransport import EchoUTransport
from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.inmemoryrpcclient import InMemoryRpcClient
from uprotocol.communication.inmemoryrpcserver import InMemoryRpcServer
from uprotocol.communication.requesthandler import RequestHandler
from uprotocol.communication.upayload import UPayload
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class TestInMemoryRpcServer(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_transport = MagicMock(spec=UTransport)
        self.mock_handler = MagicMock(spec=RequestHandler)

    @staticmethod
    def create_method_uri():
        return UUri(authority_name="Neelam", ue_id=4, ue_version_major=1, resource_id=3)

    def test_constructor_transport_none(self):
        with self.assertRaises(ValueError) as context:
            InMemoryRpcServer(None)
        self.assertEqual(str(context.exception), UTransport.TRANSPORT_NULL_ERROR)

    def test_constructor_transport_not_instance(self):
        with self.assertRaises(ValueError) as context:
            InMemoryRpcServer("Invalid Transport")
        self.assertEqual(str(context.exception), UTransport.TRANSPORT_NOT_INSTANCE_ERROR)

    async def test_register_request_handler_method_uri_none(self):
        self.mock_handler.handle_request = MagicMock(return_value=UPayload.EMPTY)
        server = InMemoryRpcServer(self.mock_transport)
        status = await server.register_request_handler(None, self.mock_handler)
        self.assertEqual(status.code, UCode.INVALID_ARGUMENT)

        self.mock_handler.handle_request.assert_not_called()

    async def test_register_request_handler_handler_none(self):
        server = InMemoryRpcServer(self.mock_transport)
        status = await server.register_request_handler(self.create_method_uri(), None)
        self.assertEqual(status.code, UCode.INVALID_ARGUMENT)

    async def test_unregister_request_handler_method_uri_none(self):
        self.mock_handler.handle_request = MagicMock(return_value=UPayload.EMPTY)
        server = InMemoryRpcServer(self.mock_transport)
        status = await server.unregister_request_handler(None, self.mock_handler)
        self.assertEqual(status.code, UCode.INVALID_ARGUMENT)
        self.mock_handler.assert_not_called()

    async def test_unregister_request_handler_handler_none(self):
        server = InMemoryRpcServer(self.mock_transport)

        status = await server.unregister_request_handler(self.create_method_uri(), None)
        self.assertEqual(status.code, UCode.INVALID_ARGUMENT)

    async def test_register_request_handler(self):
        self.mock_handler.handle_request = MagicMock(return_value=UPayload.EMPTY)

        # Create instance of InMemoryRpcServer with mocked dependencies
        server = InMemoryRpcServer(self.mock_transport)
        # Mock the return value of transport.register_listener
        self.mock_transport.register_listener = AsyncMock(return_value=UStatus(code=UCode.OK))
        result = await server.register_request_handler(self.create_method_uri(), self.mock_handler)
        # Assert the result
        self.assertEqual(result.code, UCode.OK)
        self.mock_transport.register_listener.assert_called_once()

    async def test_registering_twice_the_same_request_handler(self):
        self.mock_transport.register_listener = AsyncMock(return_value=UStatus(code=UCode.OK))
        self.mock_handler.handle_request = MagicMock(return_value=UPayload.EMPTY)

        # Create instance of InMemoryRpcServer with mocked dependencies
        server = InMemoryRpcServer(self.mock_transport)
        status = await server.register_request_handler(self.create_method_uri(), self.mock_handler)
        self.assertEqual(status.code, UCode.OK)
        status = await server.register_request_handler(self.create_method_uri(), self.mock_handler)
        self.assertEqual(status.code, UCode.ALREADY_EXISTS)
        self.mock_transport.register_listener.assert_called_once()

    async def test_unregistering_non_registered_request_handler(self):
        self.mock_transport.register_listener = AsyncMock(return_value=UStatus(code=UCode.OK))
        handler = MagicMock(side_effect=NotImplementedError("Unimplemented method 'handleRequest'"))

        # Create instance of InMemoryRpcServer with mocked dependencies
        server = InMemoryRpcServer(self.mock_transport)

        status = await server.unregister_request_handler(self.create_method_uri(), handler)
        self.assertEqual(status.code, UCode.NOT_FOUND)

    async def test_registering_request_listener_with_error_transport(self):
        self.mock_transport.register_listener = AsyncMock(return_value=UStatus(code=UCode.FAILED_PRECONDITION))
        self.mock_handler.handle_request = MagicMock(return_value=UPayload.EMPTY)

        # Create instance of InMemoryRpcServer with mocked dependencies
        server = InMemoryRpcServer(self.mock_transport)
        status = await server.register_request_handler(self.create_method_uri(), self.mock_handler)
        self.assertEqual(status.code, UCode.FAILED_PRECONDITION)
        self.mock_transport.register_listener.assert_called_once()

    async def test_handle_requests(self):
        listeners: Dict[str, UListener] = {}

        async def custom_register_listener_behavior(source: UUri, listener: UListener, sink: UUri = None) -> UStatus:
            topic = UriSerializer().serialize(sink)

            if topic not in listeners:
                listeners[topic] = listener
            return UStatus(code=UCode.OK)

        self.mock_transport.register_listener = AsyncMock(side_effect=custom_register_listener_behavior)
        self.mock_transport.get_source.return_value = UUri(authority_name="Neelam", ue_id=4, ue_version_major=1)

        async def custom_send_behavior(message):
            serialized_uri = UriSerializer().serialize(message.attributes.sink)
            if serialized_uri in listeners:
                await listeners[serialized_uri].on_receive(message)
            return UStatus(code=UCode.OK)

        self.mock_transport.send = AsyncMock(side_effect=custom_send_behavior)

        mock_handler = MagicMock(spec=RequestHandler)
        mock_handler.handle_request = MagicMock(return_value=UPayload.EMPTY)
        # Create instance of InMemoryRpcServer with mocked dependencies
        server = InMemoryRpcServer(self.mock_transport)
        method = self.create_method_uri()
        method2 = copy.deepcopy(method)
        # Update the resource_id
        method2.resource_id = 69

        self.assertEqual((await server.register_request_handler(method, mock_handler)).code, UCode.OK)
        request = UMessageBuilder.request(self.mock_transport.get_source(), method2, 1000).build()

        # fake sending a request message that will trigger the handler to be called but since it is
        # not for the same method as the one registered, it should be ignored and the handler not called
        self.assertEqual((await self.mock_transport.send(request)).code, UCode.OK)
        self.mock_transport.register_listener.assert_called_once()
        self.mock_transport.send.assert_called_once()

        request = UMessageBuilder.request(self.mock_transport.get_source(), method, 1000).build()

        # fake sending a request message that will trigger the handler to be called.
        self.assertEqual((await self.mock_transport.send(request)).code, UCode.OK)
        mock_handler.handle_request.assert_called_once()

    def test_rpcserver_constructor_transport_none(self):
        with self.assertRaises(ValueError) as context:
            InMemoryRpcServer(None)
        self.assertEqual(str(context.exception), UTransport.TRANSPORT_NULL_ERROR)

    def test_rpcserver_constructor_transport_not_instance(self):
        with self.assertRaises(ValueError) as context:
            InMemoryRpcServer("InvalidTransport")
        self.assertEqual(str(context.exception), UTransport.TRANSPORT_NOT_INSTANCE_ERROR)

    async def test_register_request_handler_null_parameters(self):
        server = InMemoryRpcServer(self.mock_transport)
        status = await server.register_request_handler(None, None)
        self.assertEqual(status.code, UCode.INVALID_ARGUMENT)

    async def test_handle_requests_exception(self):
        transport = EchoUTransport()
        exception = UStatusError.from_code_message(UCode.FAILED_PRECONDITION, "Not permitted")

        self.mock_handler.handle_request.side_effect = MagicMock(side_effect=exception)
        # Create instance of InMemoryRpcServer with mocked dependencies
        server = InMemoryRpcServer(transport)
        method = self.create_method_uri()

        self.assertEqual((await server.register_request_handler(method, self.mock_handler)).code, UCode.OK)
        request = UMessageBuilder.request(transport.get_source(), method, 1000).build()

        # fake sending a request message that will trigger the handler to be called
        status = await transport.send(request)
        self.assertEqual(status.code, UCode.OK)

    async def test_end_to_end_rpc_with_test_transport(self):
        class MyRequestHandler(RequestHandler):
            def handle_request(self, message: UMessage) -> UPayload:
                return UPayload.pack(UUri())

        handler = MyRequestHandler()
        test_transport = EchoUTransport()
        server = InMemoryRpcServer(test_transport)
        method = self.create_method_uri()

        self.assertEqual((await server.register_request_handler(method, handler)).code, UCode.OK)
        rpc_client = InMemoryRpcClient(test_transport)
        response = await rpc_client.invoke_method(method, None, CallOptions.DEFAULT)
        self.assertIsNotNone(response)
        self.assertEqual(response, UPayload.pack(UUri()))


if __name__ == '__main__':
    unittest.main()
