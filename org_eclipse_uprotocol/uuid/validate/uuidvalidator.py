# -------------------------------------------------------------------------
from abc import ABC, abstractmethod
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


from collections import namedtuple
from enum import Enum

from org_eclipse_uprotocol.proto.uuid_pb2 import UUID
from org_eclipse_uprotocol.uuid.factory.uuidutils import UUIDUtils, Version
from org_eclipse_uprotocol.validation.validationresult import ValidationResult


class UuidVariant(Enum):
    VARIANT_RFC_4122 = "RFC 4122"


class UuidValidator(ABC):
    """
    UUID Validator class that validates UUIDs
    """

    @staticmethod
    def get_validator(uuid: UUID):
        if UUIDUtils.isUuidv6(uuid):
            return Validators.UUIDV6.validator()
        elif UUIDUtils.isUProtocol(uuid):
            return Validators.UPROTOCOL.validator()
        else:
            return Validators.UNKNOWN.validator()

    def validate(self, uuid: UUID) -> ValidationResult:
        error_messages = [self.validate_version(uuid), self.validate_variant(uuid), self.validate_time(uuid)]
        error_messages = [result.message for result in error_messages if result.is_failure]
        error_message = ", ".join(error_messages)
        if not error_message:
            return ValidationResult.success()
        return ValidationResult.failure(f"Invalid argument value: {error_message}")

    @abstractmethod
    def validate_version(self, uuid: UUID) -> ValidationResult:
        raise NotImplementedError

    def validate_time(self, uuid: UUID) -> ValidationResult:
        time = UUIDUtils.getTime(uuid)
        return ValidationResult.success() if time > 0 else ValidationResult.failure("Invalid UUID Time")

    @abstractmethod
    def validate_variant(self, uuid: UUID) -> ValidationResult:
        raise NotImplementedError


class InvalidValidator(UuidValidator):
    def validate_version(self, uuid: UUID) -> ValidationResult:
        return ValidationResult.failure("Invalid UUID Version")

    def validate_variant(self, uuid: UUID) -> ValidationResult:
        return ValidationResult.failure("Invalid UUID Variant")


class UUIDv6Validator(UuidValidator):
    def validate_version(self, uuid: UUID) -> ValidationResult:
        version = UUIDUtils.getVersion(uuid)
        return ValidationResult.success() if version and version == Version.VERSION_TIME_ORDERED else (
            ValidationResult.failure(
                "Not a UUIDv6 Version"))

    def validate_variant(self, uuid: UUID) -> ValidationResult:
        variant = UUIDUtils.getVariant(uuid)
        return ValidationResult.success() if variant and "RFC 4122" in variant else ValidationResult.failure(
            "Invalid UUIDv6 variant")


class UUIDv8Validator(UuidValidator):
    def validate_version(self, uuid: UUID) -> ValidationResult:
        version = UUIDUtils.getVersion(uuid)
        return ValidationResult.success() if version and version == Version.VERSION_UPROTOCOL else (
            ValidationResult.failure(
                "Invalid UUIDv8 Version"))

    def validate_variant(self, uuid: UUID) -> ValidationResult:
        return ValidationResult.success()


class Validators(Enum):
    UNKNOWN = InvalidValidator()  # Use a default validator instance
    UUIDV6 = UUIDv6Validator()  # Use a default validator instance
    UPROTOCOL = UUIDv8Validator()  # Use a default validator instance

    def validator(self):
        return self.value

    def __new__(cls, value):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj
