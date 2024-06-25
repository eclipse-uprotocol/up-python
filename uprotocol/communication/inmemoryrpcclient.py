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
from typing import Dict, Optional

from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.rpcclient import RpcClient
from uprotocol.communication.upayload import UPayload
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.uri.factory.uri_factory import UriFactory
from uprotocol.uuid.serializer.uuidserializer import UuidSerializer
from uprotocol.v1.uattributes_pb2 import UMessageType
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri


class HandleResponsesListener(UListener):
    def __init__(self, requests):
        self.requests = requests

    def on_receive(self, umsg: UMessage) -> None:
        """
        Handle the responses coming back from the server asynchronously.

        Args:
        - response (UMessage): The response message from the server.
        """
        if umsg.attributes.type != UMessageType.UMESSAGE_TYPE_RESPONSE:
            return
        time.sleep(1)
        print("received rpc request")

        response_attributes = umsg.attributes
        future = self.requests.pop(UuidSerializer.serialize(response_attributes.reqid), None)

        if not future:
            return

        if response_attributes.commstatus:
            code = response_attributes.commstatus
            future.set_exception(UStatusError.from_code_message(code=code, message=f"Communication error [{code}]"))
            return

        future.set_result(umsg)


class InMemoryRpcClient(RpcClient):
    """
    An example implementation of the RpcClient interface that
    wraps the UTransport for implementing the RPC pattern to send
    RPC requests and receive RPC responses. This implementation
    uses an in-memory map to store futures that need to be
    completed when the response comes in from the server.

    NOTE: Developers are not required to use these APIs; they can
    implement their own or directly use the UTransport to send RPC
    requests and register listeners that handle the RPC responses.
    """

    def __init__(self, transport: UTransport):
        """
        Constructor for the InMemoryRpcClient.

        :param transport: The transport to use for sending the RPC requests.
        """
        if not transport:
            raise ValueError(UTransport.TRANSPORT_NULL_ERROR)
        elif not isinstance(transport, UTransport):
            raise ValueError(UTransport.TRANSPORT_NOT_INSTANCE_ERROR)
        self.transport = transport
        self.requests: Dict[str, asyncio.Future] = {}
        self.response_handler: UListener = HandleResponsesListener(self.requests)

        status = self.transport.register_listener(UriFactory.ANY, self.response_handler, self.transport.get_source())
        if status.code != UCode.OK:
            raise UStatusError.from_code_message(status.code, "Failed to register listener")

    async def invoke_method(
        self, method_uri: UUri, request_payload: UPayload, options: Optional[CallOptions] = None
    ) -> UPayload:
        """
        Invoke a method (send an RPC request) and receive the response asynchronously.

        :param method_uri: The method URI to be invoked.
        :param request_payload: The request message to be sent to the server.
        :param options: RPC method invocation call options. Defaults to None.
        :return: Returns the asyncio Future with the response payload or raises an exception
                 with the failure reason as UStatus.
        """
        global future
        options = options or CallOptions.DEFAULT
        builder = UMessageBuilder.request(self.transport.get_source(), method_uri, options.timeout)

        try:
            if options.token:
                builder.with_token(options.token)

            request = builder.build_from_upayload(request_payload)

            future = asyncio.Future()

            def cleanup_request(request_id):
                request_id = UuidSerializer.serialize(request_id)
                if request_id in self.requests:
                    del self.requests[request_id]

            self.requests[UuidSerializer.serialize(request.attributes.id)] = None

            status = self.transport.send(request)
            if status.code == UCode.OK:
                response_future = asyncio.Future()

                async def wait_for_response():
                    try:
                        response_message = await asyncio.wait_for(
                            response_future, timeout=request.attributes.ttl / 1000
                        )
                        return UPayload.pack_from_data_and_format(
                            response_message.payload, response_message.attributes.payload_format
                        )
                    except asyncio.TimeoutError:
                        cleanup_request(request.attributes.id)
                        raise TimeoutError(
                            f"Timeout occurred while waiting for response to request {request.attributes.id}"
                        )
                    except Exception as e:
                        cleanup_request(request.attributes.id)
                        raise e

                asyncio.create_task(wait_for_response())

                response_future.add_done_callback(lambda fut: cleanup_request(request.attributes.id))

                self.requests[UuidSerializer.serialize(request.attributes.id)] = response_future

                return await wait_for_response()
            else:
                raise UStatusError(status)

        except Exception as e:
            if not future.done():
                future.set_exception(e)

    def close(self):
        """
        Close the InMemoryRpcClient by clearing stored requests and unregistering the listener.
        """
        self.requests.clear()
        self.transport.unregister_listener(UriFactory.ANY, self.response_handler, self.transport.get_source())
