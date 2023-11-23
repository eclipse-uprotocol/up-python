# -------------------------------------------------------------------------

# Copyright (c) 2023 General Motors GTO LLC
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
# SPDX-FileCopyrightText: 2023 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0

# -------------------------------------------------------------------------


import uuid
from datetime import datetime
from enum import Enum
from typing import Optional


from org_eclipse_uprotocol.proto.uuid_pb2 import UUID
from org_eclipse_uprotocol.uuid.factory import PythonUUID


class Version(Enum):
    """
    UUID Version
    """
    VERSION_UNKNOWN = 0  # An unknown version.
    VERSION_RANDOM_BASED = 4  # The randomly or pseudo-randomly generated version specified in RFC-4122.
    VERSION_TIME_ORDERED = 6  # The time-ordered version with gregorian epoch proposed by Peabody and Davis.
    VERSION_UPROTOCOL = 8  # The custom or free-form version proposed by Peabody and Davis.

    @staticmethod
    def getVersion(value: int):
        """
        Get the Version from the passed integer representation of the version.<br><br>
        @param value:The integer representation of the version.
        @return:The Version object or Optional.empty() if the value is not a valid version.
        """
        for version in Version:
            if version.value == value:
                return version
        return None


class UUIDUtils:
    """
    UUID Utils class that provides utility methods for uProtocol IDs
    """

    @staticmethod
    def getVersion(uuid_obj: UUID) -> Optional[Version]:
        """
        Fetch the UUID version.<br><br>
        @param uuid_obj:The UUID to fetch the version from.
        @return: Return the UUID version from the UUID object or Optional.empty() if the uuid is null.
        """
        if uuid_obj is None:
            return None

        return Version.getVersion((uuid_obj.msb >> 12) & 0x0f)


    @staticmethod
    def getVariant(uuid_obj: UUID) -> Optional[str]:
        """
        Fetch the Variant from the passed UUID.<br><br>
        @param uuid_obj:The UUID to fetch the variant from.
        @return:UUID variant or Empty if uuid is null.
        """
        if uuid_obj is None:
            return None
        python_uuid = UUIDUtils.create_pythonuuid_from_eclipseuuid(uuid_obj)

        return python_uuid.variant

    @staticmethod
    def isUProtocol(uuid_obj: UUID) -> bool:
        """
        Verify if version is a formal UUIDv8 uProtocol ID.<br><br>
        @param uuid_obj:UUID object
        @return:true if is a uProtocol UUID or false if uuid passed is null or the UUID is not uProtocol format.
        """

        return UUIDUtils.getVersion(uuid_obj) == Version.VERSION_UPROTOCOL if uuid_obj is not None else False

    @staticmethod
    def isUuidv6(uuid_obj: UUID) -> bool:
        """
        Verify if version is UUIDv6<br><br>
        @param uuid_obj:UUID object
        @return:true if is UUID version 6 or false if uuid is null or not version 6
        """
        if uuid_obj is None:
            return False

        return UUIDUtils.getVersion(uuid_obj) == Version.VERSION_TIME_ORDERED and UUIDUtils.getVariant(
            uuid_obj) == uuid.RFC_4122 if uuid_obj is not None else False

    @staticmethod
    def isuuid(uuid_obj: UUID) -> bool:
        """
        Verify uuid is either v6 or v8<br><br>
        @param uuid_obj: UUID object
        @return:true if is UUID version 6 or 8
        """

        return UUIDUtils.isUProtocol(uuid_obj) or UUIDUtils.isUuidv6(uuid_obj) if uuid_obj is not None else False

    @staticmethod
    def getTime(uuid: UUID):
        """
        Return the number of milliseconds since unix epoch from a passed UUID.<br><br>
        @param uuid:passed uuid to fetch the time.
        @return:number of milliseconds since unix epoch or empty if uuid is null.
        """
        time = None
        version = UUIDUtils.getVersion(uuid)
        if uuid is None or version is None:
            return None

        if version == Version.VERSION_UPROTOCOL:
            time = uuid.msb >> 16
        elif version == Version.VERSION_TIME_ORDERED:
            try:
                python_uuid = UUIDUtils.create_pythonuuid_from_eclipseuuid(uuid)
                # Convert 100-nanoseconds ticks to milliseconds
                time = python_uuid.time // 10000
            except ValueError:
                return None

        return time

    @staticmethod
    def get_msb_lsb(uuid: PythonUUID):
        # Convert UUID to a 128-bit integer
        uuid_int = int(uuid)

        # Extract most significant bits (first 64 bits)
        msb = uuid_int >> 64

        # Extract least significant bits (last 64 bits)
        lsb = uuid_int & ((1 << 64) - 1)

        return msb, lsb

    @staticmethod
    def create_pythonuuid_from_eclipseuuid(uuid:UUID) -> PythonUUID:
        combined_int = (uuid.msb << 64) + uuid.lsb
        return PythonUUID(int=combined_int)
        # from org_eclipse_uprotocol.uuid.serializer.longuuidserializer import LongUuidSerializer
        # return PythonUUID(hex=LongUuidSerializer.instance().serialize(uuid))
