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

from multimethod import multimethod
from concurrent.futures import Future

from uprotocol.client.transport_wrapper import TransportWrapper
from uprotocol.client.ustatus_exception import UStatusException
from uprotocol.transport.builder.umessage_builder import UMessageBuilder
from uprotocol.transport.ulistener import UListener

from uprotocol.proto.uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.proto.uprotocol.v1.uattributes_pb2 import UMessageType
from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UCode


class RequestListener(TransportWrapper, UListener):
    """
    RequestListener is an interface that provides the API to receive requests
    and send responses.
    """

    @multimethod
    def on_receive(self, message: UMessage, response_future: Future):
        """
        Method called to handle/process events.

        @param message Message received.
        @param response_future Future to complete with the response.
        """
        pass

    @multimethod
    def on_receive(self, message: UMessage):
        """
        Callback method that a transport calls to process the request message.

        The RequestListener implements this call back to handle the
        request and automatically send a response message for the RpcServer.

        @param message Message received.
        """
        response_future = Future()

        if message.attributes.type != UMessageType.UMESSAGE_TYPE_REQUEST:
            response_future.set_exception(
                UStatusException(
                    code=UCode.INVALID_ARGUMENT, message="Invalid message type"
                )
            )
            return

        def handle_response(response_payload):
            response = UMessageBuilder.response(message.attributes)
            if response_payload.exception:
                response.with_commstatus(response_payload.exception.code)
            if response_payload.result:
                response.build(
                    response_payload.result.format,
                    response_payload.result.data,
                )
            else:
                response.build()
            self.get_transport().send(response)

        response_future.add_done_callback(handle_response)
