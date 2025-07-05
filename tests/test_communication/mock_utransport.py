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
from typing import List

from uprotocol.communication.upayload import UPayload
from uprotocol.core.usubscription.v3.usubscription_pb2 import (
    SubscriptionRequest,
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
        self.listeners: List[UListener] = []
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor()

    def build_response(self, request: UMessage) -> UMessage:
        if request.attributes.sink.ue_id == 0:
            if request.attributes.sink.resource_id == 1:
                try:
                    subscription_request = SubscriptionRequest.parse(request.payload)
                    sub_response = SubscriptionResponse(
                        topic=subscription_request.topic,
                        status=SubscriptionStatus(state=SubscriptionStatus.State.SUBSCRIBED),
                    )
                    return UMessageBuilder.response_for_request(request.attributes).build_from_upayload(
                        UPayload.pack(sub_response)
                    )
                except Exception:
                    return UMessageBuilder.response_for_request(request.attributes).build_from_upayload(
                        UPayload.pack(UnsubscribeResponse())
                    )
            else:
                return UMessageBuilder.response_for_request(request.attributes).build_from_upayload(
                    UPayload.pack(UnsubscribeResponse())
                )
        return UMessageBuilder.response_for_request(request.attributes).build_from_upayload(
            UPayload.pack_from_data_and_format(request.payload, request.attributes.payload_format)
        )

    async def send(self, message: UMessage) -> UStatus:
        validator = UAttributesValidator.get_validator(message.attributes)

        if message is None or validator.validate(message.attributes) != ValidationResult.success():
            return UStatus(code=UCode.INVALID_ARGUMENT, message="Invalid message attributes")

        if message.attributes.type == UMessageType.UMESSAGE_TYPE_REQUEST:
            response = self.build_response(message)
            await self._notify_listeners(response)

        return UStatus(code=UCode.OK)

    async def _notify_listeners(self, response: UMessage):
        for listener in self.listeners:
            await listener.on_receive(response)

    async def register_listener(self, source: UUri, listener: UListener, sink: UUri = None) -> UStatus:
        self.listeners.append(listener)
        return UStatus(code=UCode.OK)

    async def unregister_listener(self, source: UUri, listener: UListener, sink: UUri = None) -> UStatus:
        if listener in self.listeners:
            self.listeners.remove(listener)
            return UStatus(code=UCode.OK)
        return UStatus(code=UCode.NOT_FOUND)

    async def close(self):
        await self.listeners.clear()
        await self.executor.shutdown()


class TimeoutUTransport(MockUTransport, ABC):
    async def send(self, message):
        return UStatus(code=UCode.OK)


class ErrorUTransport(MockUTransport, ABC):
    async def send(self, message):
        return UStatus(code=UCode.FAILED_PRECONDITION)

    async def register_listener(self, source_filter: UUri, listener: UListener, sink_filter: UUri = None) -> UStatus:
        return UStatus(code=UCode.FAILED_PRECONDITION)

    async def unregister_listener(self, source: UUri, listener: UListener, sink: UUri = None) -> UStatus:
        return UStatus(code=UCode.FAILED_PRECONDITION)


class CommStatusTransport(MockUTransport):
    def build_response(self, request):
        status = UStatus(code=UCode.FAILED_PRECONDITION, message="CommStatus Error")
        return (
            UMessageBuilder.response_for_request(request.attributes)
            .with_commstatus(status.code)
            .build_from_upayload(UPayload.pack(status))
        )


class CommStatusUCodeOKTransport(MockUTransport):
    def build_response(self, request):
        status = UStatus(code=UCode.OK, message="No Communication Error")
        return (
            UMessageBuilder.response_for_request(request.attributes)
            .with_commstatus(status.code)
            .build_from_upayload(UPayload.pack(status))
        )


class EchoUTransport(MockUTransport):
    def build_response(self, request):
        return request

    async def send(self, message):
        response = self.build_response(message)

        await self._notify_listeners(response)
        return UStatus(code=UCode.OK)
