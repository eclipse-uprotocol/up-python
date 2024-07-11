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

from uprotocol.communication.inmemoryrpcserver import InMemoryRpcServer
from uprotocol.communication.requesthandler import RequestHandler
from uprotocol.communication.upayload import UPayload
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class TestInMemoryRpcServer(unittest.IsolatedAsyncioTestCase):
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
        # Mock the transport and handler
        mock_transport = MagicMock(spec=UTransport)
        mock_handler = MagicMock(spec=RequestHandler)
        mock_handler.handle_request = MagicMock(return_value=UPayload.EMPTY)
        server = InMemoryRpcServer(mock_transport)

        with self.assertRaises(ValueError) as context:
            await server.register_request_handler(None, mock_handler)
        self.assertEqual(str(context.exception), "Method URI missing")
        mock_handler.handle_request.assert_not_called()

    async def test_register_request_handler_handler_none(self):
        # Mock the transport and handler
        mock_transport = MagicMock(spec=UTransport)
        server = InMemoryRpcServer(mock_transport)
        with self.assertRaises(ValueError) as context:
            await server.register_request_handler(self.create_method_uri(), None)
        self.assertEqual(str(context.exception), "Request listener missing")

    async def test_unregister_request_handler_method_uri_none(self):
        # Mock the transport and handler
        mock_transport = MagicMock(spec=UTransport)
        mock_handler = MagicMock(spec=RequestHandler)
        mock_handler.handle_request = MagicMock(return_value=UPayload.EMPTY)
        server = InMemoryRpcServer(mock_transport)

        with self.assertRaises(ValueError) as context:
            await server.unregister_request_handler(None, mock_handler)
        self.assertEqual(str(context.exception), "Method URI missing")
        mock_handler.assert_not_called()

    async def test_unregister_request_handler_handler_none(self):
        # Mock the transport and handler
        mock_transport = MagicMock(spec=UTransport)
        server = InMemoryRpcServer(mock_transport)
        with self.assertRaises(ValueError) as context:
            await server.unregister_request_handler(self.create_method_uri(), None)
        self.assertEqual(str(context.exception), "Request listener missing")

    async def test_register_request_handler(self):
        # Mock the transport and handler
        mock_transport = MagicMock(spec=UTransport)
        mock_handler = MagicMock(spec=RequestHandler)
        mock_handler.handle_request = MagicMock(return_value=UPayload.EMPTY)

        # Create instance of InMemoryRpcServer with mocked dependencies
        server = InMemoryRpcServer(mock_transport)
        # Mock the return value of transport.register_listener
        mock_transport.register_listener = AsyncMock(return_value=UStatus(code=UCode.OK))
        result = await server.register_request_handler(self.create_method_uri(), mock_handler)
        # Assert the result
        self.assertEqual(result.code, UCode.OK)
        mock_transport.register_listener.assert_called_once()

    async def test_registering_twice_the_same_request_handler(self):
        # Mock the transport and handler
        mock_transport = MagicMock(spec=UTransport)
        mock_transport.register_listener = AsyncMock(return_value=UStatus(code=UCode.OK))
        mock_handler = MagicMock(spec=RequestHandler)
        mock_handler.handle_request = MagicMock(return_value=UPayload.EMPTY)

        # Create instance of InMemoryRpcServer with mocked dependencies
        server = InMemoryRpcServer(mock_transport)
        status = await server.register_request_handler(self.create_method_uri(), mock_handler)
        self.assertEqual(status.code, UCode.OK)
        status = await server.register_request_handler(self.create_method_uri(), mock_handler)
        self.assertEqual(status.code, UCode.ALREADY_EXISTS)
        mock_transport.register_listener.assert_called_once()

    async def test_unregistering_non_registered_request_handler(self):
        # Mock the transport and handler
        mock_transport = MagicMock(spec=UTransport)
        mock_transport.register_listener = AsyncMock(return_value=UStatus(code=UCode.OK))
        mock_handler = MagicMock(side_effect=NotImplementedError("Unimplemented method 'handleRequest'"))

        # Create instance of InMemoryRpcServer with mocked dependencies
        server = InMemoryRpcServer(mock_transport)

        status = await server.unregister_request_handler(self.create_method_uri(), mock_handler)
        self.assertEqual(status.code, UCode.NOT_FOUND)

    async def test_registering_request_listener_with_error_transport(self):
        # Mock the transport and handler
        mock_transport = MagicMock(spec=UTransport)
        mock_transport.register_listener = AsyncMock(return_value=UStatus(code=UCode.FAILED_PRECONDITION))
        mock_handler = MagicMock(spec=RequestHandler)
        mock_handler.handle_request = MagicMock(return_value=UPayload.EMPTY)

        # Create instance of InMemoryRpcServer with mocked dependencies
        server = InMemoryRpcServer(mock_transport)
        status = await server.register_request_handler(self.create_method_uri(), mock_handler)
        self.assertEqual(status.code, UCode.FAILED_PRECONDITION)
        mock_transport.register_listener.assert_called_once()

    async def test_handle_requests(self):
        # Mock the transport and handler
        mock_transport = MagicMock(spec=UTransport)
        listeners: Dict[str, UListener] = {}

        async def custom_register_listener_behavior(source: UUri, listener: UListener, sink: UUri = None) -> UStatus:
            topic = UriSerializer().serialize(sink)

            if topic not in listeners:
                listeners[topic] = listener
            return UStatus(code=UCode.OK)

        mock_transport.register_listener = AsyncMock(side_effect=custom_register_listener_behavior)
        mock_transport.get_source = MagicMock(return_value=UUri(authority_name="Neelam", ue_id=4, ue_version_major=1))

        async def custom_send_behavior(message):
            serialized_uri = UriSerializer().serialize(message.attributes.sink)
            if serialized_uri in listeners:
                listeners[serialized_uri].on_receive(message)
            return UStatus(code=UCode.OK)

        mock_transport.send = AsyncMock(side_effect=custom_send_behavior)

        mock_handler = MagicMock(spec=RequestHandler)
        mock_handler.handle_request = MagicMock(return_value=UPayload.EMPTY)
        # Create instance of InMemoryRpcServer with mocked dependencies
        server = InMemoryRpcServer(mock_transport)
        method = self.create_method_uri()
        method2 = copy.deepcopy(method)
        # Update the resource_id
        method2.resource_id = 69

        self.assertEqual((await server.register_request_handler(method, mock_handler)).code, UCode.OK)
        request = UMessageBuilder.request(mock_transport.get_source(), method2, 1000).build()

        # fake sending a request message that will trigger the handler to be called but since it is
        # not for the same method as the one registered, it should be ignored and the handler not called
        self.assertEqual((await mock_transport.send(request)).code, UCode.OK)
        mock_transport.register_listener.assert_called_once()
        mock_transport.send.assert_called_once()

        request = UMessageBuilder.request(mock_transport.get_source(), method, 1000).build()

        # fake sending a request message that will trigger the handler to be called.
        self.assertEqual((await mock_transport.send(request)).code, UCode.OK)
        mock_handler.handle_request.assert_called_once()

    def test_subscriber_constructor_transport_none(self):
        with self.assertRaises(ValueError) as context:
            InMemoryRpcServer(None)
        self.assertEqual(str(context.exception), UTransport.TRANSPORT_NULL_ERROR)

    def test_subscriber_constructor_transport_not_instance(self):
        with self.assertRaises(ValueError) as context:
            InMemoryRpcServer("InvalidTransport")
        self.assertEqual(str(context.exception), UTransport.TRANSPORT_NOT_INSTANCE_ERROR)


if __name__ == '__main__':
    unittest.main()
