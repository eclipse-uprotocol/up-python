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

from uprotocol.rpc.calloptions import CallOptions, CallOptionsBuilder


class TestCallOptions(unittest.TestCase):

    def test_hash_code_equals(self):
        call_options = CallOptionsBuilder().build()
        self.assertEqual(hash(call_options), hash(call_options))

    def test_to_string(self):
        call_options = CallOptionsBuilder().with_timeout(30).with_token("someToken").build()
        expected = "CallOptions{mTimeout=30, mToken='someToken'}"
        self.assertEqual(expected, str(call_options))

    def test_creating_call_options_default(self):
        call_options = CallOptionsBuilder.DEFAULT
        self.assertEqual(CallOptions.TIMEOUT_DEFAULT, call_options.get_timeout())
        self.assertTrue(call_options.get_token() is None or call_options.get_token() == "")

    def test_creating_call_options_with_a_token(self):
        call_options = CallOptionsBuilder().with_token("someToken").build()
        self.assertEqual(CallOptions.TIMEOUT_DEFAULT, call_options.get_timeout())
        self.assertTrue(call_options.get_token() == "someToken")

    def test_creating_call_options_with_a_null_token(self):
        call_options = CallOptionsBuilder().with_token(None).build()
        self.assertEqual(CallOptions.TIMEOUT_DEFAULT, call_options.get_timeout())
        self.assertTrue(call_options.get_token() is None or call_options.get_token() == "")

    def test_creating_call_options_with_an_empty_string_token(self):
        call_options = CallOptionsBuilder().with_token("").build()
        self.assertEqual(CallOptions.TIMEOUT_DEFAULT, call_options.get_timeout())
        self.assertTrue(call_options.get_token() is None or call_options.get_token() == "")

    def test_creating_call_options_with_a_token_with_only_spaces(self):
        call_options = CallOptionsBuilder().with_token("   ").build()
        self.assertEqual(CallOptions.TIMEOUT_DEFAULT, call_options.get_timeout())
        self.assertTrue(call_options.get_token() is None or call_options.get_token().isspace())

    def test_creating_call_options_with_a_timeout(self):
        call_options = CallOptionsBuilder().with_timeout(30).build()
        self.assertEqual(30, call_options.get_timeout())
        self.assertTrue(call_options.get_token() is None or call_options.get_token() == "")

    def test_creating_call_options_with_a_negative_timeout(self):
        call_options = CallOptionsBuilder().with_timeout(-3).build()
        self.assertEqual(CallOptions.TIMEOUT_DEFAULT, call_options.get_timeout())
        self.assertTrue(call_options.get_token() is None or call_options.get_token() == "")


if __name__ == '__main__':
    unittest.main()
