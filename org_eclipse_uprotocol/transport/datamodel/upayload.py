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


from typing import Optional

from org_eclipse_uprotocol.proto.upayload_pb2 import UPayloadFormat


class UPayload:
    """
    The UPayload contains the clean Payload information along with its raw serialized structure of a byte[].
    """
    EMPTY = None

    def __init__(self, data: bytes, hint: UPayloadFormat = None):
        """
        Create a UPayload.<br><br>
        @param data:A byte array of the actual data.
        @param hint:Hint regarding the bytes contained within the UPayload
        """
        self.data = data if data is not None else bytes()
        self.hint = hint if hint is not None else UPayloadFormat.UNKNOWN

    def get_data(self) -> bytes:
        """
        The actual serialized or raw data, which can be deserialized or simply used as is.<br><br>
        @return:Returns the actual serialized or raw data, which can be deserialized or simply used as is.
        """
        return self.data

    def get_hint(self) -> UPayloadFormat:
        """
        The hint regarding the bytes contained within the UPayload.
        @return:Returns the hint regarding the bytes contained within the UPayload.
        """
        return self.hint

    @classmethod
    def empty(cls):
        """

        @return: Returns an empty representation of UPayload.
        """
        if cls.EMPTY is None:
            cls.EMPTY = UPayload(bytes(), UPayloadFormat.UNKNOWN)
        return cls.EMPTY

    def is_empty(self):
        """

        @return:Returns true if the data in the UPayload is empty.
        """
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
    payload = UPayload(b"example_data", UPayloadFormat.UNKNOWN)
    print(payload)
