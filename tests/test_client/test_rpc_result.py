"""
SPDX-FileCopyrightText: Copyright (c) 2023 Contributors to the 
Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SPDX-FileType: SOURCE
SPDX-License-Identifier: Apache-2.0
"""

import unittest

from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UCode, UStatus
from uprotocol.client.rpc_result import RpcResult


def getDefault():
    return 5


def multiply_by_2(x):
    return RpcResult.success(x * 2)


class TestRpcResult(unittest.TestCase):

    def test_isSuccess_on_Success(self):
        result = RpcResult.success(2)
        self.assertTrue(result.isSuccess())

    def test_isSuccess_on_Failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertFalse(result.isSuccess())

    def test_isFailure_on_Success(self):
        result = RpcResult.success(2)
        self.assertFalse(result.isFailure())

    def test_isFailure_on_Failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertTrue(result.isFailure())

    def testGetOrElseOnSuccess(self):
        result = RpcResult.success(2)
        self.assertEqual(2, result.getOrElse(getDefault()))

    def testGetOrElseOnFailure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertEqual(getDefault(), result.getOrElse(getDefault))

    def testGetOrElseOnSuccess_(self):
        result = RpcResult.success(2)
        self.assertEqual(2, result.getOrElse(5))

    def testGetOrElseOnFailure_(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertEqual(5, result.getOrElse(5))

    def testSuccessValue_onSuccess(self):
        result = RpcResult.success(2)
        self.assertEqual(2, result.successValue())

    def testSuccessValue_onFailure_(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        with self.assertRaises(Exception) as context:
            result.successValue()
        self.assertEqual(str(context.exception), "Method successValue() called on a Failure instance")

    def testFailureValue_onSuccess(self):
        result = RpcResult.success(2)
        with self.assertRaises(Exception) as context:
            result.failureValue()
        self.assertEqual(str(context.exception), "Method failureValue() called on a Success instance")

    def testFailureValue_onFailure_(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        result_value = result.failureValue()
        expected_result = UStatus(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertEqual(expected_result, result_value)

    def testMapOnSuccess(self):
        result = RpcResult.success(2)
        mapped = result.map(lambda x: x * 2)
        self.assertTrue(mapped.isSuccess())
        self.assertEqual(4, mapped.successValue())

    def test_map_success_when_function_throws_exception(self):
        result = RpcResult.success(2)
        mapped = result.map(self.fun_that_throws_exception_for_map)
        self.assertTrue(mapped.isFailure())
        self.assertEqual(UCode.UNKNOWN, mapped.failureValue().code)
        self.assertEqual("2 went boom", mapped.failureValue().message)

    def test_map_on_failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        mapped = result.map(lambda x: x * 2)
        self.assertTrue(mapped.isFailure())
        expected_status = UStatus(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertEqual(expected_status, mapped.failureValue())

    def test_flat_map_success_when_function_throws_exception(self):
        result = RpcResult.success(2)
        flat_mapped = result.flatMap(self.fun_that_throws_exception_for_flat_map)
        self.assertTrue(flat_mapped.isFailure())
        self.assertEqual(UCode.UNKNOWN, flat_mapped.failureValue().code)
        self.assertEqual("2 went boom", flat_mapped.failureValue().message)

    def fun_that_throws_exception_for_flat_map(self, x):
        raise ValueError(f"{x} went boom")

    def fun_that_throws_exception_for_map(self, x):
        raise ValueError(f"{x} went boom")

    def test_flat_map_on_success(self):
        result = RpcResult.success(2)
        flat_mapped = result.flatMap(lambda x: RpcResult.success(x * 2))
        self.assertTrue(flat_mapped.isSuccess())
        self.assertEqual(4, flat_mapped.successValue())

    def test_flat_map_on_failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        flat_mapped = result.flatMap(lambda x: RpcResult.success(x * 2))
        self.assertTrue(flat_mapped.isFailure())
        expected_status = UStatus(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertEqual(expected_status, flat_mapped.failureValue())

    def test_filter_on_success_that_fails(self):
        result = RpcResult.success(2)
        filter_result = result.filter(lambda i: i > 5)
        self.assertTrue(filter_result.isFailure())
        expected_status = UStatus(code=UCode.FAILED_PRECONDITION, message="filtered out")
        self.assertEqual(expected_status, filter_result.failureValue())

    def test_filter_on_success_that_succeeds(self):
        result = RpcResult.success(2)
        filter_result = result.filter(lambda i: i < 5)
        self.assertTrue(filter_result.isSuccess())
        self.assertEqual(2, filter_result.successValue())

    def test_filter_on_success_when_function_throws_exception(self):
        result = RpcResult.success(2)
        filter_result = result.filter(self.predicate_that_throws_exception)
        self.assertTrue(filter_result.isFailure())
        expected_status = UStatus(code=UCode.UNKNOWN, message="2 went boom")
        self.assertEqual(expected_status, filter_result.failureValue())

    def predicate_that_throws_exception(self, x):
        raise ValueError(f"{x} went boom")

    def test_filter_on_failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        filter_result = result.filter(lambda i: i > 5)
        self.assertTrue(filter_result.isFailure())
        expected_status = UStatus(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertEqual(expected_status, filter_result.failureValue())

    def test_flatten_on_success(self):
        result = RpcResult.success(2)
        mapped = result.map(multiply_by_2)
        mapped_flattened = RpcResult.flatten(mapped)
        self.assertTrue(mapped_flattened.isSuccess())
        self.assertEqual(4, mapped_flattened.successValue())

    def test_flatten_on_success_with_function_that_fails(self):
        result = RpcResult.success(2)
        mapped = result.map(self.fun_that_throws_exception_for_flat_map)
        mapped_flattened = RpcResult.flatten(mapped)
        self.assertTrue(mapped_flattened.isFailure())
        expected_status = UStatus(code=UCode.UNKNOWN, message="2 went boom")
        self.assertEqual(expected_status, mapped_flattened.failureValue())

    def test_flatten_on_failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        mapped = result.map(multiply_by_2)
        mapped_flattened = RpcResult.flatten(mapped)
        self.assertTrue(mapped_flattened.isFailure())
        expected_status = UStatus(code=UCode.INVALID_ARGUMENT, message="boom")
        self.assertEqual(expected_status, mapped_flattened.failureValue())

    def test_to_string_success(self):
        result = RpcResult.success(2)
        self.assertEqual("Success(2)", str(result))

    def test_to_string_failure(self):
        result = RpcResult.failure(code=UCode.INVALID_ARGUMENT, message="boom")
        expected_string = ("Failure(code: INVALID_ARGUMENT\n"
                           "'message: \"boom\"\n)")
        self.assertEqual(expected_string, str(result))


if __name__ == "__main__":
    unittest.main()
