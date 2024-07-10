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
from unittest.mock import MagicMock

from tests.test_communication.mock_utransport import (
    ErrorUTransport,
    MockUTransport,
)
from uprotocol.communication.inmemoryrpcserver import InMemoryRpcServer
from uprotocol.communication.requesthandler import RequestHandler
from uprotocol.communication.upayload import UPayload
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.utransport import UTransport
from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
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
        server = InMemoryRpcServer(MockUTransport())
        handler = MagicMock(return_value=UPayload.EMPTY)

        with self.assertRaises(ValueError) as context:
            await server.register_request_handler(None, handler)
        self.assertEqual(str(context.exception), "Method URI missing")

    async def test_register_request_handler_handler_none(self):
        server = InMemoryRpcServer(MockUTransport())
        with self.assertRaises(ValueError) as context:
            await server.register_request_handler(self.create_method_uri(), None)
        self.assertEqual(str(context.exception), "Request listener missing")

    async def test_unregister_request_handler_method_uri_none(self):
        server = InMemoryRpcServer(MockUTransport())
        handler = MagicMock(return_value=UPayload.EMPTY)

        with self.assertRaises(ValueError) as context:
            await server.unregister_request_handler(None, handler)
        self.assertEqual(str(context.exception), "Method URI missing")

    async def test_unregister_request_handler_handler_none(self):
        server = InMemoryRpcServer(MockUTransport())
        with self.assertRaises(ValueError) as context:
            await server.unregister_request_handler(self.create_method_uri(), None)
        self.assertEqual(str(context.exception), "Request listener missing")

    async def test_registering_request_listener(self):
        handler = MagicMock(return_value=UPayload.EMPTY)
        method = self.create_method_uri()
        server = InMemoryRpcServer(MockUTransport())
        self.assertEqual((await server.register_request_handler(method, handler)).code, UCode.OK)
        self.assertEqual((await server.unregister_request_handler(method, handler)).code, UCode.OK)

    async def test_registering_twice_the_same_request_handler(self):
        handler = MagicMock(return_value=UPayload.EMPTY)
        server = InMemoryRpcServer(MockUTransport())
        status = await server.register_request_handler(self.create_method_uri(), handler)
        self.assertEqual(status.code, UCode.OK)
        status = await server.register_request_handler(self.create_method_uri(), handler)
        self.assertEqual(status.code, UCode.ALREADY_EXISTS)

    async def test_unregistering_non_registered_request_handler(self):
        handler = MagicMock(side_effect=NotImplementedError("Unimplemented method 'handleRequest'"))
        server = InMemoryRpcServer(MockUTransport())
        status = await server.unregister_request_handler(self.create_method_uri(), handler)
        self.assertEqual(status.code, UCode.NOT_FOUND)

    async def test_registering_request_listener_with_error_transport(self):
        handler = MagicMock(return_value=UPayload.EMPTY)
        server = InMemoryRpcServer(ErrorUTransport())
        status = await server.register_request_handler(self.create_method_uri(), handler)
        self.assertEqual(status.code, UCode.FAILED_PRECONDITION)

    async def test_handle_requests(self):
        class CustomTestUTransport(MockUTransport):
            async def send(self, message):
                serialized_uri = UriSerializer().serialize(message.attributes.sink)
                if serialized_uri in self.listeners:
                    for listener in self.listeners[serialized_uri]:
                        listener.on_receive(message)
                return UStatus(code=UCode.OK)

        transport = CustomTestUTransport()
        handler = MagicMock(side_effect=Exception("this should not be called"))
        server = InMemoryRpcServer(transport)
        method = self.create_method_uri()
        method2 = copy.deepcopy(method)
        # Update the resource_id
        method2.resource_id = 69

        self.assertEqual((await server.register_request_handler(method, handler)).code, UCode.OK)

        request = UMessageBuilder.request(transport.get_source(), method2, 1000).build()

        # fake sending a request message that will trigger the handler to be called but since it is
        # not for the same method as the one registered, it should be ignored and the handler not called
        self.assertEqual((await transport.send(request)).code, UCode.OK)

    async def test_handle_requests_exception(self):
        # test transport that will trigger the handleRequest()
        class CustomTestUTransport(MockUTransport):
            async def send(self, message):
                serialized_uri = UriSerializer().serialize(message.attributes.sink)
                if serialized_uri in self.listeners:
                    for listener in self.listeners[serialized_uri]:
                        listener.on_receive(message)
                return UStatus(code=UCode.OK)

        transport = CustomTestUTransport()

        class MyRequestHandler(RequestHandler):
            def handle_request(self, message: UMessage) -> UPayload:
                raise UStatusError(UStatus(code=UCode.FAILED_PRECONDITION, message="Neelam it failed!"))

        handler = MyRequestHandler()
        server = InMemoryRpcServer(transport)
        method = self.create_method_uri()

        self.assertEqual((await server.register_request_handler(method, handler)).code, UCode.OK)

        request = UMessageBuilder.request(transport.get_source(), method, 1000).build()
        self.assertEqual((await transport.send(request)).code, UCode.OK)

    async def test_handle_requests_unknown_exception(self):
        class CustomTestUTransport(MockUTransport):
            async def send(self, message):
                serialized_uri = UriSerializer().serialize(message.attributes.sink)
                if serialized_uri in self.listeners:
                    for listener in self.listeners[serialized_uri]:
                        listener.on_receive(message)
                return UStatus(code=UCode.OK)

        transport = CustomTestUTransport()

        class MyRequestHandler(RequestHandler):
            def handle_request(self, message: UMessage) -> UPayload:
                raise Exception("Neelam it failed!")

        handler = MyRequestHandler()
        server = InMemoryRpcServer(transport)
        method = self.create_method_uri()

        self.assertEqual((await server.register_request_handler(method, handler)).code, UCode.OK)

        request = UMessageBuilder.request(transport.get_source(), method, 1000).build()
        self.assertEqual((await transport.send(request)).code, UCode.OK)


if __name__ == '__main__':
    unittest.main()
