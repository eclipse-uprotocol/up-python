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

from uprotocol.proto.uri_pb2 import UAuthority, UEntity, UResource, UUri
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.uri.serializer.microuriserializer import MicroUriSerializer
from uprotocol.uri.validator.urivalidator import UriValidator


class TestUriSerializer(unittest.TestCase):

    def test_build_resolved_valid_long_micro_uri(self):
        long_uuri = UUri(authority=UAuthority(name="testauth"), entity=UEntity(name="neelam"),
                         resource=UResource(name="rpc", instance="response"))
        micro_uuri = UUri(entity=UEntity(id=29999, version_major=254), resource=UResource(id=39999))
        microuri = MicroUriSerializer().serialize(micro_uuri)
        longuri = LongUriSerializer().serialize(long_uuri)
        resolved_uuri = LongUriSerializer().build_resolved(longuri, microuri)
        self.assertTrue(resolved_uuri)
        self.assertFalse(UriValidator.is_empty(resolved_uuri))
        self.assertEqual("testauth", resolved_uuri.authority.name)
        self.assertEqual("neelam", resolved_uuri.entity.name)
        self.assertEqual(29999, resolved_uuri.entity.id)
        self.assertEqual(254, resolved_uuri.entity.version_major)
        self.assertEqual("rpc", resolved_uuri.resource.name)
        self.assertEqual("response", resolved_uuri.resource.instance)
        self.assertEqual(39999, resolved_uuri.resource.id)

    def test_build_resolved_null_long_null_micro_uri(self):
        result = MicroUriSerializer().build_resolved(None, None)
        self.assertTrue(result)
        self.assertTrue(UriValidator.is_empty(result))

    def test_build_resolved_null_long_micro_uri(self):
        result = MicroUriSerializer().build_resolved(None, bytes())
        self.assertTrue(result)
        self.assertTrue(UriValidator.is_empty(result))

    def test_build_resolved_valid_long_null_micro_uri(self):
        result = MicroUriSerializer().build_resolved("", bytes())
        self.assertTrue(result)
        self.assertTrue(UriValidator.is_empty(result))


if __name__ == '__main__':
    unittest.main()
