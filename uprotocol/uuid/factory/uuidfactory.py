"""
SPDX-FileCopyrightText: 2023 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import random
from datetime import datetime

from uprotocol.uuid.factory import uuid6
from uprotocol.uuid.factory.uuidutils import UUIDUtils
from uprotocol.v1.uuid_pb2 import UUID


class UUIDFactory:
    def create(self, instant=None):
        if instant is None:
            instant = datetime.now()
        return self._create(instant)

    def _create(self, instant):
        pass


class UUIDv6Factory(UUIDFactory):
    def _create(self, instant) -> UUID:
        python_uuid = uuid6()
        msb, lsb = UUIDUtils.get_msb_lsb(python_uuid)
        return UUID(msb=msb, lsb=lsb)


class UUIDv8Factory(UUIDFactory):
    MAX_COUNT = 0xFFF
    _lsb = (random.getrandbits(63) & 0x3FFFFFFFFFFFFFFF) | 0x8000000000000000
    UUIDV8_VERSION = 8
    _msb = UUIDV8_VERSION << 12

    def _create(self, instant) -> UUID:
        time = int(instant.timestamp() * 1000) if instant else int(datetime.now().timestamp() * 1000)

        if time == (self._msb >> 16):
            if (self._msb & 0xFFF) < self.MAX_COUNT:
                self._msb += 1
        else:
            self._msb = (time << 16) | (8 << 12)

        return UUID(msb=self._msb, lsb=self._lsb)


class Factories:
    UUIDV6 = UUIDv6Factory()
    UPROTOCOL = UUIDv8Factory()
