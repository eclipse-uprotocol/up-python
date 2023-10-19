# -------------------------------------------------------------------------

# Copyright (c) 2023 General Motors GTO LLC

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# -------------------------------------------------------------------------
import time
import uuid

import org_eclipse_uprotocol.uuid.factory as uuid


class UUIDFactory:
    def create(self, instant=None):
        if instant is None:
            instant = int(time.time() * 1000)  # Current time in milliseconds
        return self._create(instant)

    def _create(self, instant):
        pass


class UUIDv6Factory(UUIDFactory):

    def _create(self, instant):
        return uuid.uuid6()


class UUIDv8Factory(UUIDFactory):

    def _create(self, instant):
        return uuid.uuid8()


class Factories:
    UUIDV6 = UUIDv6Factory()
    UPROTOCOL = UUIDv8Factory()


def is_uuid_version_6(uuid):
    try:
        return uuid.version == 6

    except ValueError:
        # Invalid UUID string
        return False


def is_version_8(uuid):
    return uuid.version == 8
