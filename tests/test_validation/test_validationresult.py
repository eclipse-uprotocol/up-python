"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import unittest

from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.ustatus_pb2 import UStatus
from uprotocol.validation.validationresult import ValidationResult


class TestValidationResultTest(unittest.TestCase):
    def test_success_validation_result_to_string(self):
        success = ValidationResult.success()
        self.assertEqual("ValidationResult.Success()", str(success))

    def test_failure_validation_result_to_string(self):
        failure = ValidationResult.failure("boom")
        self.assertEqual("ValidationResult.Failure(message='boom')", str(failure))

    def test_success_validation_result_is_success(self):
        success = ValidationResult.success()
        self.assertTrue(success.is_success())

    def test_failure_validation_result_is_success(self):
        failure = ValidationResult.failure("boom")
        self.assertFalse(failure.is_success())

    def test_success_validation_result_get_message(self):
        success = ValidationResult.success()
        self.assertTrue(success.get_message() == '')

    def test_failure_validation_result_get_message(self):
        failure = ValidationResult.failure("boom")
        self.assertEqual("boom", failure.get_message())

    def test_success_validation_result_to_status(self):
        success = ValidationResult.success()
        self.assertEqual(ValidationResult.STATUS_SUCCESS, success.to_status())

    def test_failure_validation_result_to_status(self):
        failure = ValidationResult.failure("boom")
        status = UStatus(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertEqual(status, failure.to_status())
