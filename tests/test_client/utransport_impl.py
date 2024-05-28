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

from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri
from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UStatus, UCode
from uprotocol.proto.uprotocol.v1.uattributes_pb2 import UMessageType

from uprotocol.transport.builder.umessage_builder import UMessageBuilder
from uprotocol.transport.utransport import UTransport
from uprotocol.transport.validate.uattributesvalidator import (
    UAttributesValidator,
)
from uprotocol.validation.validationresult import ValidationResult


class UTransportImpl(UTransport):

    class Key:

        def __init__(self, source: UUri, sink: UUri):
            self.source = source
            self.sink = sink

        def get_source(self) -> UUri:
            return self.source

        def get_sink(self) -> UUri:
            return self.sink

    def __init__(self, source: UUri):
        self.source = source
        self.mlisteners = {}

    def send(self, message):
        validator = UAttributesValidator.get_validator(message.attributes)

        if (
            message is None
            or validator.validate(message.attributes)
            != ValidationResult.success()
        ):
            return UStatus(
                code=UCode.INVALID_ARGUMENT,
                message="Invalid message attributes",
            )

        # The following is test code to generate a response from a request
        if message.attributes.type == UMessageType.UMESSAGE_TYPE_REQUEST:
            response = UMessageBuilder.response(message.attributes).build()
            for key, listener in self.mlisteners.items():
                if (
                    key.source == message.attributes.source
                    or key.sink == message.attributes.sink
                ):
                    listener(response)

        return UStatus(code=UCode.OK)

    def register_listener(self, source: UUri, sink: UUri, listener):
        key = UTransportImpl.Key(source, sink)
        self.mlisteners[key] = listener
        return UStatus(code=UCode.OK)

    def unregister_listener(self, source: UUri, sink: UUri, listener):
        key = UTransportImpl.Key(source, sink)
        self.mlisteners.pop(key, None)
        return UStatus(code=UCode.OK)

    def get_source(self) -> UUri:
        return self.source
