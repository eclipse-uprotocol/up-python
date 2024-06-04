"""
SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to the
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

import datetime
import time
import unittest

from uprotocol.proto.uattributes_pb2 import UAttributes, UPriority
from uprotocol.proto.uri_pb2 import UAuthority, UEntity, UResource, UUri
from uprotocol.proto.uuid_pb2 import UUID
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.uuid.factory.uuidutils import UUIDUtils


def create_id():
    return Factories.UPROTOCOL.create()


def build_source():
    return UUri(
        authority=UAuthority(name="vcu.someVin.veh.steven.gm.com"),
        entity=UEntity(name="petapp.steven.gm.com", version_major=1),
        resource=UResource(name="door", instance="front_left", message="Door"),
    )


DELTA = 30
DELAY_MS = 100
DELAY_LONG_MS = 100000
TTL = 10000


class TestUUIDUtils(unittest.TestCase):
    def test_get_elapsed_time_creation_time_unknown(self):
        self.assertFalse(UUIDUtils.get_elapsed_time(UUID()) is not None)

    def test_get_remaining_time_no_ttl(self):
        id: UUID = create_id()
        self.assertFalse(UUIDUtils.get_remaining_time(id, 0) is not None)
        self.assertFalse(UUIDUtils.get_remaining_time(id, -1) is not None)

    def test_remaining_time_none_uuid(self):
        id: UUID = None
        self.assertFalse(UUIDUtils.get_remaining_time(id, 0) is not None)

    def test_get_remaining_time_expired(self):
        id: UUID = create_id()
        time.sleep(DELAY_MS / 1000)
        self.assertFalse(UUIDUtils.get_remaining_time(id, DELAY_MS - DELTA) is not None)

    def test_get_remaining_time_attributes_no_ttl(self):
        attributes: UAttributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).build()
        self.assertFalse(UUIDUtils.get_remaining_time(attributes) is not None)

    def test_get_remaining_time_attributes_expired(self):
        attributes: UAttributes = (
            UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_ttl(DELAY_MS - DELTA).build()
        )
        time.sleep(DELAY_MS / 1000)
        self.assertFalse(UUIDUtils.get_remaining_time(attributes) is not None)

    def test_is_expired(self):
        id: UUID = create_id()
        self.assertFalse(UUIDUtils.is_expired(id, DELAY_MS - DELTA))
        time.sleep(DELAY_MS / 1000)
        self.assertTrue(UUIDUtils.is_expired(id, DELAY_MS - DELTA))

    def test_is_expired_no_ttl(self):
        id: UUID = create_id()
        self.assertFalse(UUIDUtils.is_expired(id, 0))
        self.assertFalse(UUIDUtils.is_expired(id, -1))

    def test_is_expired_attributes(self):
        attributes: UAttributes = (
            UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).with_ttl(DELAY_MS - DELTA).build()
        )
        self.assertFalse(UUIDUtils.is_expired(attributes))
        time.sleep(DELAY_MS / 1000)
        self.assertTrue(UUIDUtils.is_expired(attributes))

    def test_is_expired_attributes_no_ttl(self):
        attributes: UAttributes = UAttributesBuilder.publish(build_source(), UPriority.UPRIORITY_CS0).build()
        self.assertFalse(UUIDUtils.is_expired(attributes))

    def test_get_elapsed_time_invalid_uuid(self):
        self.assertFalse(UUIDUtils.get_elapsed_time(None) is not None)

    def test_get_elapsed_time_past(self):
        id: UUID = Factories.UPROTOCOL.create(datetime.datetime.now() + datetime.timedelta(minutes=1))
        self.assertFalse(UUIDUtils.get_elapsed_time(id) is not None)
