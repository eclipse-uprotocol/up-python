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
from datetime import datetime, timezone

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


class UUIDv7Factory(UUIDFactory):
    def _create(self, instant) -> UUID:
        if instant is None:
            instant = datetime.now(timezone.utc)
        time = int(instant.timestamp() * 1000)  # milliseconds since epoch

        rand_a = random.getrandbits(12)  # 12 bits for random part
        rand_b = random.getrandbits(62)  # 62 bits for random part

        # Construct the MSB (most significant bits)
        msb = (time << 16) | (7 << 12) | rand_a  # version 7 in the 12th bit

        # Construct the LSB (least significant bits)
        lsb = rand_b | (1 << 63)  # set the variant to '1'
        return UUID(msb=msb, lsb=lsb)


class Factories:
    UUIDV6 = UUIDv6Factory()
    UPROTOCOL = UUIDv7Factory()
