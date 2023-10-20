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

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional


class Code(Enum):
    OK = 0
    CANCELLED = 1
    UNKNOWN = 2
    INVALID_ARGUMENT = 3
    DEADLINE_EXCEEDED = 4
    NOT_FOUND = 5
    ALREADY_EXISTS = 6
    PERMISSION_DENIED = 7
    UNAUTHENTICATED = 16
    RESOURCE_EXHAUSTED = 8
    FAILED_PRECONDITION = 9
    ABORTED = 10
    OUT_OF_RANGE = 11
    UNIMPLEMENTED = 12
    INTERNAL = 13
    UNAVAILABLE = 14
    DATA_LOSS = 15
    UNSPECIFIED = -1


class UStatus(ABC):
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

    def __init__(self, ack_id: str):
        self.ack_id = ack_id

    def isSuccess(self) -> bool:
        return True

    def msg(self) -> str:
        return self.ack_id

    def getCode(self) -> int:
        return Code.OK.value


class FailStatus(UStatus):

    def __init__(self, fail_msg: str, code: Code):
        self.fail_msg = fail_msg
        self.code = code

    def isSuccess(self) -> bool:
        return False

    def msg(self) -> str:
        return self.fail_msg

    def getCode(self) -> int:
        return self.code.value
