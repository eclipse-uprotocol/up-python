"""
SPDX-FileCopyrightText: 2023 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import unittest
from datetime import datetime, timezone

from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.uuid.factory.uuidutils import UUIDUtils
from uprotocol.uuid.serializer.uuidserializer import UuidSerializer
from uprotocol.uuid.validator.uuidvalidator import UuidValidator, Validators
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.uuid_pb2 import UUID
from uprotocol.validation.validationresult import ValidationResult


class TestUuidValidator(unittest.TestCase):
    def test_validator_with_good_uuid(self):
        uuid = Factories.UPROTOCOL.create()
        status = UuidValidator.get_validator(uuid).validate(uuid)
        self.assertEqual(ValidationResult.STATUS_SUCCESS, status)

    def test_good_uuid_string(self):
        status = Validators.UPROTOCOL.validator().validate(Factories.UPROTOCOL.create())
        self.assertEqual(status, ValidationResult.STATUS_SUCCESS)

    def test_invalid_uuid(self):
        uuid = UUID(msb=0, lsb=0)
        status = UuidValidator.get_validator(uuid).validate(uuid)
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)
        self.assertEqual(
            "Invalid UUID Version,Invalid UUID Variant,Invalid UUID Time",
            status.message,
        )

    def test_invalid_time_uuid(self):
        epoch_time = datetime.fromtimestamp(0, tz=timezone.utc)

        uuid = Factories.UPROTOCOL.create(epoch_time)
        status = Validators.UPROTOCOL.validator().validate(uuid)
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)
        self.assertEqual("Invalid UUID Time", status.message)

    def test_uuidv7_with_invalid_uuids(self):
        validator = Validators.UPROTOCOL.validator()
        self.assertIsNotNone(validator)
        status = validator.validate(None)
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)
        self.assertEqual("Invalid UUIDv7 Version,Invalid UUID Time", status.message)

    def test_uuidv7_with_invalid_types(self):
        uuidv6 = Factories.UUIDV6.create()
        uuid = UUID(msb=0, lsb=0)
        uuidv4 = UuidSerializer.deserialize("195f9bd1-526d-4c28-91b1-ff34c8e3632d")

        validator = Validators.UPROTOCOL.validator()
        self.assertIsNotNone(validator)

        status = validator.validate(uuidv6)
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)
        self.assertEqual("Invalid UUIDv7 Version", status.message)

        status1 = validator.validate(uuid)
        self.assertEqual(UCode.INVALID_ARGUMENT, status1.code)
        self.assertEqual("Invalid UUIDv7 Version,Invalid UUID Time", status1.message)

        status2 = validator.validate(uuidv4)
        self.assertEqual(UCode.INVALID_ARGUMENT, status2.code)
        self.assertEqual("Invalid UUIDv7 Version,Invalid UUID Time", status2.message)

    def test_good_uuidv6(self):
        uuid = Factories.UUIDV6.create()

        validator = UuidValidator.get_validator(uuid)
        self.assertIsNotNone(validator)
        self.assertTrue(UUIDUtils.is_uuidv6(uuid))
        self.assertEqual(UCode.OK, validator.validate(uuid).code)

    def test_uuidv6_with_invalid_uuid(self):
        uuid = UUID(msb=9 << 12, lsb=0)
        validator = Validators.UUIDV6.validator()
        self.assertIsNotNone(validator)
        status = validator.validate(uuid)
        self.assertEqual(
            "Not a UUIDv6 Version,Invalid UUIDv6 variant,Invalid UUID Time",
            status.message,
        )
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)

    def test_uuidv6_with_null_uuid(self):
        validator = Validators.UUIDV6.validator()
        self.assertIsNotNone(validator)
        status = validator.validate(None)
        self.assertEqual(
            "Not a UUIDv6 Version,Invalid UUIDv6 variant,Invalid UUID Time",
            status.message,
        )
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)

    def test_uuidv6_with_uuidv7(self):
        uuid = Factories.UPROTOCOL.create()
        validator = Validators.UUIDV6.validator()
        self.assertIsNotNone(validator)
        status = validator.validate(uuid)
        self.assertEqual("Not a UUIDv6 Version", status.message)
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)


if __name__ == "__main__":
    unittest.main()
