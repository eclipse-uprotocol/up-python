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

from uprotocol.core.usubscription.v3 import usubscription_pb2
from uprotocol.uri.factory.uri_factory import UriFactory


class TestUriFactory(unittest.TestCase):
    def test_from_proto(self):
        service_descriptor = usubscription_pb2.DESCRIPTOR.services_by_name["uSubscription"]
        uri = UriFactory.from_proto(service_descriptor, 0, "")

        self.assertIsNotNone(uri)
        self.assertEqual(uri.resource_id, 0)
        self.assertEqual(uri.ue_id, 0)
        self.assertEqual(uri.ue_version_major, 3)
        self.assertEqual(uri.authority_name, "")

    def test_any(self):
        uri = UriFactory.ANY
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
