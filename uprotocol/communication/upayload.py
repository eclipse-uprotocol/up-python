"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from dataclasses import dataclass, field
from typing import Optional, Type

import google.protobuf.any_pb2 as any_pb2
import google.protobuf.message as message

from uprotocol.v1.uattributes_pb2 import (
    UPayloadFormat,
)


@dataclass(frozen=True)
class UPayload:
    data: bytes = field(default_factory=bytes)
    format: UPayloadFormat = UPayloadFormat.UPAYLOAD_FORMAT_UNSPECIFIED

    # Define EMPTY as a class-level constant
    EMPTY: Optional['UPayload'] = None

    @staticmethod
    def is_empty(payload: Optional['UPayload']) -> bool:
        return payload is None or (payload.data == b'' and payload.format == UPayloadFormat.UPAYLOAD_FORMAT_UNSPECIFIED)

    @staticmethod
    def pack_to_any(message: message.Message) -> 'UPayload':
        if message is None:
            return UPayload.EMPTY
        any_message = any_pb2.Any()
        any_message.Pack(message)
        serialized_data = any_message.SerializeToString()
        return UPayload(data=serialized_data, format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY)

    @staticmethod
    def pack(message: message.Message) -> 'UPayload':
        if message is None:
            return UPayload.EMPTY
        return UPayload(message.SerializeToString(), UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF)

    @staticmethod
    def pack_from_data_and_format(data: bytes, format: UPayloadFormat) -> 'UPayload':
        return UPayload(data, format)

    @staticmethod
    def unpack(payload: Optional['UPayload'], clazz: Type[message.Message]) -> Optional[message.Message]:
        if payload is None:
            return None
        return UPayload.unpack_data_format(payload.data, payload.format, clazz)

    @staticmethod
    def unpack_data_format(
        data: bytes, format: UPayloadFormat, clazz: Type[message.Message]
    ) -> Optional[message.Message]:
        format = format if format is not None else UPayloadFormat.UPAYLOAD_FORMAT_UNSPECIFIED
        if data is None or len(data) == 0:
            return None
        try:
            if format == UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY:
                message = clazz()
                any_message = any_pb2.Any()
                any_message.ParseFromString(data)
                any_message.Unpack(message)
                return message
            elif format == UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF:
                message = clazz()
                message.ParseFromString(data)
                return message
            else:
                return None
        except Exception:
            return None


# Initialize EMPTY outside the class definition
UPayload.EMPTY = UPayload(data=bytes(), format=UPayloadFormat.UPAYLOAD_FORMAT_UNSPECIFIED)
