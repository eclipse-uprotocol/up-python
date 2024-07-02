"""
SPDX-FileCopyrightText: 2023 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import unittest

from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.v1.uri_pb2 import UUri


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

    def test_is_rpc_method_none(self):
        self.assertFalse(UriValidator.is_rpc_method(None))

    def test_is_rpc_response_with_resourceid_equal_rpcresponseid(self):
        uri = UUri(authority_name="hi", resource_id=UriValidator.DEFAULT_RESOURCE_ID)
        self.assertTrue(UriValidator.is_rpc_response(uri))

    def test_is_rpc_response_with_resourceid_greater_rpcresponseid(self):
        uri = UUri(resource_id=UriValidator.DEFAULT_RESOURCE_ID + 1)
        self.assertFalse(UriValidator.is_rpc_response(uri))


if __name__ == "__main__":
    unittest.main()
