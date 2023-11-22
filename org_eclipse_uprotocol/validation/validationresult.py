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

from org_eclipse_uprotocol.proto.ustatus_pb2 import UCode, UStatus



class ValidationResult(ABC):
    """
    Class wrapping a ValidationResult of success or failure wrapping the value of a UStatus.
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
