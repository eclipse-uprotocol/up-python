"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import threading
from abc import ABC
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from uprotocol.communication.upayload import UPayload
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.transport.validator.uattributesvalidator import UAttributesValidator
from uprotocol.uri.factory.uri_factory import UriFactory
from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.v1.uattributes_pb2 import (
    UMessageType,
)
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus
from uprotocol.validation.validationresult import ValidationResult


class MockUTransport(UTransport):
    def get_source(self) -> UUri:
        return self.source

    def __init__(self, source=None):
        super().__init__()
        self.source = source if source else UUri(authority_name="Neelam", ue_id=4, ue_version_major=1)
        self.listeners: Dict[str, List[UListener]] = {}
        self.lock = threading.Lock()

    def build_response(self, request: UMessage):
        payload = UPayload.pack_from_data_and_format(request.payload, request.attributes.payload_format)

        return UMessageBuilder.response_for_request(request.attributes).build_from_upayload(payload)

    def close(self):
        self.listeners.clear()

    def register_listener(self, source_filter: UUri, listener: UListener, sink_filter: UUri = None) -> UStatus:
        with self.lock:
            if sink_filter is not None:  # method uri
                topic = UriSerializer().serialize(sink_filter)
            else:
                topic = UriSerializer().serialize(source_filter)

            if topic not in self.listeners:
                self.listeners[topic] = []
            self.listeners[topic].append(listener)
            return UStatus(code=UCode.OK)

    def unregister_listener(self, source: UUri, listener: UListener, sink: UUri = None) -> UStatus:
        with self.lock:
            if sink is not None:  # method uri
                topic = UriSerializer().serialize(sink)
            else:
                topic = UriSerializer().serialize(source)

            if topic in self.listeners and listener in self.listeners[topic]:
                self.listeners[topic].remove(listener)
                if not self.listeners[topic]:  # If the list is empty, remove the key
                    del self.listeners[topic]
                code = UCode.OK
            else:
                code = UCode.INVALID_ARGUMENT
            result = UStatus(code=code)
        return result

    def send(self, message: UMessage) -> UStatus:
        validator = UAttributesValidator.get_validator(message.attributes)
        with self.lock:
            if message is None or validator.validate(message.attributes) != ValidationResult.success():
                return UStatus(code=UCode.INVALID_ARGUMENT, message="Invalid message attributes")

            threading.Thread(target=self._notify_listeners, args=(message,)).start()

        return UStatus(code=UCode.OK)

    def _notify_listeners(self, umsg):
        if umsg.attributes.type == UMessageType.UMESSAGE_TYPE_PUBLISH:
            for key, listeners in self.listeners.items():
                uri = UriSerializer().deserialize(key)
                if not (UriValidator.is_rpc_method(uri) or UriValidator.is_rpc_response(uri)):
                    for listener in listeners:
                        listener.on_receive(umsg)

        else:
            if umsg.attributes.type == UMessageType.UMESSAGE_TYPE_REQUEST:
                serialized_uri = UriSerializer().serialize(umsg.attributes.sink)
                if serialized_uri not in self.listeners:
                    # no listener registered for method uri, send dummy response.
                    # This case will only come for request type
                    # as for response type, there will always be response handler as it is in up client
                    serialized_uri = UriSerializer().serialize(UriFactory.ANY)
                    umsg = self.build_response(umsg)
            else:
                # this is for response type,handle response
                serialized_uri = UriSerializer().serialize(UriFactory.ANY)

            for listener in self.listeners[serialized_uri]:
                listener.on_receive(umsg)
                break  # as there will be only one listener for method uri


class TimeoutUTransport(MockUTransport, ABC):
    def send(self, message):
        return UStatus(code=UCode.OK)


class ErrorUTransport(MockUTransport, ABC):
    def send(self, message):
        return UStatus(code=UCode.FAILED_PRECONDITION)

    def register_listener(self, source_filter: UUri, listener: UListener, sink_filter: UUri = None) -> UStatus:
        return UStatus(code=UCode.FAILED_PRECONDITION)

    def unregister_listener(self, source: UUri, listener: UListener, sink: UUri = None) -> UStatus:
        return UStatus(code=UCode.FAILED_PRECONDITION)


class CommStatusTransport(MockUTransport):
    def build_response(self, request):
        status = UStatus(code=UCode.FAILED_PRECONDITION, message="CommStatus Error")
        return (
            UMessageBuilder.response_for_request(request.attributes)
            .with_commstatus(status.code)
            .build_from_upayload(UPayload.pack(status))
        )


class EchoUTransport(MockUTransport):
    def build_response(self, request):
        return request

    def send(self, message):
        response = self.build_response(message)
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(self._notify_listeners, response)
        return UStatus(code=UCode.OK)
