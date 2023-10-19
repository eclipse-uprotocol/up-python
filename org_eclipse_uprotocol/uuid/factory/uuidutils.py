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
import uuid
from enum import Enum
from typing import Optional

from org_eclipse_uprotocol.uuid.factory import UUID


class Version(Enum):
    VERSION_UNKNOWN = 0
    VERSION_RANDOM_BASED = 4
    VERSION_TIME_ORDERED = 6
    VERSION_UPROTOCOL = 8

    @staticmethod
    def getVersion(value):
        for version in Version:
            if version.value == value:
                return version
        return None


class UUIDUtils:
    @staticmethod
    def toString(uuid_obj: UUID) -> str:
        return str(uuid_obj) if uuid_obj is not None else None

    @staticmethod
    def toBytes(uuid_obj: UUID) -> Optional[bytes]:
        if uuid_obj is None:
            return None
        uuid_bytes = uuid_obj.bytes
        return uuid_bytes

    @staticmethod
    def fromBytes(bytes_list: bytes) -> Optional[UUID]:
        if bytes_list is None or len(bytes_list) != 16:
            return None
        uuid_bytes = bytes(bytes_list)
        return uuid.UUID(bytes=uuid_bytes)

    @staticmethod
    def fromString(string: str) -> Optional[UUID]:
        try:
            return uuid.UUID(string)
        except ValueError:
            return None

    @staticmethod
    def getVersion(uuid_obj: UUID) -> Optional[Version]:
        if uuid_obj is None:
            return None
        return Version.getVersion(uuid_obj.version)

    @staticmethod
    def getVariant(uuid_obj: UUID) -> Optional[str]:
        if uuid_obj is None:
            return None
        return uuid_obj.variant

    @staticmethod
    def isUProtocol(uuid_obj: UUID) -> bool:
        return UUIDUtils.getVersion(uuid_obj) == Version.VERSION_UPROTOCOL if uuid_obj is not None else False

    @staticmethod
    def isUuidv6(uuid_obj: UUID) -> bool:
        if uuid_obj is None:
            return False
        return UUIDUtils.getVersion(uuid_obj) == Version.VERSION_TIME_ORDERED and UUIDUtils.getVariant(
            uuid_obj) == uuid.RFC_4122 if uuid_obj is not None else False

    @staticmethod
    def isuuid(uuid_obj: UUID) -> bool:
        return UUIDUtils.isUProtocol(uuid_obj) or UUIDUtils.isUuidv6(uuid_obj) if uuid_obj is not None else False

    @staticmethod
    def getTime(uuid: UUID):
        time = None
        version = UUIDUtils.getVersion(uuid)
        if uuid is None or version is None:
            return None

        if version == Version.VERSION_UPROTOCOL:
            time = uuid.int >> 16
        elif version == Version.VERSION_TIME_ORDERED:
            try:
                # Convert 100-nanoseconds ticks to milliseconds
                time = uuid.time // 10000
            except ValueError:
                return None

        return time
