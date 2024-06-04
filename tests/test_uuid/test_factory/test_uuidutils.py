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

import unittest
import time
import datetime

from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.uuid.factory.uuidutils import UUIDUtils

from uprotocol.proto.uprotocol.v1.uuid_pb2 import UUID


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
        self.assertFalse(
            UUIDUtils.get_remaining_time(id, DELAY_MS - DELTA) is not None
        )

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
        id: UUID = Factories.UPROTOCOL.create(
            datetime.datetime.now() + datetime.timedelta(minutes=1)
        )
        self.assertFalse(UUIDUtils.get_elapsed_time(id) is not None)
