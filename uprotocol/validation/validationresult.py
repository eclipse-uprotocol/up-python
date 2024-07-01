"""
SPDX-FileCopyrightText: 2023 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from abc import ABC, abstractmethod

from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.ustatus_pb2 import UStatus


class ValidationResult(ABC):
    """
    Class wrapping a ValidationResult of success or failure wrapping the value
    of a UStatus.
    """

    STATUS_SUCCESS = UStatus(code=UCode.OK, message="OK")

    def __init__(self):
        pass

    @abstractmethod
    def to_status(self) -> UStatus:
        pass

    @abstractmethod
    def is_success(self) -> bool:
        pass

    def is_failure(self) -> bool:
        return not self.is_success()

    @abstractmethod
    def get_message(self) -> str:
        pass

    @staticmethod
    def success():
        return Success()

    @staticmethod
    def failure(message):
        return Failure(message)


class Failure(ValidationResult):
    """
    Implementation for failure, wrapping the message.
    """

    def __init__(self, message):
        super().__init__()
        self.message = message if message else "Validation Failed."

    def to_status(self) -> UStatus:
        return UStatus(code=3, message=self.message)

    def is_success(self) -> bool:
        return False

    def get_message(self) -> str:
        return self.message

    def __str__(self):
        return f"ValidationResult.Failure(message='{self.message}')"


class Success(ValidationResult):
    """
    Implementation for success, wrapping a UStatus with UCode 0 for success.
    """

    def to_status(self) -> UStatus:
        return ValidationResult.STATUS_SUCCESS

    def is_success(self) -> bool:
        return True

    def get_message(self) -> str:
        return ""

    def __str__(self):
        return "ValidationResult.Success()"

    def __eq__(self, other):
        if isinstance(other, Success):
            return self.to_status() == other.to_status()
        return False
