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

from concurrent.futures import Future
from google.protobuf.message import Message

from uprotocol.client.call_options import CallOptions
from uprotocol.client.ustatus_exception import UStatusException
from uprotocol.client.transport_wrapper import TransportWrapper
from uprotocol.transport.builder.umessage_builder import UMessageBuilder
from uprotocol.client.upayload import UPayload

from uprotocol.proto.uprotocol.v1.uattributes_pb2 import (
    UMessageType,
    UPayloadFormat,
)
from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UCode, UStatus
from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri


class RpcClient(TransportWrapper):
    """
    The interface provides a clean contract for mapping an RPC request to a
    response.
    """

    def _invoke_method_static(
        self, method_uri: UUri, request_payload: UPayload, options: CallOptions
    ):
        transport = self.get_transport()
        builder = UMessageBuilder.request(
            method_uri, transport.get_source(), options.timeout
        )
        request = None

        if request_payload is not None:
            request = builder.build(
                request_payload.get_format(), request_payload.get_data()
            )
        else:
            request = builder.build()

        response_payload = Future()

        def on_receive(response):
            if response.attributes.type == UMessageType.UMESSAGE_TYPE_RESPONSE:
                response_payload.set_result(
                    UPayload(
                        data=response.payload,
                        format=response.attributes.payload_format,
                    )
                )
                transport.unregister_listener(
                    method_uri,
                    response.attributes.source,
                    response.attributes.sink,
                )
            else:
                response_payload.set_exception(
                    UStatusException(
                        status=UStatus(
                            code=UCode.INTERNAL,
                            message="Failed to send request",
                        )
                    )
                )

        transport.register_listener(
            method_uri, transport.get_source(), on_receive
        )

        result = transport.send(request)
        if result.code != UCode.OK:
            response_payload.set_exception(
                UStatusException(
                    status=UStatus(
                        code=UCode.INTERNAL, message="Failed to send request"
                    )
                )
            )

        return response_payload

    def invoke_method(self, method_uri: UUri, arg2, arg3=None):
        """
        Overloaded method to handle different signatures for
        invoking RPC methods.
        """
        if isinstance(arg2, Message) and arg3 is None:
            return self._invoke_method_static(
                method_uri,
                UPayload(
                    format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF,
                    data=arg2.SerializeToString(),
                ),
                CallOptions(),
            )
        elif isinstance(arg2, UPayload) and arg3 is None:
            return self._invoke_method_static(
                method_uri,
                arg2,
                CallOptions(),
            )
        elif isinstance(arg2, UPayload) and isinstance(arg3, CallOptions):
            return self._invoke_method_static(method_uri, arg2, arg3)
        else:
            raise TypeError("Invalid arguments for invoke_method")
