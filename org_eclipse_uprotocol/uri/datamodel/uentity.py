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
class UEntity:
    """
    Data representation of an <b> Software Entity - uE</b><br>Software entities are distinguished by using a unique
    name or a unique id along with the specific version of the software.<br>An Software Entity is a piece of software
    deployed somewhere on a uDevice.<br>The Software Entity is used in the source and sink parts of communicating
    software.<br>A uE that publishes events is a <b>Service</b> role.<br>A uE that consumes events is an
    <b>Application</b> role.
    """
    EMPTY = None

    def __init__(self, name: str, version: int, identifier: int, marked_resolved: bool):
        """
        Build a Software Entity that represents a communicating piece of software.<br><br>
        @param name:The name of the software such as petapp or body.access.
        @param version:The software version. If not supplied, the latest version of the service will be used.
        @param identifier:A numeric identifier for the software entity which is a one-to-one correspondence with the
        software name.
        @param marked_resolved:Indicates that this uResource was populated with intent of having all data.
        """
        if name is None:
            raise ValueError("Software Entity must have a name")
        self.name = name
        self.version = version
        self.id = identifier
        self.marked_resolved = marked_resolved

    @staticmethod
    def resolved_format(name: str, version: int, identifier: int):
        """
        Create a complete UEntity with all the information so that it can be used in long form UUri serialisation and
        micro form UUri serialisation.<br>In the case of missing elements such as name or id, the UEntity will not be
        marked as resolvable and will not be usable in serialisation formats.<br><br>
        @param name:The name of the software such as petapp or body.access.
        @param version:The software version. If not supplied, the latest version of the service will be used.
        @param identifier:A numeric identifier for the software entity which is a one-to-one correspondence with the
        software name.
        @return:Returns a complete UEntity with all the information so that it can be used in long form UUri
        serialisation and micro form UUri serialisation.
        """
        resolved = name and name.strip() and identifier is not None
        return UEntity(name if name else "", version, identifier, resolved)

    @staticmethod
    def long_format(name: str, version: int):
        """
        Static factory method for creating a uE using the software entity name, that can be used in long form UUri
        serialisation.<br><br>
        @param name:The software entity name, such as petapp or body.access.
        @param version:The software entity version.
        @return:Returns an UEntity with the name and the version of the service and can only be serialized to long
        UUri format.
        """
        return UEntity(name if name else "", version, None, False)

    @staticmethod
    def long_format_name(name: str):
        """
        Static factory method for creating a uE using the software entity name, that can be used in long form UUri
        serialisation.<br><br>
        @param name:The software entity name, such as petapp or body.access.
        @return:Returns an UEntity with the name where the version is the latest version of the service and can only
        be serialized to long UUri format.
        """
        return UEntity(name if name else "", None, None, False)

    @staticmethod
    def micro_format(identifier: int):
        """
        Static factory method for creating a uE using the software entity identification number, that can be used to
        serialize micro UUris.<br><br>
        @param identifier: numeric identifier for the software entity which is a one-to-one correspondence with the
        software name.
        @return:Returns an UEntity with the name where the version is the latest version of the service and can only
        be serialized to long micro UUri format.
        """
        return UEntity("", None, identifier, False)

    @staticmethod
    def micro_format_id_version(identifier: int, version: int):
        """
        Static factory method for creating a uE using the software entity identification number, that can be used to
        serialize micro UUris.<br><br>
        @param identifier:A numeric identifier for the software entity which is a one-to-one correspondence with the
        software name.
        @param version:The software entity version.
        @return:Returns an UEntity with the name and the version of the service and can only be serialized to micro
        UUri format.
        """
        return UEntity("", version, identifier, False)

    @staticmethod
    def empty():
        """
        Static factory method for creating an empty software entity, to avoid working with null<br><br>
        @return:Returns an empty software entity that has a blank name, no unique id and no version information.
        """
        if UEntity.EMPTY is None:
            UEntity.EMPTY = UEntity("", None, None, False)
        return UEntity.EMPTY

    def is_empty(self) -> bool:
        """
        Indicates that this software entity is an empty container and has no valuable information in building
        uProtocol sinks or sources.<br><br>
        @return: Returns true if this software entity is an empty container and has no valuable information in
        building uProtocol sinks or sources.
        """
        return not (self.name or self.version or self.id)

    def is_resolved(self) -> bool:
        """
        Return true if the UEntity contains both the name and IDs meaning it contains all the information to be
        serialized into a long UUri or a micro form UUri.<br><br>
        @return:Returns true of this resource contains resolved information meaning it contains all the information
        to be serialized into a long UUri or a micro form UUri.
        """
        return self.marked_resolved

    def is_long_form(self) -> bool:
        """
        Determine if this software entity can be serialised into a long UUri form.<br><br>
        @return:Returns true if this software entity can be serialised into a long UUri form, meaning it has at least
        a name.
        """
        return bool(self.name)

    def is_micro_form(self) -> bool:
        """
        Returns true if the Uri part contains the id's which will allow the Uri part to be serialized into micro
        form.<br><br>
        @return:Returns true if the Uri part can be serialized into micro form, meaning is has at least a unique
        numeric identifier.
        """
        return self.id is not None

    def get_name(self) -> str:
        """
        Returns the name of the software.<br><br>
        @return: Returns the name of the software such as petpp or body.access.
        """
        return self.name

    def get_version(self) -> int:
        """
        Returns the software version if it exists.<br><br>
        @return:Returns the software version if it exists. If the version does not exist, the latest version of the
        service will be used.
        """
        return self.version

    def get_id(self) -> int:
        """
        Returns the software id if it exists. The software id represents the numeric identifier of the uE.<br><br>
        @return: Returns the software id if it exists. The software id represents the numeric identifier of the uE.
        """
        return self.id

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, UEntity):
            return False
        return (
                self.marked_resolved == other.marked_resolved and self.name == other.name and self.version ==
                other.version and self.id == other.id)

    def __hash__(self):
        return hash((self.name, self.version, self.id, self.marked_resolved))

    def __str__(self):
        return (f"UEntity{{name='{self.name}', version={self.version}, id={self.id}, markedResolved="
                f"{self.marked_resolved}}}")


# Initialize EMPTY
UEntity.EMPTY = UEntity("", None, None, False)
