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

from uprotocol.communication.rpcresult import RpcResult
from uprotocol.v1.ucode_pb2 import UCode


class TestRpcResult(unittest.TestCase):
    def fun_that_throws_exception_for_flat_map(self, x):
        raise ValueError(f"{x} went boom")

    def test_is_success_on_success(self):
        result = RpcResult.success(2)
        self.assertTrue(result.is_success())

    def test_is_success_on_failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertFalse(result.is_success())

    def test_is_failure_on_success(self):
        result = RpcResult.success(2)
        self.assertFalse(result.is_failure())

    def test_is_failure_on_failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertTrue(result.is_failure())

    def test_get_or_else_on_success(self):
        result = RpcResult.success(2)
        self.assertEqual(result.get_or_else(lambda: self.get_default()), 2)

    def test_get_or_else_on_failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertEqual(result.get_or_else(lambda: self.get_default()), self.get_default())

    def test_success_value_on_success(self):
        result = RpcResult.success(2)
        self.assertEqual(result.success_value(), 2)

    def test_success_value_on_failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        with self.assertRaises(Exception):
            result.success_value()

    def test_failure_value_on_success(self):
        result = RpcResult.success(2)
        with self.assertRaises(Exception):
            result.failure_value()

    def test_failure_value_on_failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertEqual(result.failure_value().code, UCode.INVALID_ARGUMENT)
        self.assertEqual(result.failure_value().message, "boom")

    def test_map_on_success(self):
        result = RpcResult.success(2)
        mapped = result.map(lambda x: x * 2)
        self.assertTrue(mapped.is_success())
        self.assertEqual(mapped.success_value(), 4)

    def test_map_success_when_function_throws_exception(self):
        result = RpcResult.success(2)
        mapped = result.map(self.fun_that_throws_an_exception_for_map)
        self.assertTrue(mapped.is_failure())
        self.assertEqual(mapped.failure_value().code, UCode.UNKNOWN)
        self.assertEqual(mapped.failure_value().message, "2 went boom")

    def fun_that_throws_an_exception_for_map(self, x):
        raise Exception(f"{x} went boom")

    def test_map_on_failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        mapped = result.map(lambda x: x * 2)
        self.assertTrue(mapped.is_failure())
        self.assertEqual(mapped.failure_value().code, UCode.INVALID_ARGUMENT)
        self.assertEqual(mapped.failure_value().message, "boom")

    def test_flat_map_on_success(self):
        result = RpcResult.success(2)
        flat_mapped = result.flat_map(lambda x: RpcResult.success(x * 2))
        self.assertTrue(flat_mapped.is_success())
        self.assertEqual(flat_mapped.success_value(), 4)

    def test_flat_map_on_failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        flat_mapped = result.flat_map(lambda x: RpcResult.success(x * 2))
        self.assertTrue(flat_mapped.is_failure())
        self.assertEqual(flat_mapped.failure_value().code, UCode.INVALID_ARGUMENT)
        self.assertEqual(flat_mapped.failure_value().message, "boom")

    def test_filter_on_success_that_fails(self):
        result = RpcResult.success(2)
        filter_result = result.filter(lambda i: i > 5)
        self.assertTrue(filter_result.is_failure())
        self.assertEqual(filter_result.failure_value().code, UCode.FAILED_PRECONDITION)
        self.assertEqual(filter_result.failure_value().message, "filtered out")

    def test_filter_on_success_that_succeeds(self):
        result = RpcResult.success(2)
        filter_result = result.filter(lambda i: i < 5)
        self.assertTrue(filter_result.is_success())
        self.assertEqual(filter_result.success_value(), 2)

    def test_filter_on_success_when_function_throws_exception(self):
        result = RpcResult.success(2)
        filter_result = result.filter(self.predicate_that_throws_an_exception)
        self.assertTrue(filter_result.is_failure())
        self.assertEqual(filter_result.failure_value().code, UCode.UNKNOWN)
        self.assertEqual(filter_result.failure_value().message, "2 went boom")

    def predicate_that_throws_an_exception(self, x):
        raise Exception(f"{x} went boom")

    def test_filter_on_failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        filter_result = result.filter(lambda i: i > 5)
        self.assertTrue(filter_result.is_failure())
        self.assertEqual(filter_result.failure_value().code, UCode.INVALID_ARGUMENT)
        self.assertEqual(filter_result.failure_value().message, "boom")

    def test_flatten_on_success(self):
        result = RpcResult.success(2)
        mapped = result.map(lambda x: RpcResult.success(self.multiply_by_2(x)))
        mapped_flattened = RpcResult.flatten(mapped)
        self.assertTrue(mapped_flattened.is_success())
        self.assertEqual(mapped_flattened.success_value(), 4)

    def test_flatten_on_success_with_function_that_fails(self):
        result = RpcResult.success(2)
        flat_mapped = result.flat_map(self.fun_that_throws_exception_for_flat_map)
        self.assertTrue(flat_mapped.is_failure())
        self.assertEqual(UCode.UNKNOWN, flat_mapped.failure_value().code)
        self.assertEqual("2 went boom", flat_mapped.failure_value().message)

    def test_flatten_on_failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        mapped = result.map(lambda x: RpcResult.success(self.multiply_by_2(x)))
        mapped_flattened = RpcResult.flatten(mapped)
        self.assertTrue(mapped_flattened.is_failure())
        self.assertEqual(mapped_flattened.failure_value().code, UCode.INVALID_ARGUMENT)
        self.assertEqual(mapped_flattened.failure_value().message, "boom")

    def multiply_by_2(self, x):
        return x * 2

    def get_default(self):
        return 5

    def test_to_string_success(self):
        result = RpcResult.success(2)
        self.assertEqual(str(result), "Success(2)")

    def test_to_string_failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertTrue(result.is_failure())
        self.assertEqual(result.failure_value().code, UCode.INVALID_ARGUMENT)
        self.assertEqual(result.failure_value().message, "boom")


if __name__ == '__main__':
    unittest.main()
