"""
SPDX-FileCopyrightText: 2023 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import datetime
import time
import unittest

from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.uuid.factory.uuidutils import UUIDUtils
from uprotocol.v1.uuid_pb2 import UUID


def create_id():
    return Factories.UPROTOCOL.create()


DELTA = 30
DELAY_MS = 100
DELAY_LONG_MS = 100000
TTL = 10000


class TestUUIDUtils(unittest.TestCase):
    def test_get_elapsed_time(self):
        id_val: UUID = create_id()
        self.assertIsNotNone(UUIDUtils.get_elapsed_time(id_val))

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

    def test_is_expired(self):
        id: UUID = create_id()
        self.assertFalse(UUIDUtils.is_expired(id, DELAY_MS - DELTA))
        time.sleep(DELAY_MS / 1000)
        self.assertTrue(UUIDUtils.is_expired(id, DELAY_MS - DELTA))

    def test_is_expired_no_ttl(self):
        id_val: UUID = create_id()
        self.assertFalse(UUIDUtils.is_expired(id_val, 0))
        self.assertFalse(UUIDUtils.is_expired(id_val, -1))

    def test_get_elapsed_time_invalid_uuid(self):
        self.assertFalse(UUIDUtils.get_elapsed_time(None) is not None)

    def test_get_elapsed_time_past(self):
        id: UUID = Factories.UPROTOCOL.create(datetime.datetime.now() + datetime.timedelta(minutes=1))
        self.assertFalse(UUIDUtils.get_elapsed_time(id) is not None)
