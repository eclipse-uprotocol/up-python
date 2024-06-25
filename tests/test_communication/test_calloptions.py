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

from uprotocol.communication.calloptions import CallOptions
from uprotocol.v1.uattributes_pb2 import (
    UPriority,
)
from uprotocol.v1.uri_pb2 import UUri


class TestCallOptions(unittest.TestCase):
    def test_build_null_call_options(self):
        """Test building a null CallOptions that is equal to the default"""
        options = CallOptions()
        self.assertEqual(options, CallOptions.DEFAULT)

    def test_build_call_options_with_timeout(self):
        """Test building a CallOptions with a timeout"""
        options = CallOptions(timeout=1000)
        self.assertEqual(1000, options.timeout)
        self.assertEqual(UPriority.UPRIORITY_CS4, options.priority)
        self.assertTrue(options.token == "")

    def test_build_call_options_with_priority(self):
        """Test building a CallOptions with a priority"""
        options = CallOptions(timeout=1000, priority=UPriority.UPRIORITY_CS4)
        self.assertEqual(UPriority.UPRIORITY_CS4, options.priority)

    def test_build_call_options_with_all_parameters(self):
        """Test building a CallOptions with all parameters"""
        options = CallOptions(timeout=1000, priority=UPriority.UPRIORITY_CS4, token="token")
        self.assertEqual(1000, options.timeout)
        self.assertEqual(UPriority.UPRIORITY_CS4, options.priority)
        self.assertEqual("token", options.token)

    def test_build_call_options_with_blank_token(self):
        """Test building a CallOptions with a blank token"""
        options = CallOptions(timeout=1000, priority=UPriority.UPRIORITY_CS4, token="")
        self.assertTrue(options.token == "")

    def test_is_equals_with_null(self):
        """Test isEquals when passed parameter is not equals"""
        options = CallOptions(timeout=1000, priority=UPriority.UPRIORITY_CS4, token="token")
        self.assertNotEqual(options, None)

    def test_is_equals_with_same_object(self):
        """Test isEquals when passed parameter is equals"""
        options = CallOptions(timeout=1000, priority=UPriority.UPRIORITY_CS4, token="token")
        self.assertEqual(options, options)

    def test_is_equals_with_different_parameters(self):
        """Test isEquals when timeout is not the same"""
        options = CallOptions(timeout=1001, priority=UPriority.UPRIORITY_CS3, token="token")
        other_options = CallOptions(timeout=1000, priority=UPriority.UPRIORITY_CS3, token="token")
        self.assertNotEqual(options, other_options)

    def test_is_equals_with_different_parameters_priority(self):
        """Test isEquals when priority is not the same"""
        options = CallOptions(timeout=1000, priority=UPriority.UPRIORITY_CS4, token="token")
        other_options = CallOptions(timeout=1000, priority=UPriority.UPRIORITY_CS3, token="token")
        self.assertNotEqual(options, other_options)

    def test_is_equals_with_different_parameters_token(self):
        """Test isEquals when token is not the same"""
        options = CallOptions(timeout=1000, priority=UPriority.UPRIORITY_CS3, token="Mytoken")
        other_options = CallOptions(timeout=1000, priority=UPriority.UPRIORITY_CS3, token="token")
        self.assertNotEqual(options, other_options)

    def test_is_equals_with_different_type(self):
        """Test equals when object passed is not the same type as CallOptions"""
        options = CallOptions(timeout=1000, priority=UPriority.UPRIORITY_CS4, token="token")
        uri = UUri()
        self.assertNotEqual(options, uri)


if __name__ == '__main__':
    unittest.main()
