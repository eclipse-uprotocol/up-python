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


import base64
from builtins import str

from uprotocol.cloudevent.serialize.cloudeventserializer import CloudEventSerializer


class Base64ProtobufSerializer(CloudEventSerializer):
    """
    Helper for serializing Base64 protobuf data.
    """

    def deserialize(self, proto_bytes: bytes) -> str:
        """
        Deserialize a base64 protobuf payload into a Base64 String.<br><br>

        @param proto_bytes: byte[] data
        @return: Returns a String from the base64 protobuf payload.
        """
        if proto_bytes is None:
            return ""
        return base64.b64encode(proto_bytes).decode('utf-8')  # return base64.b64decode(proto_bytes).decode('utf-8')

    def serialize(self, string_to_serialize: str) -> bytes:
        """
        Serialize a String into Base64 format.<br><br>
        @param string_to_serialize:String to serialize.
        @return: Returns the Base64 formatted String as a byte[].
        """
        if string_to_serialize is None:
            return bytearray()
        return base64.b64decode(string_to_serialize.encode('utf-8'))
