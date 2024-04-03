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

import re
import socket
from typing import List

from uprotocol.proto.uri_pb2 import UUri, UAuthority, UEntity
from uprotocol.proto.uri_pb2 import UResource

from uprotocol.uri.serializer.ipaddress import IpAddress
from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.uri.factory.uresource_builder import UResourceBuilder


def convert_packed_ipaddr_to_string(packed_ipaddr: bytes):
    for address_type in [socket.AF_INET, socket.AF_INET6]:
        try:
            """
            socket.inet_ntop():
            Convert a packed IP address (a bytes-like object
            of some number of bytes)
            to its standard, family-specific string representation
            (for example, '7.10.0.5' or '5aef:2b::8')
            """
            return socket.inet_ntop(address_type, packed_ipaddr)
        except ValueError:
            pass

    raise Exception(
        "Could not find correct address family to unpack ip address",
        "from bytes to str",
    )


class ShortUriSerializer(UriSerializer):
    """
    UUri Serializer that serializes a UUri to a Short format string.
    """

    def serialize(self, uri: UUri) -> str:
        if uri is None or UriValidator.is_empty(uri):
            return ""
        string_builder: List[str] = []

        if uri.HasField("authority"):
            authority: UAuthority = uri.authority
            if uri.authority.HasField("ip"):
                try:
                    string_builder.append("//")
                    string_builder.append(
                        convert_packed_ipaddr_to_string(authority.ip)
                    )
                except Exception:
                    print("in exception")
                    return ""
            elif uri.authority.HasField("id"):
                string_builder.append("//")
                string_builder.append(authority.id.decode("utf-8"))
            else:
                return ""

        string_builder.append("/")
        string_builder.append(
            self.build_software_entity_part_of_uri(uri.entity)
        )
        string_builder.append(self.build_resource_part_of_uri(uri))

        return re.sub("/+$", "", "".join(string_builder))

    @staticmethod
    def build_resource_part_of_uri(uri: UUri):
        if not uri.HasField("resource"):
            return ""
        resource: UResource = uri.resource

        string_builder: List[str] = ["/"]
        string_builder.append(str(resource.id))

        return "".join(string_builder)

    @staticmethod
    def build_software_entity_part_of_uri(entity):
        """
        Create the service part of the uProtocol URI from a
        software entity object.
        @param use  Software Entity representing a service or an application.
        """
        string_builder: List[str] = []
        string_builder.append(str(entity.id))
        string_builder.append("/")
        if entity.version_major > 0:
            string_builder.append(str(entity.version_major))

        return "".join(string_builder)

    def deserialize(self, uprotocol_uri: str) -> UUri:
        """
        Deserialize a String into a UUri object.
        @param uProtocolUri A short format uProtocol URI.
        @return Returns an UUri data object.
        """
        if uprotocol_uri is None or uprotocol_uri.strip() == "":
            return UUri()

        uri = (
            uprotocol_uri[uprotocol_uri.index(":") + 1:]
            if ":" in uprotocol_uri
            else uprotocol_uri.replace("\\", "/")
        )

        is_local = not uri.startswith("//")

        uri_parts = uri.split("/")
        number_of_parts_in_uri = len(uri_parts)

        if number_of_parts_in_uri < 2:
            return UUri()

        ue_id = ""
        ue_version = ""

        resource = None
        authority = None

        if is_local:
            ue_id = uri_parts[1]
            if number_of_parts_in_uri > 2:
                ue_version = uri_parts[2]

                if number_of_parts_in_uri > 3:
                    resource = ShortUriSerializer.parse_from_string(
                        uri_parts[3]
                    )

                if number_of_parts_in_uri > 4:
                    return UUri()
        else:
            if uri_parts[2].strip() == "":
                return UUri()
            if IpAddress.is_valid(uri_parts[2]):
                authority = UAuthority(ip=IpAddress.to_bytes(uri_parts[2]))
            else:
                authority = UAuthority(id=bytes(uri_parts[2], "utf-8"))

            if len(uri_parts) > 3:
                ue_id = uri_parts[3]
                if number_of_parts_in_uri > 4:
                    ue_version = uri_parts[4]
                    if number_of_parts_in_uri > 5:
                        resource = ShortUriSerializer.parse_from_string(
                            uri_parts[5]
                        )
                    if number_of_parts_in_uri > 6:
                        return UUri()
            else:
                return UUri(authority=authority)

        ue_version_int = None
        ue_id_int = None

        try:
            if ue_version.strip() != "":
                ue_version_int = int(ue_version)
            if ue_id.strip() != "":
                ue_id_int = int(ue_id)
        except Exception:
            return UUri()

        entity = UEntity()
        new_uri = UUri()
        if ue_id_int is not None:
            entity.id = ue_id_int
            new_uri.entity.CopyFrom(entity)
        if ue_version_int is not None:
            entity.version_major = ue_version_int
            new_uri.entity.CopyFrom(entity)

        if authority is not None:
            new_uri.authority.CopyFrom(authority)

        if resource is not None:
            new_uri.resource.CopyFrom(resource)

        return new_uri

    @staticmethod
    def parse_from_string(resource_string):
        """
        Static factory method for creating a UResource using a string value
        @param resource_string String that contains the UResource id.
        @return Returns a UResource object.
        """
        if resource_string is None:
            raise ValueError(" Resource must have a command name")
        id = None
        try:
            id = int(resource_string)
        except Exception:
            return UResource()

        return UResourceBuilder.from_id(id)
