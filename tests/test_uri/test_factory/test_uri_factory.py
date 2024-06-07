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

from uprotocol.uri.factory.uri_factory import UriFactory

from uprotocol.proto.uprotocol.core.usubscription.v3 import usubscription_pb2


class TestUriFactory(unittest.TestCase):

    def test_from_proto(self):
        service_descriptor = usubscription_pb2.DESCRIPTOR.services_by_name[
            "uSubscription"
        ]
        uri = UriFactory.from_proto(service_descriptor, 0, "")

        self.assertIsNotNone(uri)
        self.assertEqual(uri.resource_id, 0)
        self.assertEqual(uri.ue_id, 0)
        self.assertEqual(uri.ue_version_major, 3)
        self.assertEqual(uri.authority_name, "")

    def test_any(self):
        uri = UriFactory.any_func()
        self.assertIsNotNone(uri)
        self.assertEqual(uri.resource_id, 65535)
        self.assertEqual(uri.ue_id, 65535)
        self.assertEqual(uri.ue_version_major, 255)
        self.assertEqual(uri.authority_name, "*")

    def test_from_proto_with_null_descriptor(self):
        uri = UriFactory.from_proto(None, 0, "")

        self.assertIsNotNone(uri)
        self.assertEqual(uri.resource_id, 0)
        self.assertEqual(uri.ue_id, 0)
        self.assertEqual(uri.ue_version_major, 0)
        self.assertEqual(uri.authority_name, "")
