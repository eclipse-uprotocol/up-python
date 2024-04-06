# -------------------------------------------------------------------------
# Copyright (c) 2024 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: 2024 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0

# -------------------------------------------------------------------------


import random
from datetime import datetime

from uprotocol.proto.uuid_pb2 import UUID
from uprotocol.uuid.factory import uuid6
from uprotocol.uuid.factory.uuidutils import UUIDUtils


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
        time = (
            int(instant.timestamp() * 1000)
            if instant
            else int(datetime.now().timestamp() * 1000)
        )

        if time == (self._msb >> 16):
            if (self._msb & 0xFFF) < self.MAX_COUNT:
                self._msb += 1
        else:
            self._msb = (time << 16) | (8 << 12)

        return UUID(msb=self._msb, lsb=self._lsb)
        # return UUID(msb=msb, lsb=lsb)


class Factories:
    UUIDV6 = UUIDv6Factory()
    UPROTOCOL = UUIDv8Factory()
