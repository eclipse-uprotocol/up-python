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

from datetime import datetime, timedelta, timezone
import unittest
from uprotocol.uuid.serializer.uuid_serializer import UuidSerializer
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.uuid.factory.uuidutils import UUIDUtils, Version
from uprotocol.proto.uprotocol.v1.uuid_pb2 import UUID


class TestUUIDFactory(unittest.TestCase):

    def test_uuidv8_creation(self):
        now = datetime.now()
        uuid = Factories.UPROTOCOL.create(now)
        version = UUIDUtils.get_version(uuid)
        time = UUIDUtils.get_time(uuid)
        uuid_string = UuidSerializer.serialize(uuid)

        self.assertIsNotNone(uuid)
        self.assertTrue(UUIDUtils.is_uprotocol(uuid))
        self.assertTrue(UUIDUtils.is_uuid(uuid))
        self.assertFalse(UUIDUtils.is_uuidv6(uuid))
        self.assertTrue(version)
        self.assertTrue(time)
        self.assertEqual(time, int(now.timestamp() * 1000))

        self.assertFalse(uuid_string.isspace())

        uuid2 = UuidSerializer.deserialize(uuid_string)

        self.assertNotEqual(uuid2, UUID())
        self.assertEqual(uuid, uuid2)

    def test_uuidv8_creation_with_null_instant(self):
        uuid = Factories.UPROTOCOL.create(None)
        version = UUIDUtils.get_version(uuid)
        time = UUIDUtils.get_time(uuid)
        uuid_string = UuidSerializer.serialize(uuid)

        self.assertIsNotNone(uuid)
        self.assertTrue(UUIDUtils.is_uprotocol(uuid))
        self.assertTrue(UUIDUtils.is_uuid(uuid))
        self.assertFalse(UUIDUtils.is_uuidv6(uuid))
        self.assertTrue(version)
        self.assertTrue(time)
        self.assertFalse(uuid_string.isspace())

        uuid2 = UuidSerializer.deserialize(uuid_string)

        self.assertNotEqual(uuid2, UUID())
        self.assertEqual(uuid, uuid2)

    def test_uuidv8_overflow(self):
        uuid_list = []
        max_count = 4095

        now = datetime.now()
        for i in range(max_count * 2):
            uuid_list.append(Factories.UPROTOCOL.create(now))

            self.assertEqual(
                UUIDUtils.get_time(uuid_list[0]),
                UUIDUtils.get_time(uuid_list[i]),
            )
            self.assertEqual(uuid_list[0].lsb, uuid_list[i].lsb)
            if i > max_count:
                self.assertEqual(uuid_list[max_count].msb, uuid_list[i].msb)

    def test_uuidv6_creation_with_instant(self):
        now = datetime.now()
        uuid = Factories.UUIDV6.create(now)
        version = UUIDUtils.get_version(uuid)
        uuid_string = UuidSerializer.serialize(uuid)

        self.assertIsNotNone(uuid)
        self.assertTrue(UUIDUtils.is_uuidv6(uuid))
        self.assertTrue(UUIDUtils.is_uuid(uuid))
        self.assertFalse(UUIDUtils.is_uprotocol(uuid))
        self.assertTrue(version)
        self.assertFalse(uuid_string.isspace())

        uuid2 = UuidSerializer.deserialize(uuid_string)

        self.assertNotEqual(uuid2, UUID())
        self.assertEqual(uuid, uuid2)

    def test_uuidv6_creation_with_null_instant(self):
        uuid = Factories.UUIDV6.create(None)
        version = UUIDUtils.get_version(uuid)
        time = UUIDUtils.get_time(uuid)
        uuid_string = UuidSerializer.serialize(uuid)

        self.assertIsNotNone(uuid)
        self.assertTrue(UUIDUtils.is_uuidv6(uuid))
        self.assertFalse(UUIDUtils.is_uprotocol(uuid))
        self.assertTrue(UUIDUtils.is_uuid(uuid))
        self.assertTrue(version)
        self.assertTrue(time)
        self.assertFalse(uuid_string.isspace())

        uuid2 = UuidSerializer.deserialize(uuid_string)

        self.assertNotEqual(uuid2, UUID())
        self.assertEqual(uuid, uuid2)

    def test_UUIDUtils_for_random_uuid(self):
        uuid = UuidSerializer.deserialize(
            "195f9bd1-526d-4c28-91b1-ff34c8e3632d"
        )
        version = UUIDUtils.get_version(uuid)
        time = UUIDUtils.get_time(uuid)
        uuid_string = UuidSerializer.serialize(uuid)

        self.assertIsNotNone(uuid)
        self.assertFalse(UUIDUtils.is_uuidv6(uuid))
        self.assertFalse(UUIDUtils.is_uprotocol(uuid))
        self.assertFalse(UUIDUtils.is_uuid(uuid))
        self.assertTrue(version)
        self.assertFalse(time)
        self.assertFalse(uuid_string.isspace())

        uuid2 = UuidSerializer.deserialize(uuid_string)

        self.assertNotEqual(uuid2, UUID())
        self.assertEqual(uuid, uuid2)

    def test_UUIDUtils_for_empty_uuid(self):
        uuid = UUID()
        version = UUIDUtils.get_version(uuid)
        time = UUIDUtils.get_time(uuid)
        uuid_string = UuidSerializer.serialize(uuid)

        self.assertIsNotNone(uuid)
        self.assertFalse(UUIDUtils.is_uuidv6(uuid))
        self.assertFalse(UUIDUtils.is_uprotocol(uuid))
        self.assertTrue(version)
        self.assertEqual(version, Version.VERSION_UNKNOWN)
        self.assertFalse(time)
        self.assertFalse(uuid_string.isspace())
        self.assertFalse(UUIDUtils.is_uuidv6(None))
        self.assertFalse(UUIDUtils.is_uprotocol(None))
        self.assertFalse(UUIDUtils.is_uuid(None))

        uuid2 = UuidSerializer.deserialize(uuid_string)
        self.assertTrue(uuid2, UUID())
        self.assertEqual(uuid, uuid2)

    def test_UUIDUtils_for_null_uuid(self):
        self.assertFalse(UUIDUtils.get_version(None))
        self.assertEqual(len(UuidSerializer.serialize(None)), 0)
        self.assertFalse(UUIDUtils.is_uuidv6(None))
        self.assertFalse(UUIDUtils.is_uprotocol(None))
        self.assertFalse(UUIDUtils.is_uuid(None))
        self.assertFalse(UUIDUtils.get_time(None))

    def test_uuidutils_from_invalid_uuid(self):
        uuid = UUID(msb=9 << 12, lsb=0)  # Invalid UUID type
        self.assertFalse(UUIDUtils.get_version(uuid))
        self.assertFalse(UUIDUtils.get_time(uuid))
        self.assertFalse(UuidSerializer.serialize(uuid).isspace())
        self.assertFalse(UUIDUtils.is_uuidv6(uuid))
        self.assertFalse(UUIDUtils.is_uprotocol(uuid))
        self.assertFalse(UUIDUtils.is_uuid(uuid))
        self.assertFalse(UUIDUtils.get_time(uuid))

    def test_uuidutils_fromstring_with_invalid_string(self):
        uuid = UuidSerializer.deserialize(None)
        self.assertEqual(uuid, UUID())
        uuid1 = UuidSerializer.deserialize("")
        self.assertEqual(uuid1, UUID())

    def test_create_uprotocol_uuid_in_the_past(self):
        now = datetime.now()
        past = now - timedelta(seconds=10)
        past = past.replace(tzinfo=timezone.utc)
        uuid = Factories.UPROTOCOL.create(past)
        time_val = UUIDUtils.get_time(uuid)
        self.assertTrue(UUIDUtils.is_uprotocol(uuid))
        self.assertTrue(UUIDUtils.is_uuid(uuid))
        self.assertIsNotNone(time_val)
        self.assertEqual(time_val, int(past.timestamp() * 1000))

    def test_create_uprotocol_uuid_with_different_time_values(self):
        uuid = Factories.UPROTOCOL.create()
        import time

        time.sleep(0.01)  # Sleep for 10 milliseconds
        uuid1 = Factories.UPROTOCOL.create()
        time_val = UUIDUtils.get_time(uuid)
        time1 = UUIDUtils.get_time(uuid1)

        self.assertTrue(UUIDUtils.is_uprotocol(uuid))
        self.assertTrue(UUIDUtils.is_uuid(uuid))
        self.assertTrue(UUIDUtils.is_uprotocol(uuid1))
        self.assertTrue(UUIDUtils.is_uuid(uuid1))

        self.assertIsNotNone(time_val)
        self.assertIsNotNone(time1)
        self.assertNotEqual(time_val, time1)

    def test_create_both_uuidv6_and_v8_to_compare_performance(self):
        uuidv6_list = []
        uuidv8_list = []
        max_count = 10000

        for _ in range(max_count):
            uuidv8_list.append(Factories.UPROTOCOL.create())

        for _ in range(max_count):
            uuidv6_list.append(Factories.UUIDV6.create())


if __name__ == "__main__":
    unittest.main()
