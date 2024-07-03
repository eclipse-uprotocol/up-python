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

from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.ustatus_pb2 import UStatus


class TestUStatusError(unittest.IsolatedAsyncioTestCase):
    def test_ustatus_exception_constructor(self):
        """Test UStatusError constructor"""
        exception = UStatusError.from_code_message(UCode.INVALID_ARGUMENT, "Invalid message type")

        self.assertEqual(UCode.INVALID_ARGUMENT, exception.get_code())
        self.assertEqual("Invalid message type", exception.get_message())

    def test_ustatus_exception_constructor_null(self):
        """Test UStatusError constructor passing null"""
        exception = UStatusError(None, None)

        self.assertEqual(UCode.UNKNOWN, exception.get_code())
        self.assertEqual("", exception.get_message())

    def test_ustatus_exception_constructor_ustatus(self):
        """Test UStatusError constructor passing a UStatus"""
        status = UStatus(code=UCode.INVALID_ARGUMENT, message="Invalid message type")
        exception = UStatusError(status)

        self.assertEqual(UCode.INVALID_ARGUMENT, exception.get_code())
        self.assertEqual("Invalid message type", exception.get_message())

    def test_get_status(self):
        """Test UStatusError getStatus"""
        status = UStatus(code=UCode.INVALID_ARGUMENT, message="Invalid message type")
        exception = UStatusError(status)

        self.assertEqual(status, exception.get_status())

    def test_ustatus_exception_throwable(self):
        """Test UStatusError padding a throwable cause"""
        cause = Exception("This is a cause")
        exception = UStatusError(UStatus(code=UCode.INVALID_ARGUMENT, message="Invalid message type"), cause)

        self.assertEqual(UCode.INVALID_ARGUMENT, exception.get_code())
        self.assertEqual("Invalid message type", exception.get_message())
        self.assertEqual(cause, exception.get_cause())


if __name__ == '__main__':
    unittest.main()
