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

from abc import ABC, abstractmethod
from re import T

from uprotocol.proto.uri_pb2 import UUri


class UriSerializer(ABC):
    """
    UUris are used in transport layers and hence need to be serialized.<br>
    Each transport supports different
    serialization formats.
    """

    @abstractmethod
    def deserialize(self, uri: T) -> UUri:
        """
        Deserialize from the format to a UUri.<br><br>
        @param uri:serialized UUri.
        @return:Returns a UUri object from the serialized format from the wire.
        """
        pass

    @abstractmethod
    def serialize(self, uri: UUri) -> T:
        """
        Serialize from a UUri to a specific serialization format.<br><br>
        @param uri:UUri object to be serialized to the format T.
        @return:Returns the UUri in the transport serialized format.
        """
        pass
