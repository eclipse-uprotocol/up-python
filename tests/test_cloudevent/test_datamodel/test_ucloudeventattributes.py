# -------------------------------------------------------------------------

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

# -------------------------------------------------------------------------

import unittest

from uprotocol.cloudevent.datamodel.ucloudeventattributes import (
    UCloudEventAttributesBuilder,
    UCloudEventAttributes,
)
from uprotocol.proto.uattributes_pb2 import UPriority


class TestUCloudEventAttributes(unittest.TestCase):

    def test_to_string(self):
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_hash("somehash")
            .with_priority(UPriority.UPRIORITY_CS1)
            .with_ttl(3)
            .with_token("someOAuthToken")
            .build()
        )

        expected = "UCloudEventAttributes{hash='somehash', priority=UPRIORITY_CS1, ttl=3, token='someOAuthToken'}"
        self.assertEqual(expected, str(u_cloud_event_attributes))

    def test_create_valid_with_blank_traceparent(self):
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_hash("somehash")
            .with_priority(UPriority.UPRIORITY_CS1)
            .with_ttl(3)
            .with_token("someOAuthToken")
            .with_traceparent(" ")
            .build()
        )
        self.assertTrue(u_cloud_event_attributes.get_hash() is not None)
        self.assertEqual("somehash", u_cloud_event_attributes.get_hash())
        self.assertFalse(
            u_cloud_event_attributes.get_traceparent() is not None
        )

    def test_create_empty_with_only_traceparent(self):
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_traceparent("someTraceParent")
            .build()
        )
        self.assertFalse(u_cloud_event_attributes.get_hash() is not None)
        self.assertFalse(u_cloud_event_attributes.get_priority() is not None)
        self.assertFalse(u_cloud_event_attributes.get_token() is not None)
        self.assertFalse(u_cloud_event_attributes.get_ttl() is not None)
        self.assertTrue(u_cloud_event_attributes.get_traceparent() is not None)
        self.assertFalse(u_cloud_event_attributes.is_empty())
        self.assertEqual(
            "someTraceParent", u_cloud_event_attributes.get_traceparent()
        )

    def test_create_valid(self):
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_hash("somehash")
            .with_priority(UPriority.UPRIORITY_CS6)
            .with_ttl(3)
            .with_token("someOAuthToken")
            .build()
        )

        self.assertEqual("somehash", u_cloud_event_attributes.get_hash())
        self.assertEqual(
            UPriority.Name(UPriority.UPRIORITY_CS6),
            u_cloud_event_attributes.get_priority(),
        )
        self.assertEqual(3, u_cloud_event_attributes.get_ttl())
        self.assertEqual(
            "someOAuthToken", u_cloud_event_attributes.get_token()
        )

    def test_is_empty_function(self):
        u_cloud_event_attributes = UCloudEventAttributes.empty()
        self.assertTrue(u_cloud_event_attributes.is_empty())
        self.assertTrue(u_cloud_event_attributes.priority is None)
        self.assertTrue(u_cloud_event_attributes.token is None)
        self.assertTrue(u_cloud_event_attributes.ttl is None)

    def test_is_empty_function_when_built_with_blank_strings(self):
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_hash("  ")
            .with_token("  ")
            .build()
        )
        self.assertTrue(u_cloud_event_attributes.is_empty())
        self.assertTrue(u_cloud_event_attributes.hash.isspace())
        self.assertTrue(u_cloud_event_attributes.priority is None)
        self.assertTrue(u_cloud_event_attributes.token.isspace())
        self.assertTrue(u_cloud_event_attributes.ttl is None)

    def test_is_empty_function_permutations(self):
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_hash("  ")
            .with_token("  ")
            .build()
        )
        self.assertTrue(u_cloud_event_attributes.is_empty())

        u_cloud_event_attributes2 = (
            UCloudEventAttributesBuilder()
            .with_hash("someHash")
            .with_token("  ")
            .build()
        )
        self.assertFalse(u_cloud_event_attributes2.is_empty())

        u_cloud_event_attributes3 = (
            UCloudEventAttributesBuilder()
            .with_hash(" ")
            .with_token("SomeToken")
            .build()
        )
        self.assertFalse(u_cloud_event_attributes3.is_empty())

        u_cloud_event_attributes4 = (
            UCloudEventAttributesBuilder()
            .with_priority(UPriority.UPRIORITY_CS0)
            .build()
        )
        self.assertFalse(u_cloud_event_attributes4.is_empty())

        u_cloud_event_attributes5 = (
            UCloudEventAttributesBuilder().with_ttl(8).build()
        )
        self.assertFalse(u_cloud_event_attributes5.is_empty())

    def test__eq__is_same(self):
        u_cloud_event_attributes = (
            UCloudEventAttributesBuilder()
            .with_hash("  ")
            .with_token("  ")
            .build()
        )
        self.assertTrue(
            u_cloud_event_attributes.__eq__(u_cloud_event_attributes)
        )

    def test__eq__is_equal(self):
        u_cloud_event_attributes_1 = (
            UCloudEventAttributesBuilder()
            .with_hash("  ")
            .with_token("  ")
            .build()
        )
        u_cloud_event_attributes_2 = (
            UCloudEventAttributesBuilder()
            .with_hash("  ")
            .with_token("  ")
            .build()
        )
        self.assertTrue(
            u_cloud_event_attributes_1.__eq__(u_cloud_event_attributes_2)
        )

    def test__eq__is_not_equal(self):
        u_cloud_event_attributes_1 = (
            UCloudEventAttributesBuilder()
            .with_hash("  ")
            .with_token("  ")
            .build()
        )
        u_cloud_event_attributes_2 = (
            UCloudEventAttributesBuilder()
            .with_hash("  ")
            .with_token("12345")
            .build()
        )
        self.assertFalse(
            u_cloud_event_attributes_1.__eq__(u_cloud_event_attributes_2)
        )

    def test__hash__same(self):
        u_cloud_event_attributes_1 = (
            UCloudEventAttributesBuilder()
            .with_hash("  ")
            .with_token("  ")
            .build()
        )
        self.assertEqual(
            hash(u_cloud_event_attributes_1), hash(u_cloud_event_attributes_1)
        )

    def test__hash__different(self):
        u_cloud_event_attributes_1 = (
            UCloudEventAttributesBuilder()
            .with_hash("  ")
            .with_token("  ")
            .build()
        )
        u_cloud_event_attributes_2 = (
            UCloudEventAttributesBuilder()
            .with_hash("  ")
            .with_token("12345")
            .build()
        )
        self.assertNotEqual(
            hash(u_cloud_event_attributes_1), hash(u_cloud_event_attributes_2)
        )


if __name__ == "__main__":
    unittest.main()
