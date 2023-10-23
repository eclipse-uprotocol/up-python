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

from typing import Optional

from org_eclipse_uprotocol.transport.datamodel.userializationhint import USerializationHint


class UPayload:
    EMPTY = None

    def __init__(self, data: bytes, hint: Optional[USerializationHint] = None):
        self.data = data if data is not None else bytes()
        self.hint = hint if hint is not None else USerializationHint.UNKNOWN

    def get_data(self) -> bytes:
        return self.data

    def get_hint(self) -> USerializationHint:
        return self.hint

    @classmethod
    def empty(cls):
        if cls.EMPTY is None:
            cls.EMPTY = UPayload(bytes(), USerializationHint.UNKNOWN)
        return cls.EMPTY

    def is_empty(self):
        return len(self.data) == 0

    def __eq__(self, other):
        if self is other:
            return True
        if other is None or self.__class__ != other.__class__:
            return False
        return self.data == other.data and self.hint == other.hint

    def __hash__(self):
        return hash((hash(self.data), self.hint))

    def __str__(self):
        return f"UPayload{{data={list(self.data)}, hint={self.hint}}}"


# Example usage
if __name__ == "__main__":
    payload = UPayload(b"example_data", USerializationHint.UNKNOWN)
    print(payload)
