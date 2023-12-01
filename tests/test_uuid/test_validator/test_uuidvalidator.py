# -------------------------------------------------------------------------
#
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
#
# -------------------------------------------------------------------------


import unittest
from datetime import datetime, timezone

from uprotocol.uuid.factory.uuidutils import UUIDUtils
from uprotocol.uuid.serializer.longuuidserializer import LongUuidSerializer

from uprotocol.validation.validationresult import ValidationResult
from uprotocol.proto.uuid_pb2 import UUID
from uprotocol.proto.ustatus_pb2 import UCode
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.uuid.validate.uuidvalidator import UuidValidator, Validators


class TestUuidValidator(unittest.TestCase):
    def test_validator_with_good_uuid(self):
        uuid = Factories.UPROTOCOL.create()
        status = UuidValidator.get_validator(uuid).validate(uuid)
        self.assertEqual(ValidationResult.STATUS_SUCCESS, status)

    def test_good_uuid_string(self):
        status = Validators.UPROTOCOL.validator().validate(
            Factories.UPROTOCOL.create()
        )
        self.assertEqual(status, ValidationResult.STATUS_SUCCESS)
        # self.assertTrue(ValidationResult.success().__eq__(status))

    def test_invalid_uuid(self):
        uuid = UUID(msb=0, lsb=0)
        status = UuidValidator.get_validator(uuid).validate(uuid)
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)
        self.assertEqual(
            "Invalid UUID Version,Invalid UUID Variant,Invalid UUID Time",
            status.message,
        )

    def test_invalid_time_uuid(self):
        epoch_time = datetime.utcfromtimestamp(0).replace(tzinfo=timezone.utc)

        uuid = Factories.UPROTOCOL.create(
            epoch_time
        )
        status = Validators.UPROTOCOL.validator().validate(uuid)
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)
        self.assertEqual("Invalid UUID Time", status.message)

    def test_uuidv8_with_invalid_uuids(self):
        validator = Validators.UPROTOCOL.validator()
        self.assertIsNotNone(validator)
        status = validator.validate(None)
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)
        self.assertEqual("Invalid UUIDv8 Version,Invalid UUID Time", status.message)

    def test_uuidv8_with_invalid_types(self):
        uuidv6 = Factories.UUIDV6.create()
        uuid = UUID(msb=0, lsb=0)
        uuidv4 = LongUuidSerializer.instance().deserialize("195f9bd1-526d-4c28-91b1-ff34c8e3632d")

        validator = Validators.UPROTOCOL.validator()
        self.assertIsNotNone(validator)

        status = validator.validate(uuidv6)
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)
        self.assertEqual("Invalid UUIDv8 Version", status.message)

        status1 = validator.validate(uuid)
        self.assertEqual(UCode.INVALID_ARGUMENT, status1.code)
        self.assertEqual("Invalid UUIDv8 Version,Invalid UUID Time", status1.message)

        status2 = validator.validate(uuidv4)
        self.assertEqual(UCode.INVALID_ARGUMENT, status2.code)
        self.assertEqual("Invalid UUIDv8 Version,Invalid UUID Time", status2.message)

    def test_good_uuidv6(self):
        uuid = Factories.UUIDV6.create()

        validator = UuidValidator.get_validator(uuid)
        self.assertIsNotNone(validator)
        self.assertTrue(UUIDUtils.isUuidv6(uuid))
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

    def test_uuidv6_with_uuidv8(self):
        uuid = Factories.UPROTOCOL.create()
        validator = Validators.UUIDV6.validator()
        self.assertIsNotNone(validator)
        status = validator.validate(uuid)
        self.assertEqual("Not a UUIDv6 Version", status.message)
        self.assertEqual(UCode.INVALID_ARGUMENT, status.code)


if __name__ == "__main__":
    unittest.main()
