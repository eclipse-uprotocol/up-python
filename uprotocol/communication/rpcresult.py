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
from typing import TypeVar

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
        value: UStatus = None,
        code: UCode = UCode.UNKNOWN,
        message: str = "",
    ) -> "RpcResult":
        return Failure(value, code, message)


class Success(RpcResult):
    def __init__(self, value: T):
        self.value = value

    def is_success(self) -> bool:
        return True

    def is_failure(self) -> bool:
        return False

    def failure_value(self) -> UStatus:
        raise ValueError("Method failure_value() called on a Success instance")

    def success_value(self) -> T:
        return self.value

    def __str__(self) -> str:
        return f"Success({self.success_value()})"


class Failure(RpcResult):
    def __init__(
        self,
        value: UStatus = None,
        code: UCode = UCode.UNKNOWN,
        message: str = "",
    ):
        if isinstance(value, UStatus):
            self.value = value
        else:
            self.value = UStatus(code=code, message=message)

    def is_success(self) -> bool:
        return False

    def is_failure(self) -> bool:
        return True

    def failure_value(self) -> UStatus:
        return self.value

    def success_value(self) -> T:
        raise ValueError("Method success_value() called on a Failure instance")

    def __str__(self) -> str:
        return f"Failure({self.value})"
