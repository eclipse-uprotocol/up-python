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


from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from uprotocol.proto.uuid_pb2 import UUID

T = TypeVar('T')


class UuidSerializer(ABC, Generic[T]):
    """
    UUID Serializer interface used to serialize/deserialize UUIDs to/from either Long (string) or micro (bytes) form
    """

    @abstractmethod
    def deserialize(self, uuid: T) -> UUID:
        """
        Deserialize from the format to a UUID.
        :param uuid: Serialized UUID.
        :return: Returns a UUID object from the serialized format from the wire.
        """
        pass  # Implement your deserialization logic here

    @abstractmethod
    def serialize(self, uuid: UUID) -> T:
        """
        Serialize from a UUID to a specific serialization format.
        :param uuid: UUID object to be serialized to the format T.
        :return: Returns the UUID in the transport serialized format.
        """
        pass  # Implement your serialization logic here
