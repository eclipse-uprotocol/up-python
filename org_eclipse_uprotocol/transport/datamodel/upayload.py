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
import sys

from google.protobuf import any_pb2


class USerializationHint:
    def __init__(self, hint_value):
        self.hint_value = hint_value


class UPayload:
    EMPTY = None

    def __init__(self, data: bytes, size: int, hint: USerializationHint):
        self.data = data
        self.size = size
        self.hint = hint

    @classmethod
    def empty(cls):
        if cls.EMPTY is None:
            cls.EMPTY = cls(bytearray(), 0, None)
        return cls.EMPTY

    @classmethod
    def from_string(cls, payload: str, hint: USerializationHint):
        return cls(bytearray(payload.encode()), hint)

    def get_data(self) -> bytes:
        return self.data if self.data is not None else UPayload.empty().data

    def hint(self):
        return self.hint

    def is_empty(self):
        return self.data is None or len(self.data) == 0

    def get_size(self) -> int:
        return self.size

    @staticmethod
    def get_any_from_payload_data(data: bytes):
        any_message = any_pb2.Any()
        any_message.ParseFromString(data)
        return any_message

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, UPayload):
            return False
        return self.data == other.data and self.hint == other.hint and self.size == other.size

    def __hash__(self):
        return hash((sys.hash_info.width, tuple(self.data), self.hint, self.size))

    def __str__(self):
        return f"UPayload{{data={list(self.data)}, size={self.size}, hint={self.hint}}}"
