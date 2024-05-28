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

from uprotocol.uri.validator.uri_validator import UriValidator
from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri


class TestUriValidator(unittest.TestCase):

    def test_is_empty_with_null_uri(self):
        self.assertTrue(UriValidator.is_empty(None))

    def test_is_empty_with_default_uri(self):
        self.assertTrue(UriValidator.is_empty(UUri()))

    def test_is_empty_with_non_empty_uri(self):
        self.assertFalse(UriValidator.is_empty(UUri(authority_name="hi")))

    def test_is_rpc_method_passing_null_for_uri(self):
        self.assertFalse(UriValidator.is_rpc_method(None))

    def test_is_rpc_method_passing_null_for_uri(self):
        self.assertFalse(UriValidator.is_rpc_method(UUri()))

    def test_is_rpc_method_for_uresource_id_less_than_min_topic(self):
        uri = UUri(resource_id=0x7FFF)
        self.assertTrue(UriValidator.is_rpc_method(uri))

    def test_is_rpc_method_for_uresource_id_greater_than_min_topic(self):
        uri = UUri(resource_id=0x8000)
        self.assertFalse(UriValidator.is_rpc_method(uri))

    def test_is_rpc_response_with_null_uri(self):
        self.assertFalse(UriValidator.is_rpc_response(None))

    # def test_is_rpc_response_with_default_uri(self):
    #     self.assertFalse(UriValidator.is_rpc_response(UUri()))

    def test_is_rpc_response_with_resourceid_equal_rpcresponseid(self):
        uri = UUri(resource_id=UriValidator.RPC_RESPONSE_ID)
        self.assertTrue(UriValidator.is_rpc_response(uri))

    def test_is_rpc_response_with_resourceid_greater_rpcresponseid(self):
        uri = UUri(resource_id=UriValidator.RPC_RESPONSE_ID + 1)
        self.assertFalse(UriValidator.is_rpc_response(uri))


if __name__ == "__main__":
    unittest.main()
