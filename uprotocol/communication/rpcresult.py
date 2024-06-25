"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from abc import ABC, abstractmethod
from typing import Callable, TypeVar, Union

from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.ustatus_pb2 import UStatus

T = TypeVar("T")


class RpcResult(ABC):
    """
    Wrapper class for RPC Stub calls. It contains a Success with the type of the RPC call, or a failure with the
    UStatus returned by the failed call.
    """

    @abstractmethod
    def is_success(self) -> bool:
        pass

    @abstractmethod
    def is_failure(self) -> bool:
        pass

    @abstractmethod
    def get_or_else(self, default_value: Callable[[], T]) -> T:
        pass

    @abstractmethod
    def map(self, f: Callable[[T], T]) -> "RpcResult":
        pass

    @abstractmethod
    def flat_map(self, f: Callable[[T], "RpcResult"]) -> "RpcResult":
        pass

    @abstractmethod
    def filter(self, f: Callable[[T], bool]) -> "RpcResult":
        pass

    @abstractmethod
    def failure_value(self) -> UStatus:
        pass

    @abstractmethod
    def success_value(self) -> T:
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
        return result.flat_map(lambda x: x)


class Success(RpcResult):
    def __init__(self, value: T):
        self.value = value

    def is_success(self) -> bool:
        return True

    def is_failure(self) -> bool:
        return False

    def get_or_else(self, default_value: Callable[[], T]) -> T:
        return self.success_value()

    def map(self, f: Callable[[T], T]) -> RpcResult:
        try:
            return self.success(f(self.success_value()))
        except Exception as e:
            return self.failure(e)

    def flat_map(self, f: Callable[[T], RpcResult]) -> RpcResult:
        try:
            return f(self.success_value())
        except Exception as e:
            return self.failure(e)

    def filter(self, f: Callable[[T], bool]) -> RpcResult:
        try:
            return (
                self
                if f(self.success_value())
                else self.failure(code=UCode.FAILED_PRECONDITION, message="filtered out")
            )
        except Exception as e:
            return self.failure(e)

    def failure_value(self) -> UStatus:
        raise ValueError("Method failure_value() called on a Success instance")

    def success_value(self) -> T:
        return self.value

    def __str__(self) -> str:
        return f"Success({self.success_value()})"


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
            self.value = value.failure_value()
        else:
            self.value = UStatus(code=code, message=message)

    def is_success(self) -> bool:
        return False

    def is_failure(self) -> bool:
        return True

    def get_or_else(self, default_value: Callable[[], T]) -> T:
        if callable(default_value):
            return default_value()
        return default_value

    def map(self, f: Callable[[T], T]) -> RpcResult:
        return self.failure(self)

    def flat_map(self, f: Callable[[T], RpcResult]) -> RpcResult:
        return self.failure(self.failure_value())

    def filter(self, f: Callable[[T], bool]) -> RpcResult:
        return self.failure(self)

    def failure_value(self) -> UStatus:
        return self.value

    def success_value(self) -> T:
        raise ValueError("Method success_value() called on a Failure instance")

    def __str__(self) -> str:
        return f"Failure({self.value})"
