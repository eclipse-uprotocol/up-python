"""
SPDX-FileCopyrightText: 2023 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

from uprotocol.uuid.factory import PythonUUID
from uprotocol.uuid.factory.uuidutils import UUIDUtils
from uprotocol.v1.uuid_pb2 import UUID


class UuidSerializer:
    """
    UUID Serializer interface used to serialize/deserialize UUIDs
    to/from either Long (string) or micro (bytes) form
    """

    @staticmethod
    def deserialize(string_uuid: Optional[str]) -> UUID:
        """
        Deserialize from the string format to a UUID.
        :param string_uuid: Serialized UUID in string format.
        :return: Returns a UUID object from the serialized format from the
        wire.
        """
        if not string_uuid or string_uuid.isspace():
            return UUID()  # Return default UUID if string is empty or whitespace
        try:
            msb, lsb = UUIDUtils.get_msb_lsb(PythonUUID(string_uuid))
            return UUID(msb=msb, lsb=lsb)
        except ValueError:
            return UUID()  # Return default UUID in case of parsing failure

    @staticmethod
    def serialize(uuid: UUID) -> str:
        """
        Serialize from a UUID to a string format.
        :param uuid: UUID object to be serialized to a string.
        :return: Returns the UUID in the string serialized format.
        """
        if uuid is None:
            return ""

        pythonuuid = UUIDUtils.create_pythonuuid_from_eclipseuuid(uuid)
        return str(pythonuuid) if uuid else ""
