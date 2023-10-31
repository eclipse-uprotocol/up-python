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


from org_eclipse_uprotocol.proto.uri_pb2 import UEntity


class UEntityFactory:
    """
    A factory is a part of the software that has methods to generate concrete objects, usually of the same type.<br>
    Data representation of an <b> Software Entity - uE</b><br>Software entities are distinguished by using a unique
    name or a unique id along with the specific version of the software.<br>An Software Entity is a piece of software
    deployed somewhere on a uDevice.<br>The Software Entity is used in the source and sink parts of communicating
    software.<br>A uE that publishes events is a <b>Service</b> role.<br>A uE that consumes events is an
    <b>Application</b> role.<br> The UEntity Factory knows how to generate UEntity proto message.<br>
    """

    @staticmethod
    def long_format(name: str, version_minor: int = 0, version_major: int = 0) -> UEntity:
        """
        Static factory method for creating a uE using the software entity name, that can be used in long form UUri
        serialisation.<br><br>
        @param name:The software entity name, such as petapp or body.access.
        @param version_minor:minor version of the uEntity
        @param version_major:major version of the uEntity
        @return:Returns an UEntity with the name and the version of the service and can only be serialized to long
        UUri format.
        """
        entity = UEntity(name=name if name else "")
        if version_minor != 0 and version_minor is not None:
            entity.version_minor = version_minor
        if version_major != 0 and version_major is not None:
            entity.version_major = version_major
        return entity

    @staticmethod
    def long_format_name(name: str) -> UEntity:
        """
        Static factory method for creating a uE using the software entity name, that can be used in long form UUri
        serialisation.<br><br>
        @param name:The software entity name, such as petapp or body.access.
        @return:Returns an UEntity with the name where the version is the latest version of the service and can only
        be serialized to long UUri format.
        """
        return UEntity(name=name if name else "")

    @staticmethod
    def micro_format(identifier: int) -> UEntity:
        """
        Static factory method for creating a uE using the software entity identification number, that can be used to
        serialize micro UUris.<br><br>
        @param identifier: numeric identifier for the software entity which is a one-to-one correspondence with the
        software name.
        @return:Returns an UEntity with the name where the version is the latest version of the service and can only
        be serialized to long micro UUri format.
        """
        entity = UEntity()
        if identifier is not None and identifier != 0:
            entity.id = identifier
        return entity

    @staticmethod
    def micro_format_id_version(identifier: int, version_major: int, version_minor: int):
        """
        Static factory method for creating a uE using the software entity identification number, that can be used to
        serialize micro UUris.<br><br>
        @param identifier:A numeric identifier for the software entity which is a one-to-one correspondence with the
        software name.
        @param version_major:major version of the uEntity
        @return:Returns an UEntity with the name and the version of the service and can only be serialized to micro
        UUri format.
        """
        entity = UEntity()
        if identifier is not None and identifier != 0:
            entity.id = identifier
        if version_major is not None and version_major != 0:
            entity.version_major = version_major
        if version_minor is not None and version_minor != 0:
            entity.version_minor = version_minor
        return entity

    @staticmethod
    def empty():
        """
        Static factory method for creating an empty software entity, to avoid working with null<br><br>
        @return:Returns an empty software entity that has a blank name, no unique id and no version information.
        """
        return UEntity()

    @staticmethod
    def is_empty(uentity: UEntity) -> bool:
        """
        Indicates that this software entity is an empty container and has no valuable information in building
        uProtocol sinks or sources.<br><br>
        @param uentity: UEntity protobuf message
        @return: Returns true if this software entity is an empty container and has no valuable information in
        building uProtocol sinks or sources.
        """
        return (
                uentity.name.strip() == "" and uentity.version_major == 0 and uentity.id == 0 and
                uentity.version_minor == 0)

    @staticmethod
    def is_long_form(uentity: UEntity) -> bool:
        """
        Determine if this software entity can be serialised into a long UUri form.<br><br>
        @param uentity: UEntity protobuf message
        @return:Returns true if this software entity can be serialised into a long UUri form, meaning it has at least
        a name.
        """
        return bool(uentity.name)

    @staticmethod
    def is_micro_form(uentity: UEntity) -> bool:
        """
        Returns true if the Uri part contains the id's which will allow the Uri part to be serialized into micro
        form.<br><br>
        @param uentity: UEntity protobuf message
        @return:Returns true if the Uri part can be serialized into micro form, meaning is has at least a unique
        numeric identifier.
        """
        return uentity.id != 0

    @staticmethod
    def resolved_format(name: str, version_major: int, version_minor: int, identifier: int):
        """
        Create a complete UEntity with all the information so that it can be used in long form UUri serialisation and
        micro form UUri serialisation.<br>In the case of missing elements such as name or id, the UEntity will not be
        marked as resolvable and will not be usable in serialisation formats.<br><br>
        @param name:The name of the software such as petapp or body.access.
        @param version_major:The software major version. If not supplied, the latest version of the service will be
        used.
        @param version_minor:The software minor version.
        @param identifier:A numeric identifier for the software entity which is a one-to-one correspondence with the
        software name.
        @return:Returns a complete UEntity with all the information so that it can be used in long form UUri
        serialisation and micro form UUri serialisation.
        """
        return UEntity(name if name else "", version_major if version_major else 0,
                       version_minor if version_minor else 0, identifier if identifier else 0)
