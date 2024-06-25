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

from uprotocol.communication.upayload import UPayload
from uprotocol.core.usubscription.v3.usubscription_pb2 import (
    SubscriptionResponse,
    SubscriptionStatus,
    UnsubscribeResponse,
)
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.transport.validator.uattributesvalidator import UAttributesValidator
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
        self.listeners = []
        self.lock = threading.Lock()

    def build_response(self, request: UMessage):
        sink = request.attributes.sink
        response_map = {
            (0, 3, 1): SubscriptionResponse(
                status=SubscriptionStatus(state=SubscriptionStatus.State.SUBSCRIBED, message="Successfully Subscribed")
            ),
            (0, 3, 2): UnsubscribeResponse(),
        }

        response_payload = response_map.get((sink.ue_id, sink.ue_version_major, sink.resource_id))
        if response_payload is None:
            payload = UPayload.pack_from_data_and_format(request.payload, request.attributes.payload_format)
        else:
            payload = UPayload.pack(response_payload)

        return UMessageBuilder.response_for_request(request.attributes).build_from_upayload(payload)

    def close(self):
        self.listeners.clear()

    def register_listener(self, source_filter: UUri, listener: UListener, sink_filter: UUri = None) -> UStatus:
        with self.lock:
            self.listeners.append(listener)
            return UStatus(code=UCode.OK)

    def unregister_listener(self, source: UUri, listener: UListener, sink: UUri = None) -> UStatus:
        with self.lock:
            if listener in self.listeners:
                self.listeners.remove(listener)
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

            if message.attributes.type == UMessageType.UMESSAGE_TYPE_REQUEST:
                response = self.build_response(message)
                threading.Thread(target=self._notify_listeners, args=(response,)).start()

        return UStatus(code=UCode.OK)

    def _notify_listeners(self, response):
        for i in self.listeners:
            i.on_receive(response)


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


class CommStatusTransport(MockUTransport, ABC):
    def build_response(self, request):
        status = UStatus(code=UCode.FAILED_PRECONDITION, message="CommStatus Error")
        return UMessageBuilder.response_for_request(request.attributes).with_commstatus(status.code).build()


class EchoUTransport(MockUTransport):
    def build_response(self, request):
        return request

    def send(self, message):
        response = self.build_response(message)
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(self._notify_listeners, response)
        return UStatus(code=UCode.OK)
