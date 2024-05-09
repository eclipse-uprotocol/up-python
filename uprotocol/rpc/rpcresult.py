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


from abc import ABC, abstractmethod
from typing import Callable, TypeVar, Union

from uprotocol.proto.ustatus_pb2 import UCode
from uprotocol.proto.ustatus_pb2 import UStatus

T = TypeVar("T")


class RpcResult(ABC):
    """
    Wrapper class for RPC Stub calls. It contains a Success with the type of the RPC call, or a failure with the
    UStatus returned by the failed call.
    """

    @abstractmethod
    def isSuccess(self) -> bool:
        pass

    @abstractmethod
    def isFailure(self) -> bool:
        pass

    @abstractmethod
    def getOrElse(self, default_value: Callable[[], T]) -> T:
        pass

    @abstractmethod
    def map(self, f: Callable[[T], T]) -> "RpcResult":
        pass

    @abstractmethod
    def flatMap(self, f: Callable[[T], "RpcResult"]) -> "RpcResult":
        pass

    @abstractmethod
    def filter(self, f: Callable[[T], bool]) -> "RpcResult":
        pass

    @abstractmethod
    def failureValue(self) -> UStatus:
        pass

    @abstractmethod
    def successValue(self) -> T:
        pass

    @staticmethod
    def success(value: T) -> "RpcResult":
        return Success(value)

    @staticmethod
    def failure(
        value: Union[
            UStatus,
            "Failure",
            Exception,
        ] = None,
        code: UCode = UCode.UNKNOWN,
        message: str = "",
    ) -> "RpcResult":
        return Failure(value, code, message)

    @staticmethod
    def flatten(result: "RpcResult") -> "RpcResult":
        return result.flatMap(lambda x: x)


class Success(RpcResult):

    def __init__(self, value: T):
        self.value = value

    def isSuccess(self) -> bool:
        return True

    def isFailure(self) -> bool:
        return False

    def getOrElse(self, default_value: Callable[[], T]) -> T:
        return self.successValue()

    def map(self, f: Callable[[T], T]) -> RpcResult:
        try:

            return self.success(f(self.successValue()))
        except Exception as e:
            return self.failure(e)

    def flatMap(self, f: Callable[[T], RpcResult]) -> RpcResult:
        try:
            return f(self.successValue())
        except Exception as e:
            return self.failure(e)

    def filter(self, f: Callable[[T], bool]) -> RpcResult:
        try:
            return (
                self
                if f(self.successValue())
                else self.failure(
                    code=UCode.FAILED_PRECONDITION, message="filtered out"
                )
            )
        except Exception as e:
            return self.failure(e)

    def failureValue(self) -> UStatus:
        raise ValueError("Method failureValue() called on a Success instance")

    def successValue(self) -> T:
        return self.value

    def __str__(self) -> str:
        return f"Success({self.successValue()})"


class Failure(RpcResult):

    def __init__(
        self,
        value: Union[UStatus, "Failure", Exception, None] = None,
        code: UCode = UCode.UNKNOWN,
        message: str = "",
    ):
        if isinstance(value, UStatus):
            self.value = value
        elif isinstance(value, Exception):
            self.value = UStatus(code=code, message=str(value))
        elif isinstance(value, Failure):
            self.value = value.failureValue()
        else:
            self.value = UStatus(code=code, message=message)

    def isSuccess(self) -> bool:
        return False

    def isFailure(self) -> bool:
        return True

    def getOrElse(self, default_value: Callable[[], T]) -> T:
        if callable(default_value):
            return default_value()
        return default_value

    def map(self, f: Callable[[T], T]) -> RpcResult:
        return self.failure(self)

    def flatMap(self, f: Callable[[T], RpcResult]) -> RpcResult:
        return self.failure(self.failureValue())

    def filter(self, f: Callable[[T], bool]) -> RpcResult:
        return self.failure(self)

    def failureValue(self) -> UStatus:
        return self.value

    def successValue(self) -> T:
        raise ValueError("Method successValue() called on a Failure instance")

    def __str__(self) -> str:
        return f"Failure({self.value})"
