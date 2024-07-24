"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from uprotocol.communication.requesthandler import RequestHandler
from uprotocol.communication.rpcserver import RpcServer
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.uri.factory.uri_factory import UriFactory
from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.v1.uattributes_pb2 import (
    UMessageType,
)
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class HandleRequestListener(UListener):
    def __init__(self, transport: UTransport, request_handlers):
        self.transport = transport
        self.request_handlers = request_handlers

    async def on_receive(self, request: UMessage) -> None:
        """
        Generic incoming handler to process RPC requests from clients.

        :param request: The request message from clients.
        """
        # Only handle request messages, ignore all other messages like notifications
        if request.attributes.type != UMessageType.UMESSAGE_TYPE_REQUEST:
            return

        request_attributes = request.attributes

        # Check if the request is for one that we have registered a handler for, if not ignore it
        handler = self.request_handlers.get(UriSerializer().serialize(request_attributes.sink))
        if handler is None:
            return

        response_builder = UMessageBuilder.response_for_request(request_attributes)

        try:
            response_payload = handler.handle_request(request)
        except Exception as e:
            code = UCode.INTERNAL
            response_payload = None
            if isinstance(e, UStatusError):
                code = e.get_code()
            response_builder.with_commstatus(code)
        await self.transport.send(response_builder.build_from_upayload(response_payload))


class InMemoryRpcServer(RpcServer):
    def __init__(self, transport):
        if not transport:
            raise ValueError(UTransport.TRANSPORT_NULL_ERROR)
        elif not isinstance(transport, UTransport):
            raise ValueError(UTransport.TRANSPORT_NOT_INSTANCE_ERROR)
        self.transport = transport
        self.request_handlers = {}
        self.request_handler = HandleRequestListener(self.transport, self.request_handlers)

    async def register_request_handler(self, method_uri: UUri, handler: RequestHandler) -> UStatus:
        """
        Register a handler that will be invoked when requests come in from clients for the given method.

        Note: Only one handler is allowed to be registered per method URI.

        :param method_uri: The URI for the method to register the listener for.
        :param handler: The handler that will process the request for the client.
        :return: Returns the status of registering the RpcListener.
        """

        if method_uri is None or handler is None:
            return UStatus(code=UCode.INVALID_ARGUMENT, message="Method URI or handler missing")

        try:
            method_uri_str = UriSerializer().serialize(method_uri)
            if method_uri_str in self.request_handlers:
                current_handler = self.request_handlers[method_uri_str]
                if current_handler is not None:
                    raise UStatusError.from_code_message(UCode.ALREADY_EXISTS, "Handler already registered")

            result = await self.transport.register_listener(UriFactory.ANY, self.request_handler, method_uri)
            if result.code != UCode.OK:
                raise UStatusError.from_code_message(result.code, result.message)

            self.request_handlers[method_uri_str] = handler
            return UStatus(code=UCode.OK)

        except UStatusError as e:
            return UStatus(code=e.get_code(), message=e.get_message())

    async def unregister_request_handler(self, method_uri: UUri, handler: RequestHandler) -> UStatus:
        """
        Unregister a handler that will be invoked when requests come in from clients for the given method.

        :param method_uri: The resolved UUri where the listener was registered to receive messages from.
        :param handler: The handler for processing requests.
        :return: Returns the status of unregistering the RpcListener.
        """
        if method_uri is None or handler is None:
            return UStatus(code=UCode.INVALID_ARGUMENT, message="Method URI or handler missing")

        method_uri_str = UriSerializer().serialize(method_uri)

        if self.request_handlers.get(method_uri_str) == handler:
            del self.request_handlers[method_uri_str]
            return await self.transport.unregister_listener(UriFactory.ANY, self.request_handler, method_uri)

        return UStatus(code=UCode.NOT_FOUND)
