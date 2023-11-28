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


import unittest

from org_eclipse_uprotocol.validation.validationresult import ValidationResult
from org_eclipse_uprotocol.proto.ustatus_pb2 import UStatus, UCode


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
