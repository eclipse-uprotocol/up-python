# -------------------------------------------------------------------------

# Copyright (c) 2023 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: 2023 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0

# -------------------------------------------------------------------------

import typing

from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from google.protobuf.any_pb2 import Any
from google.protobuf import message

class UPayloadBuilder:
    
    def pack_to_any(message: message) -> UPayload:
        '''
        Build a uPayload from google.protobuf.Message by stuffing the message into an Any. 
        @param message the message to pack
        @return the UPayload 
        '''
        any_message = Any()
        any_message.Pack(message)
        return UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
                           value=any_message.SerializeToString())
    
    def pack(message: message) -> UPayload:
        '''
        Build a uPayload from google.protobuf.Message using protobuf PayloadFormat.
        @param message the message to pack
        @return the UPayload
        '''
        return UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF,
                           value=message.SerializeToString())

    def unpack(payload: UPayload, clazz: typing.Type) -> typing.Type:
        '''
        Unpack a uPayload into a google.protobuf.Message.
        @param payload the payload to unpack
        @param clazz the class of the message to unpack
        @return the unpacked message
        '''
        if payload is None or payload.value is None:
            return None
        try:
            if payload.format == UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF:
                message = clazz()
                message.ParseFromString(payload.value)
                return message
            elif payload.format == UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY:
                any_message = Any()
                any_message.ParseFromString(payload.value)
                message = clazz()
                any_message.Unpack(message)
                return message
            else:
                return None
        except:
            return None