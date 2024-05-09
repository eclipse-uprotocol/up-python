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


import uuid
import time
from enum import Enum
from typing import Optional, Union

from multimethod import multimethod

from uprotocol.proto.uuid_pb2 import UUID
from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.uuid.factory import PythonUUID


class Version(Enum):
    """
    UUID Version
    """

    VERSION_UNKNOWN = 0
    VERSION_RANDOM_BASED = 4
    VERSION_TIME_ORDERED = 6
    VERSION_UPROTOCOL = 8

    @staticmethod
    def get_version(value: int):
        """
        Get the Version from the passed integer representation
        of the version.<br><br>
        @param value:The integer representation of the version.
        @return:The Version object or Optional.empty() if the value
        is not a valid version.
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
    def get_version(uuid_obj: UUID) -> Optional[Version]:
        """
        Fetch the UUID version.<br><br>
        @param uuid_obj:The UUID to fetch the version from.
        @return: Return the UUID version from the UUID object
        or Optional.empty() if the uuid is null.
        """
        if uuid_obj is None:
            return None

        return Version.get_version((uuid_obj.msb >> 12) & 0x0F)

    @staticmethod
    def get_variant(uuid_obj: UUID) -> Optional[str]:
        """
        Fetch the Variant from the passed UUID.<br><br>
        @param uuid_obj:The UUID to fetch the variant from.
        @return:UUID variant or Empty if uuid is null.
        """
        if uuid_obj is None:
            return None
        python_uuid = UUIDUtils.create_pythonuuid_from_eclipseuuid(
            uuid_obj
        )

        return python_uuid.variant

    @staticmethod
    def is_uprotocol(uuid_obj: UUID) -> bool:
        """
        Verify if version is a formal UUIDv8 uProtocol ID.<br><br>
        @param uuid_obj:UUID object
        @return:true if is a uProtocol UUID or false if uuid
        passed is null or the UUID is not uProtocol format.
        """

        return (
            UUIDUtils.get_version(uuid_obj)
            == Version.VERSION_UPROTOCOL
            if uuid_obj is not None
            else False
        )

    @staticmethod
    def is_uuidv6(uuid_obj: UUID) -> bool:
        """
        Verify if version is UUIDv6<br><br>
        @param uuid_obj:UUID object
        @return:true if is UUID version 6 or false if uuid
        is null or not version 6
        """
        if uuid_obj is None:
            return False

        return (
            UUIDUtils.get_version(uuid_obj)
            == Version.VERSION_TIME_ORDERED
            and UUIDUtils.get_variant(uuid_obj) == uuid.RFC_4122
            if uuid_obj is not None
            else False
        )

    @staticmethod
    def is_uuid(uuid_obj: UUID) -> bool:
        """
        Verify uuid is either v6 or v8<br><br>
        @param uuid_obj: UUID object
        @return:true if is UUID version 6 or 8
        """

        return (
            UUIDUtils.is_uprotocol(uuid_obj)
            or UUIDUtils.is_uuidv6(uuid_obj)
            if uuid_obj is not None
            else False
        )

    @staticmethod
    def get_time(uuid: UUID):
        """
        Return the number of milliseconds since unix epoch from
        a passed UUID.<br><br>
        @param uuid:passed uuid to fetch the time.
        @return:number of milliseconds since unix epoch or
        empty if uuid is null.
        """
        time = None
        version = UUIDUtils.get_version(uuid)
        if uuid is None or version is None:
            return None

        if version == Version.VERSION_UPROTOCOL:
            time = uuid.msb >> 16
        elif version == Version.VERSION_TIME_ORDERED:
            try:
                python_uuid = (
                    UUIDUtils.create_pythonuuid_from_eclipseuuid(uuid)
                )
                # Convert 100-nanoseconds ticks to milliseconds
                time = python_uuid.time // 10000
            except ValueError:
                return None

        return time

    @staticmethod
    def get_elapsed_time(id: UUID):
        """
        Calculates the elapsed time since the creation of the specified UUID.

        @param id The UUID of the object whose creation time
        needs to be determined.
        @return The elapsed time in milliseconds,
        or None if the creation time cannot be determined.
        """
        creation_time = UUIDUtils.get_time(id) or -1
        if creation_time < 0:
            return None
        now = int(time.time() * 1000)
        return now - creation_time if now >= creation_time else None

    @multimethod
    def get_remaining_time(id: Union[UUID, None], ttl: int):
        """
        Calculates the remaining time until the expiration of the event
        identified by the given UUID.

        @param id  The UUID of the object whose remaining time needs to
        be determined.
        @param ttl The time-to-live (TTL) in milliseconds.
        @return The remaining time in milliseconds until the event expires,
        or None if the UUID is null, TTL is non-positive, or the
        creation time cannot be determined.
        """
        if id is None or ttl <= 0:
            return None
        elapsed_time = UUIDUtils.get_elapsed_time(id)
        return ttl - elapsed_time if ttl > elapsed_time else None

    @multimethod
    def get_remaining_time(attributes: Union[UAttributes, None]):
        """
        Calculates the remaining time until the expiration of the event
        identified by the given UAttributes.
        @param attributes The attributes containing information about
        the event, including its ID and TTL.
        @return The remaining time in milliseconds until the event expires,
        or None if the attributes do not contain TTL information or the
        creation time cannot be determined.
        """
        return (
            UUIDUtils.get_remaining_time(
                attributes.id, attributes.ttl
            )
            if attributes.HasField("ttl")
            else None
        )

    @multimethod
    def is_expired(id: Union[UUID, None], ttl: int):
        """
        Checks if the event identified by the given UUID has expired based
        on the specified time-to-live (TTL).

        @param id  The UUID identifying the event.
        @param ttl The time-to-live (TTL) in milliseconds for the event.
        @return true if the event has expired, false otherwise. Returns false
        if TTL is non-positive or creation time
        cannot be determined.
        """
        return (
            ttl > 0 and UUIDUtils.get_remaining_time(id, ttl) is None
        )

    @multimethod
    def is_expired(attributes: Union[UAttributes, None]):
        """
        Checks if the event identified by the given UAttributes has expired.

        @param attributes The attributes containing information about the
        event, including its ID and TTL.
        @return true if the event has expired, false otherwise.Returns false
        if the attributes do not contain TTL
        information or creation time cannot be determined.
        """
        return attributes.HasField("ttl") and UUIDUtils.is_expired(
            attributes.id, attributes.ttl
        )

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
    def create_pythonuuid_from_eclipseuuid(uuid: UUID) -> PythonUUID:
        combined_int = (uuid.msb << 64) + uuid.lsb
        return PythonUUID(int=combined_int)
