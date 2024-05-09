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

from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from google.protobuf.any_pb2 import Any
from google.protobuf.message import Message


class UPayloadBuilder:

    @staticmethod
    def pack_to_any(message: Message) -> UPayload:
        """
        Build a uPayload from google.protobuf.Message by stuffing the message into an Any.
        @param message the message to pack
        @return the UPayload
        """
        any_message = Any()
        any_message.Pack(message)
        return UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
            value=any_message.SerializeToString(),
        )

    @staticmethod
    def pack(message: Message) -> UPayload:
        """
        Build a uPayload from google.protobuf.Message using protobuf PayloadFormat.
        @param message the message to pack
        @return the UPayload
        """
        return UPayload(
            format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF,
            value=message.SerializeToString(),
        )

    @staticmethod
    def unpack(payload: UPayload, clazz: Type[Message]) -> Optional[Message]:
        """
        Unpack a uPayload into a google.protobuf.Message.
        @param payload the payload to unpack
        @param clazz the class of the message to unpack
        @return the unpacked message
        """
        if payload is None or payload.value is None:
            return None
        try:
            if payload.format == UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF:
                message = clazz()
                message.ParseFromString(payload.value)
                return message
            elif (
                payload.format
                == UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY
            ):
                any_message = Any()
                any_message.ParseFromString(payload.value)
                message = clazz()
                any_message.Unpack(message)
                return message
            else:
                return None
        except Exception:
            return None
