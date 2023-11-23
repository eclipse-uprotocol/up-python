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


from org_eclipse_uprotocol.proto.uuid_pb2 import UUID
from org_eclipse_uprotocol.uuid.factory import PythonUUID
from org_eclipse_uprotocol.uuid.factory.uuidutils import UUIDUtils
from org_eclipse_uprotocol.uuid.serializer.uuidserializer import UuidSerializer


class LongUuidSerializer(UuidSerializer):
    """
    UUID Serializer implementation used to serialize/deserialize UUIDs to/from a string
    """

    @staticmethod
    def instance():
        return LongUuidSerializer()

    def deserialize(self, string_uuid: str) -> UUID:
        """
        Deserialize from the string format to a UUID.
        :param string_uuid: Serialized UUID in string format.
        :return: Returns a UUID object from the serialized format from the wire.
        """
        if not string_uuid or string_uuid.isspace():
            return UUID()  # Return default UUID if string is empty or whitespace
        try:
            msb, lsb = UUIDUtils.get_msb_lsb(PythonUUID(string_uuid))
            return UUID(msb=msb, lsb=lsb)
        except ValueError:
            return UUID()  # Return default UUID in case of parsing failure

    def serialize(self, uuid: UUID) -> str:
        """
        Serialize from a UUID to a string format.
        :param uuid: UUID object to be serialized to a string.
        :return: Returns the UUID in the string serialized format.
        """
        if uuid is None:
            return ''

        pythonuuid = UUIDUtils.create_pythonuuid_from_eclipseuuid(uuid)
        return str(pythonuuid) if uuid else ''
