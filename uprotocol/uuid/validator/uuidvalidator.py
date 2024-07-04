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
from enum import Enum

from uprotocol.uuid.factory.uuidutils import UUIDUtils, Version
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.ustatus_pb2 import UStatus
from uprotocol.v1.uuid_pb2 import UUID
from uprotocol.validation.validationresult import ValidationResult


class UuidVariant(Enum):
    VARIANT_RFC_4122 = "RFC 4122"


class UuidValidator(ABC):
    """
    UUID Validator class that validates UUIDs
    """

    @staticmethod
    def get_validator(uuid: UUID):
        if UUIDUtils.is_uuidv6(uuid):
            return Validators.UUIDV6.validator()
        elif UUIDUtils.is_uprotocol(uuid):
            return Validators.UPROTOCOL.validator()
        else:
            return Validators.UNKNOWN.validator()

    def validate(self, uuid: UUID) -> UStatus:
        error_messages = [
            self.validate_version(uuid),
            self.validate_variant(uuid),
            self.validate_time(uuid),
        ]
        error_messages = [result.get_message() for result in error_messages if result.is_failure()]
        error_message = ",".join(error_messages)
        if not error_message:
            return ValidationResult.success().to_status()
        return UStatus(code=UCode.INVALID_ARGUMENT, message=error_message)

    @abstractmethod
    def validate_version(self, uuid: UUID) -> ValidationResult:
        raise NotImplementedError

    def validate_time(self, uuid: UUID) -> ValidationResult:
        time = UUIDUtils.get_time(uuid)
        return (
            ValidationResult.success()
            if (time is not None and time > 0)
            else ValidationResult.failure("Invalid UUID Time")
        )

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
        version = UUIDUtils.get_version(uuid)
        return (
            ValidationResult.success()
            if version and version == Version.VERSION_TIME_ORDERED
            else (ValidationResult.failure("Not a UUIDv6 Version"))
        )

    def validate_variant(self, uuid: UUID) -> ValidationResult:
        variant = UUIDUtils.get_variant(uuid)
        return (
            ValidationResult.success()
            if variant and "RFC 4122" in variant
            else ValidationResult.failure("Invalid UUIDv6 variant")
        )


class UUIDv7Validator(UuidValidator):
    def validate_version(self, uuid: UUID) -> ValidationResult:
        version = UUIDUtils.get_version(uuid)
        return (
            ValidationResult.success()
            if version and version == Version.VERSION_UPROTOCOL
            else (ValidationResult.failure("Invalid UUIDv7 Version"))
        )

    def validate_variant(self, uuid: UUID) -> ValidationResult:
        return ValidationResult.success()


class Validators(Enum):
    UNKNOWN = InvalidValidator()  # Use a default validator instance
    UUIDV6 = UUIDv6Validator()  # Use a default validator instance
    UPROTOCOL = UUIDv7Validator()  # Use a default validator instance

    def validator(self):
        return self.value

    def __new__(cls, value):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj
