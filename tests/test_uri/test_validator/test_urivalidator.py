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

from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.v1.uri_pb2 import UUri


class TestUriValidator(unittest.IsolatedAsyncioTestCase):
    def test_is_empty_with_null_uri(self):
        self.assertTrue(UriValidator.is_empty(None))

    def test_is_empty_with_default_uri(self):
        self.assertTrue(UriValidator.is_empty(UUri()))

    def test_is_empty_with_non_empty_uri(self):
        self.assertFalse(UriValidator.is_empty(UUri(authority_name="hi")))

    def test_is_rpc_method_passing_null_for_uri(self):
        self.assertFalse(UriValidator.is_rpc_method(None))

    def test_is_rpc_method_passing_default_for_uri(self):
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
        uri = UUri(authority_name="hi", resource_id=UriValidator.RESOURCE_ID_RESPONSE)
        self.assertTrue(UriValidator.is_rpc_response(uri))

    def test_is_rpc_response_with_resourceid_greater_rpcresponseid(self):
        uri = UUri(resource_id=UriValidator.RESOURCE_ID_RESPONSE + 1)
        self.assertFalse(UriValidator.is_rpc_response(uri))

    def test_matches_succeeds_for_identical_uris(self):
        pattern_uri = UriSerializer.deserialize("//authority/A410/3/1003")
        candidate_uri = UriSerializer.deserialize("//authority/A410/3/1003")
        self.assertTrue(UriValidator.matches(pattern_uri, candidate_uri))

    def test_matches_succeeds_for_pattern_with_wildcard_authority(self):
        pattern_uri = UriSerializer.deserialize("//*/A410/3/1003")
        candidate_uri = UriSerializer.deserialize("//authority/A410/3/1003")
        self.assertTrue(UriValidator.matches(pattern_uri, candidate_uri))

    def test_matches_succeeds_for_pattern_with_wildcard_authority_and_local_candidate_uri(self):
        pattern_uri = UriSerializer.deserialize("//*/A410/3/1003")
        candidate_uri = UriSerializer.deserialize("/A410/3/1003")
        self.assertTrue(UriValidator.matches(pattern_uri, candidate_uri))

    def test_matches_succeeds_for_pattern_with_wildcard_entity_id(self):
        pattern_uri = UriSerializer.deserialize("//authority/FFFF/3/1003")
        candidate_uri = UriSerializer.deserialize("//authority/A410/3/1003")
        self.assertTrue(UriValidator.matches(pattern_uri, candidate_uri))

    def test_matches_succeeds_for_pattern_with_macthing_entity_instance(self):
        pattern_uri = UriSerializer.deserialize("//authority/A410/3/1003")
        candidate_uri = UriSerializer.deserialize("//authority/2A410/3/1003")
        self.assertTrue(UriValidator.matches(pattern_uri, candidate_uri))

    def test_matches_succeeds_for_pattern_with_wildcard_entity_version(self):
        pattern_uri = UriSerializer.deserialize("//authority/A410/FF/1003")
        candidate_uri = UriSerializer.deserialize("//authority/A410/3/1003")
        self.assertTrue(UriValidator.matches(pattern_uri, candidate_uri))

    def test_matches_succeeds_for_pattern_with_wildcard_resource(self):
        pattern_uri = UriSerializer.deserialize("//authority/A410/3/FFFF")
        candidate_uri = UriSerializer.deserialize("//authority/A410/3/1003")
        self.assertTrue(UriValidator.matches(pattern_uri, candidate_uri))

    def test_matches_fail_for_upper_case_authority(self):
        pattern = UriSerializer.deserialize("//Authority/A410/3/1003")
        candidate = UriSerializer.deserialize("//authority/A410/3/1003")
        self.assertFalse(UriValidator.matches(pattern, candidate))

    def test_matches_fail_for_local_pattern_with_authority(self):
        pattern = UriSerializer.deserialize("/A410/3/1003")
        candidate = UriSerializer.deserialize("//authority/A410/3/1003")
        self.assertFalse(UriValidator.matches(pattern, candidate))

    def test_matches_fail_for_different_authority(self):
        pattern = UriSerializer.deserialize("//other/A410/3/1003")
        candidate = UriSerializer.deserialize("//authority/A410/3/1003")
        self.assertFalse(UriValidator.matches(pattern, candidate))

    def test_matches_fail_for_different_entity_id(self):
        pattern = UriSerializer.deserialize("//authority/45/3/1003")
        candidate = UriSerializer.deserialize("//authority/A410/3/1003")
        self.assertFalse(UriValidator.matches(pattern, candidate))

    def test_matches_fail_for_different_entity_instance(self):
        pattern = UriSerializer.deserialize("//authority/30A410/3/1003")
        candidate = UriSerializer.deserialize("//authority/2A410/3/1003")
        self.assertFalse(UriValidator.matches(pattern, candidate))

    def test_matches_fail_for_different_entity_version(self):
        pattern = UriSerializer.deserialize("//authority/A410/1/1003")
        candidate = UriSerializer.deserialize("//authority/A410/3/1003")
        self.assertFalse(UriValidator.matches(pattern, candidate))

    def test_matches_fail_for_different_resource(self):
        pattern = UriSerializer.deserialize("//authority/A410/3/ABCD")
        candidate = UriSerializer.deserialize("//authority/A410/3/1003")
        self.assertFalse(UriValidator.matches(pattern, candidate))

    def test_has_wildcard_for_null_uuri(self):
        self.assertFalse(UriValidator.has_wildcard(None))

    def test_has_wildcard_for_empty_uuri(self):
        self.assertFalse(UriValidator.has_wildcard(UUri()))

    def test_has_wildcard_for_uuri_with_wildcard_authority(self):
        uri = UriSerializer.deserialize("//*/A410/3/1003")
        self.assertTrue(UriValidator.has_wildcard(uri))

    def test_has_wildcard_for_uuri_with_wildcard_entity_id(self):
        uri = UriSerializer.deserialize("//authority/FFFF/3/1003")
        self.assertTrue(UriValidator.has_wildcard(uri))

    def test_has_wildcard_for_uuri_with_wildcard_entity_instance(self):
        uri = UriSerializer.deserialize("//authority/1FFFF/3/1003")
        self.assertTrue(UriValidator.has_wildcard(uri))

    def test_has_wildcard_for_uuri_with_wildcard_version(self):
        uri = UriSerializer.deserialize("//authority/A410/FF/1003")
        self.assertTrue(UriValidator.has_wildcard(uri))

    def test_has_wildcard_for_uuri_with_wildcard_resource(self):
        uri = UriSerializer.deserialize("//authority/A410/3/FFFF")
        self.assertTrue(UriValidator.has_wildcard(uri))

    def test_has_wildcard_for_uuri_with_no_wildcards(self):
        uri = UriSerializer.deserialize("//authority/A410/3/1003")
        self.assertFalse(UriValidator.has_wildcard(uri))


if __name__ == "__main__":
    unittest.main()
