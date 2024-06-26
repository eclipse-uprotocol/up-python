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
from datetime import datetime, timedelta, timezone

from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.uuid.factory.uuidutils import UUIDUtils, Version
from uprotocol.uuid.serializer.uuidserializer import UuidSerializer
from uprotocol.v1.uuid_pb2 import UUID


class TestUUIDFactory(unittest.TestCase):
    def test_uuidv7_creation(self):
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

    def test_uuidv7_creation_with_null_instant(self):
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

    def test_uuid_utils_for_random_uuid(self):
        uuid = UuidSerializer.deserialize("195f9bd1-526d-4c28-91b1-ff34c8e3632d")
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

    def test_uuid_utils_for_empty_uuid(self):
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

    def test_uuid_utils_for_null_uuid(self):
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
        time = UUIDUtils.get_time(uuid)
        self.assertTrue(UUIDUtils.is_uprotocol(uuid))
        self.assertTrue(UUIDUtils.is_uuid(uuid))
        self.assertTrue(time is not None)
        self.assertEqual(time, int(past.timestamp() * 1000))

    def test_create_uprotocol_uuid_with_different_time_values(self):
        uuid = Factories.UPROTOCOL.create()
        import time

        time.sleep(0.01)  # Sleep for 10 milliseconds
        uuid1 = Factories.UPROTOCOL.create()
        time = UUIDUtils.get_time(uuid)
        time1 = UUIDUtils.get_time(uuid1)

        self.assertTrue(UUIDUtils.is_uprotocol(uuid))
        self.assertTrue(UUIDUtils.is_uuid(uuid))
        self.assertTrue(UUIDUtils.is_uprotocol(uuid1))
        self.assertTrue(UUIDUtils.is_uuid(uuid1))

        self.assertTrue(time is not None)
        self.assertTrue(time1 is not None)
        self.assertNotEqual(time, time1)

    def test_create_both_uuidv6_and_v7_to_compare_performance(self):
        uuidv6_list = []
        uuidv7_list = []
        max_count = 10000

        for _ in range(max_count):
            uuidv7_list.append(Factories.UPROTOCOL.create())

        for _ in range(max_count):
            uuidv6_list.append(Factories.UUIDV6.create())

    def test_create_uuidv7_with_the_same_time_to_confirm_the_uuids_are_not_the_same(self):
        now = datetime.utcnow()
        factory = Factories.UPROTOCOL
        uuid = factory.create(now)
        uuid1 = factory.create(now)
        self.assertNotEqual(uuid, uuid1)
        self.assertEqual(UUIDUtils.get_time(uuid), UUIDUtils.get_time(uuid1))


if __name__ == "__main__":
    unittest.main()
