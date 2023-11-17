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


from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

import google.rpc.code_pb2


class Code(Enum):
    """
     Enum to contain the status code that we map to google.rpc.Code.<br>Please refer to <a
     href="https://github.com/googleapis/googleapis/blob/master/google/rpc/code.proto">code.proto</a>for
     documentation on the codes listed below
    """
    OK = google.rpc.code_pb2.OK
    CANCELLED = google.rpc.code_pb2.CANCELLED
    UNKNOWN = google.rpc.code_pb2.UNKNOWN
    INVALID_ARGUMENT = google.rpc.code_pb2.INVALID_ARGUMENT
    DEADLINE_EXCEEDED = google.rpc.code_pb2.DEADLINE_EXCEEDED
    NOT_FOUND = google.rpc.code_pb2.NOT_FOUND
    ALREADY_EXISTS = google.rpc.code_pb2.ALREADY_EXISTS
    PERMISSION_DENIED = google.rpc.code_pb2.PERMISSION_DENIED
    UNAUTHENTICATED = google.rpc.code_pb2.UNAUTHENTICATED
    RESOURCE_EXHAUSTED = google.rpc.code_pb2.RESOURCE_EXHAUSTED
    FAILED_PRECONDITION = google.rpc.code_pb2.FAILED_PRECONDITION
    ABORTED = google.rpc.code_pb2.ABORTED
    OUT_OF_RANGE = google.rpc.code_pb2.OUT_OF_RANGE
    UNIMPLEMENTED = google.rpc.code_pb2.UNIMPLEMENTED
    INTERNAL = google.rpc.code_pb2.INTERNAL
    UNAVAILABLE = google.rpc.code_pb2.UNAVAILABLE
    DATA_LOSS = google.rpc.code_pb2.DATA_LOSS
    UNSPECIFIED = -1

    def __init__(self, value):
        self._value_ = value

    def value(self):
        return self._value_
    @staticmethod
    def from_int( value: int):
        for enum_value in Code:
            if enum_value.value == value:
                return enum_value
        return None


class UStatus(ABC):
    """
    UProtocol general status for all operations.<br> A UStatus is generated using the static factory methods,
    making is easy to quickly create UStatus objects.<br> Example: UStatus ok = UStatus.ok();
    """
    OK = "ok"
    FAILED = "failed"

    @abstractmethod
    def isSuccess(self) -> bool:
        pass

    @abstractmethod
    def msg(self) -> str:
        pass

    @abstractmethod
    def getCode(self) -> int:
        pass

    def isFailed(self) -> bool:
        """
        Return true if UStatus is a failure.<br><br>
        @return:Returns true if the UStatus is failed.
        """
        return not self.isSuccess()

    def __str__(self) -> str:
        return f"UStatus {'ok' if self.isSuccess() else 'failed'} " \
               f"{'id=' if self.isSuccess() else 'msg='}{self.msg()} code={self.getCode()}"

    @staticmethod
    def ok():
        return OKStatus(UStatus.OK)

    @staticmethod
    def ok_with_ack_id(ack_id: str):
        return OKStatus(ack_id)

    @staticmethod
    def failed():
        return FailStatus(UStatus.FAILED, Code.UNKNOWN)

    @staticmethod
    def failed_with_msg(msg: str):
        return FailStatus(msg, Code.UNKNOWN)

    @staticmethod
    def failed_with_msg_and_code(msg: str, code: Code):
        return FailStatus(msg, code)

    @staticmethod
    def from_int(value: int) -> Optional[Code]:
        for item in Code:
            if item.value == value:
                return item
        return None

    @staticmethod
    def from_google_rpc_code(code: int) -> Optional[Code]:
        if code == -1:  # UNRECOGNIZED
            return None
        for item in Code:
            if item.value == code:
                return item
        return None


class OKStatus(UStatus):
    """
    A successful UStatus.
    """

    def __init__(self, ack_id: str):
        """
         A successful status could contain an id for tracking purposes.
        @param ack_id:
        """
        self.ack_id = ack_id

    def isSuccess(self) -> bool:
        return True

    def msg(self) -> str:
        return self.ack_id

    def getCode(self) -> int:
        return Code.OK.value


class FailStatus(UStatus):
    """
    A failed UStatus.
    """

    def __init__(self, fail_msg: str, code: Code):
        self.fail_msg = fail_msg
        self.code = code

    def isSuccess(self) -> bool:
        return False

    def msg(self) -> str:
        return self.fail_msg

    def getCode(self) -> int:
        return self.code.value
