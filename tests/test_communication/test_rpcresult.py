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

    def test_isSuccess_on_Success(self):
        result = RpcResult.success(2)
        self.assertTrue(result.is_success())

    def test_isSuccess_on_Failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertFalse(result.is_success())

    def test_isFailure_on_Success(self):
        result = RpcResult.success(2)
        self.assertFalse(result.is_failure())

    def test_isFailure_on_Failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertTrue(result.is_failure())

    def testGetOrElseOnSuccess(self):
        result = RpcResult.success(2)
        self.assertEqual(result.get_or_else(lambda: self.getDefault()), 2)

    def testGetOrElseOnFailure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertEqual(result.get_or_else(lambda: self.getDefault()), self.getDefault())

    def testSuccessValue_onSuccess(self):
        result = RpcResult.success(2)
        self.assertEqual(result.success_value(), 2)

    def testSuccessValue_onFailure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        with self.assertRaises(Exception):
            result.success_value()

    def testFailureValue_onSuccess(self):
        result = RpcResult.success(2)
        with self.assertRaises(Exception):
            result.failure_value()

    def testFailureValue_onFailure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertEqual(result.failure_value().code, UCode.INVALID_ARGUMENT)
        self.assertEqual(result.failure_value().message, "boom")

    def testMapOnSuccess(self):
        result = RpcResult.success(2)
        mapped = result.map(lambda x: x * 2)
        self.assertTrue(mapped.is_success())
        self.assertEqual(mapped.success_value(), 4)

    def testMapSuccess_when_function_throws_exception(self):
        result = RpcResult.success(2)
        mapped = result.map(self.funThatThrowsAnExceptionForMap)
        self.assertTrue(mapped.is_failure())
        self.assertEqual(mapped.failure_value().code, UCode.UNKNOWN)
        self.assertEqual(mapped.failure_value().message, "2 went boom")

    def funThatThrowsAnExceptionForMap(self, x):
        raise Exception(f"{x} went boom")

    def testMapOnFailure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        mapped = result.map(lambda x: x * 2)
        self.assertTrue(mapped.is_failure())
        self.assertEqual(mapped.failure_value().code, UCode.INVALID_ARGUMENT)
        self.assertEqual(mapped.failure_value().message, "boom")

    def testFlatMapOnSuccess(self):
        result = RpcResult.success(2)
        flatMapped = result.flat_map(lambda x: RpcResult.success(x * 2))
        self.assertTrue(flatMapped.is_success())
        self.assertEqual(flatMapped.success_value(), 4)

    def testFlatMapOnFailure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        flatMapped = result.flat_map(lambda x: RpcResult.success(x * 2))
        self.assertTrue(flatMapped.is_failure())
        self.assertEqual(flatMapped.failure_value().code, UCode.INVALID_ARGUMENT)
        self.assertEqual(flatMapped.failure_value().message, "boom")

    def testFilterOnSuccess_that_fails(self):
        result = RpcResult.success(2)
        filter_result = result.filter(lambda i: i > 5)
        self.assertTrue(filter_result.is_failure())
        self.assertEqual(filter_result.failure_value().code, UCode.FAILED_PRECONDITION)
        self.assertEqual(filter_result.failure_value().message, "filtered out")

    def testFilterOnSuccess_that_succeeds(self):
        result = RpcResult.success(2)
        filter_result = result.filter(lambda i: i < 5)
        self.assertTrue(filter_result.is_success())
        self.assertEqual(filter_result.success_value(), 2)

    def testFilterOnSuccess_when_function_throws_exception(self):
        result = RpcResult.success(2)
        filter_result = result.filter(self.predicateThatThrowsAnException)
        self.assertTrue(filter_result.is_failure())
        self.assertEqual(filter_result.failure_value().code, UCode.UNKNOWN)
        self.assertEqual(filter_result.failure_value().message, "2 went boom")

    def predicateThatThrowsAnException(self, x):
        raise Exception(f"{x} went boom")

    def testFilterOnFailure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        filter_result = result.filter(lambda i: i > 5)
        self.assertTrue(filter_result.is_failure())
        self.assertEqual(filter_result.failure_value().code, UCode.INVALID_ARGUMENT)
        self.assertEqual(filter_result.failure_value().message, "boom")

    def testFlattenOnSuccess(self):
        result = RpcResult.success(2)
        mapped = result.map(lambda x: RpcResult.success(self.multiplyBy2(x)))
        mapped_flattened = RpcResult.flatten(mapped)
        self.assertTrue(mapped_flattened.is_success())
        self.assertEqual(mapped_flattened.success_value(), 4)

    def testFlattenOnSuccess_with_function_that_fails(self):
        result = RpcResult.success(2)
        flat_mapped = result.flat_map(self.fun_that_throws_exception_for_flat_map)
        self.assertTrue(flat_mapped.is_failure())
        self.assertEqual(UCode.UNKNOWN, flat_mapped.failure_value().code)
        self.assertEqual("2 went boom", flat_mapped.failure_value().message)

    def testFlattenOnFailure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        mapped = result.map(lambda x: RpcResult.success(self.multiplyBy2(x)))
        mapped_flattened = RpcResult.flatten(mapped)
        self.assertTrue(mapped_flattened.is_failure())
        self.assertEqual(mapped_flattened.failure_value().code, UCode.INVALID_ARGUMENT)
        self.assertEqual(mapped_flattened.failure_value().message, "boom")

    def multiplyBy2(self, x):
        return x * 2

    def getDefault(self):
        return 5

    def testToStringSuccess(self):
        result = RpcResult.success(2)
        self.assertEqual(str(result), "Success(2)")

    def testToStringFailure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertEqual(str(result), "Failure(code: INVALID_ARGUMENT\nmessage: \"boom\"\n)")


if __name__ == '__main__':
    unittest.main()
