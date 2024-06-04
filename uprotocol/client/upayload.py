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

from typing import Optional, Type

from uprotocol.proto.uprotocol.v1.uattributes_pb2 import UPayloadFormat
from google.protobuf.any_pb2 import Any
from google.protobuf.message import Message


class UPayload:

    def __init__(self, format: UPayloadFormat, data: bytes):
        self.format = (
            format if format else UPayloadFormat.UPAYLOAD_FORMAT_UNSPECIFIED
        )
        self.data = data

    def get_data(self) -> bytes:
        return self.data

    def get_format(self) -> UPayloadFormat:
        return self.format

    @staticmethod
    def pack_to_any(message):
        """
        Build a uPayload from google.protobuf.Message by stuffing the message into an Any.
        @param message the message to pack
        @return the UPayload
        """
        any_message = Any()
        any_message.Pack(message)
        return UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
            data=any_message.SerializeToString(),
        )

    @staticmethod
    def pack(message):
        """
        Build a uPayload from google.protobuf.Message using protobuf PayloadFormat.
        @param message the message to pack
        @return the UPayload
        """
        return UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF,
            data=message.SerializeToString(),
        )

    @staticmethod
    def unpack(payload, clazz: Type[Message]) -> Optional[Message]:
        """
        Unpack a uPayload into a google.protobuf.Message.
        @param payload the payload to unpack
        @param clazz the class of the message to unpack
        @return the unpacked message
        """
        if payload is None or payload.data is None:
            return None
        try:
            if payload.format == UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF:
                message = clazz()
                message.ParseFromString(payload.data)
                return message
            elif (
                payload.format
                == UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY
            ):
                any_message = Any()
                any_message.ParseFromString(payload.data)
                message = clazz()
                any_message.Unpack(message)
                return message
            else:
                return None
        except Exception:
            return None
