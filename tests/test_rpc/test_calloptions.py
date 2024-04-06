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

from uprotocol.proto.uattributes_pb2 import CallOptions


class TestCallOptions(unittest.TestCase):

    def test_to_string(self):
        call_options = CallOptions(ttl=30, token="someToken")
        self.assertEqual(30, call_options.ttl)
        self.assertEqual("someToken", call_options.token)

    def test_creating_call_options_with_a_token(self):
        call_options = CallOptions(token="someToken")
        self.assertTrue(call_options.HasField("token"))
        self.assertTrue(call_options.token == "someToken")

    def test_creating_call_options_without_token(self):
        call_options = CallOptions()
        self.assertFalse(call_options.HasField("token"))
        self.assertEqual(0, call_options.ttl)

    def test_creating_call_options_with_an_empty_string_token(self):
        call_options = CallOptions(token="")
        self.assertTrue(call_options.HasField("token"))
        self.assertTrue(call_options.token == "")

    def test_creating_call_options_with_a_token_with_only_spaces(self):
        call_options = CallOptions(token="   ")
        self.assertTrue(call_options.HasField("token"))
        self.assertTrue(call_options.token.strip() == "")

    def test_creating_call_options_with_a_timeout(self):
        call_options = CallOptions(ttl=30)
        self.assertEqual(30, call_options.ttl)
        self.assertTrue(call_options.token is None or call_options.token == "")


if __name__ == '__main__':
    unittest.main()
