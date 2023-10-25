# -------------------------------------------------------------------------

# Copyright (c) 2023 General Motors GTO LLC

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# -------------------------------------------------------------------------

from enum import Enum, unique


@unique
class USerializationHint(Enum):
    # Serialization hint is unknown
    UNKNOWN = (0, "")

    # serialized com.google.protobuf.Any type
    PROTOBUF = (1, "application/x-protobuf")

    # data is a UTF-8 string containing a JSON structure
    JSON = (2, "application/json")

    # data is a UTF-8 string containing a JSON structure
    SOMEIP = (3, "application/x-someip")

    # Raw binary data that has not been serialized
    RAW = (4, "application/octet-stream")

    # Text Format
    TEXT = (5, "text/plain")

    def __init__(self, hint_number: int, mime_type: str):
        self.hint_number = hint_number
        self.mime_type = mime_type

    def get_hint_number(self):
        return self.hint_number

    def get_mime_type(self):
        return self.mime_type

    @classmethod
    def from_hint_number(cls, value: int):
        """
        Find the serialization hint matching the mimeType value. Mind you, it might not exist.<br><br>
        @param value:numeric hint value.
        @return:Returns the USerializationHint matching the numeric value.
        """
        for hint in cls:
            if hint.get_hint_number() == value:
                return hint
        return None

    @classmethod
    def from_mime_type(cls, value: str):
        """
        Find the serialization hint  matching the String value. Mind you, it might not exist.<br><br>
        @param value:String hint value.
        @return:Returns the USerializationHint matching the String value.
        """
        for hint in cls:
            if hint.get_mime_type() == value:
                return hint
        return None
