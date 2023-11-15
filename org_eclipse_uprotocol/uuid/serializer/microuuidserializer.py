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


import struct

from org_eclipse_uprotocol.proto.uuid_pb2 import UUID
from org_eclipse_uprotocol.uuid.factory.uuidutils import UUIDUtils
from org_eclipse_uprotocol.uuid.serializer.uuidserializer import UuidSerializer


class MicroUuidSerializer(UuidSerializer):
    """
    UUID Serializer implementation used to serialize/deserialize UUIDs to/from bytes
    """

    @staticmethod
    def instance():
        return MicroUuidSerializer()

    def deserialize(self, uuid_bytes: bytes) -> UUID:
        """
        Deserialize from the bytes format to a UUID.
        :param uuid_bytes: Serialized UUID in bytes format.
        :return: Returns a UUID object from the serialized format from the wire.
        """
        if not uuid_bytes or len(uuid_bytes) != 16:
            return UUID()  # Return default UUID if bytes are empty or not 16 bytes

        msb, lsb = struct.unpack('>QQ', uuid_bytes)
        return UUID(msb=msb, lsb=lsb)

    def serialize(self, uuid: UUID) -> bytes:
        """
        Serialize from a UUID to bytes format.
        :param uuid: UUID object to be serialized to bytes.
        :return: Returns the UUID in the bytes serialized format.
        """
        if uuid is None:
            return b'\x00' * 16  # Return 16 zero bytes for a None UUID
        pythonuuid = UUIDUtils.create_pythonuuid_from_msb_lsb(uuid.msb, uuid.lsb)
        msb, lsb = divmod(pythonuuid.int, 2 ** 64)
        return struct.pack('>QQ', msb, lsb)
