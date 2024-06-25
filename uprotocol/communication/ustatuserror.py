"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.ustatus_pb2 import UStatus


class UStatusError(Exception):
    def __init__(self, status: UStatus, cause: Optional[Exception] = None):
        message = ""
        if status is not None:
            message = status.message
        super().__init__(message, cause)
        self.status = status if status is not None else UStatus(code=UCode.UNKNOWN)
        self.cause = cause

    @classmethod
    def from_code_message(cls, code: UCode, message: str, cause: Optional[Exception] = None):
        return cls(UStatus(code=code, message=message), cause)

    def get_status(self) -> UStatus:
        return self.status

    def get_code(self) -> UCode:
        return self.status.code

    def get_message(self) -> str:
        return self.status.message

    def get_cause(self) -> Exception:
        return self.cause
