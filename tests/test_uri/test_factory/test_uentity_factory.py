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

from uprotocol.proto.core.usubscription.v3.usubscription_pb2 import (
    DESCRIPTOR as USubscriptionFileDescriptor,
)
from uprotocol.proto.core.udiscovery.v3.udiscovery_pb2 import (
    DESCRIPTOR as UDiscoveryFileDescriptor,
)
from uprotocol.proto.core.utwin.v2.utwin_pb2 import (
    DESCRIPTOR as UTwinFileDescriptor,
)
from uprotocol.proto.uri_pb2 import UEntity
from uprotocol.uri.factory.uentity_factory import UEntityFactory

from google.protobuf.descriptor import ServiceDescriptor, FileDescriptor


class TestUEntityFactory(unittest.TestCase):

    def test_from_proto_given_usubscription_descriptor_return_uentity(self):
        """
        Get default service values:
        Example: in uSubscription.proto...

        // Subscription Service Interface definition
        service uSubscription {
            option (name) = "core.usubscription"; // Service name
            option (version_major) = 3;
            option (version_minor) = 0;
            option (id) = 0;
            ...
        }
        """
        file_descriptor: FileDescriptor = USubscriptionFileDescriptor
        service_descriptor: ServiceDescriptor = (
            file_descriptor.services_by_name["uSubscription"]
        )
        default_service_name: str = "core.usubscription"
        default_version_major: str = 3
        default_version_minor: str = 0
        default_id = 0

        actual_uentity: UEntity = UEntityFactory.from_proto(service_descriptor)
        self.assertIsNotNone(actual_uentity)

        self.assertEqual(default_service_name, actual_uentity.name)
        self.assertEqual(default_version_major, actual_uentity.version_major)
        self.assertEqual(default_version_minor, actual_uentity.version_minor)
        self.assertEqual(default_id, actual_uentity.id)

    def test_from_proto_given_udiscovery_descriptor_return_uentity(self):
        file_descriptor: FileDescriptor = UDiscoveryFileDescriptor
        service_descriptor: ServiceDescriptor = (
            file_descriptor.services_by_name["uDiscovery"]
        )
        default_service_name: str = "core.udiscovery"
        default_version_major: str = 3
        default_version_minor: str = 0
        default_id = 1

        actual_uentity: UEntity = UEntityFactory.from_proto(service_descriptor)
        self.assertIsNotNone(actual_uentity)

        self.assertEqual(default_service_name, actual_uentity.name)
        self.assertEqual(default_version_major, actual_uentity.version_major)
        self.assertEqual(default_version_minor, actual_uentity.version_minor)
        self.assertEqual(default_id, actual_uentity.id)

    def test_from_proto_given_utwin_descriptor_return_uentity(self):
        file_descriptor: FileDescriptor = UTwinFileDescriptor
        service_descriptor: ServiceDescriptor = (
            file_descriptor.services_by_name["uTwin"]
        )
        default_service_name: str = "core.utwin"
        default_version_major: str = 2
        default_version_minor: str = 0
        default_id = 26

        actual_uentity: UEntity = UEntityFactory.from_proto(service_descriptor)
        self.assertIsNotNone(actual_uentity)

        self.assertEqual(default_service_name, actual_uentity.name)
        self.assertEqual(default_version_major, actual_uentity.version_major)
        self.assertEqual(default_version_minor, actual_uentity.version_minor)
        self.assertEqual(default_id, actual_uentity.id)

    def test_from_proto_given_none_return_empty_uentity(self):
        empty_service_name: str = ""
        empty_version_major: str = 0
        empty_version_minor: str = 0
        empty_id = 0

        actual_uentity: UEntity = UEntityFactory.from_proto(None)
        self.assertIsNotNone(actual_uentity)

        self.assertEqual(empty_service_name, actual_uentity.name)
        self.assertEqual(empty_version_major, actual_uentity.version_major)
        self.assertEqual(empty_version_minor, actual_uentity.version_minor)
        self.assertEqual(empty_id, actual_uentity.id)
