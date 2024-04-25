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

from uprotocol.proto.uri_pb2 import UAuthority
from uprotocol.proto.uri_pb2 import UEntity
from uprotocol.proto.uri_pb2 import UResource
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.uri.validator.urivalidator import UriValidator


class LongUriSerializer(UriSerializer):
    """
    UUri Serializer that serializes a UUri to a long format string per
    <a href=https://github.com/eclipse-uprotocol/uprotocol-spec/blob/main/basics/uri.adoc>
    https://github.com/eclipse-uprotocol/uprotocol-spec/blob/main/basics/uri.adoc</a>
    """

    def serialize(self, uri: UUri) -> str:
        """
        Support for serializing UUri objects into their String format.<br><br>
        @param uri: UUri object to be serialized to the String format.
        @return:Returns the String format of the supplied UUri that can be
        used as a sink or a source in a
        uProtocol publish communication.
        """
        if uri is None or UriValidator.is_empty(uri):
            return ""

        sb = []

        if (
            uri.HasField("authority")
            and uri.authority.HasField("name")
            and not uri.authority.name.strip() == ""
        ):
            sb.append("//")
            sb.append(uri.authority.name)

        sb.append("/")

        sb.append(self.build_software_entity_part_of_uri(uri.entity))
        sb.append(self.build_resource_part_of_uri(uri))

        return re.sub("/+$", "", "".join(sb))

    @staticmethod
    def build_resource_part_of_uri(uuri: UUri) -> str:

        if not uuri.HasField("resource"):
            return ""
        u_resource = uuri.resource

        sb = "/" + u_resource.name

        if (
            u_resource.instance is not None
            and not u_resource.instance.strip() == ""
        ):
            sb += "." + u_resource.instance
        if (
            u_resource.message is not None
            and not u_resource.message.strip() == ""
        ):
            sb += "#" + u_resource.message

        return sb

    @staticmethod
    def build_software_entity_part_of_uri(entity: UEntity) -> str:
        """
        Create the service part of the uProtocol URI from an
        UEntity object.<br><br>
        @param entity:Software Entity representing a service
        or an application.
        @return: Returns the String representation of the UEntity
        in the uProtocol URI.
        """
        sb = str(entity.name.strip())
        sb += "/"

        if entity.version_major > 0:
            sb += str(entity.version_major)

        return sb

    def deserialize(self, u_protocol_uri: str) -> UUri:
        """
        Deserialize a String into a UUri object.<br><br>
        @param u_protocol_uri:A long format uProtocol URI.
        @return:Returns an UUri data object.
        """
        if u_protocol_uri is None or u_protocol_uri.strip() == "":
            return UUri()
        uri = (
            u_protocol_uri[u_protocol_uri.index(":") + 1 :]
            if ":" in u_protocol_uri
            else u_protocol_uri.replace("\\", "/")
        )

        is_local = not uri.startswith("//")
        uri_parts = LongUriSerializer.remove_empty(uri.split("/"))
        number_of_parts_in_uri = len(uri_parts)

        if number_of_parts_in_uri == 0 or number_of_parts_in_uri == 1:
            return UUri()

        use_name = ""
        use_version = ""
        u_resource = None
        u_authority = None

        if is_local:
            use_name = uri_parts[1]
            if number_of_parts_in_uri > 2:
                use_version = uri_parts[2]
                if number_of_parts_in_uri > 3:
                    u_resource = self.parse_from_string(uri_parts[3])

        else:
            if uri_parts[2].strip() == "":
                return UUri()
            u_authority = UAuthority(name=uri_parts[2])
            if len(uri_parts) > 3:
                use_name = uri_parts[3]
                if number_of_parts_in_uri > 4:
                    use_version = uri_parts[4]
                    if number_of_parts_in_uri > 5:
                        u_resource = self.parse_from_string(uri_parts[5])
            else:
                return UUri(authority=u_authority)

        use_version_int = None
        try:
            if use_version.strip() != "":
                use_version_int = int(use_version)
        except ValueError:
            return UUri()

        u_entity_builder = UEntity(name=use_name)
        if use_version_int is not None:
            u_entity_builder.version_major = use_version_int

        new_uri = UUri(entity=u_entity_builder)
        if u_authority is not None:
            new_uri.authority.CopyFrom(u_authority)

        if u_resource is not None:
            new_uri.resource.CopyFrom(u_resource)

        return new_uri

    @staticmethod
    def parse_from_string(resource_string: str) -> UResource:
        """
        Static builder method for creating a UResource using a string
        that contains name + instance + message.<br><br>
        @param resource_string:String that contains the UResource information.
        @return:Returns a UResource object.
        """
        if resource_string is None or resource_string.strip() == "":
            raise ValueError("Resource must have a command name.")

        parts = LongUriSerializer.remove_empty(resource_string.split("#"))
        name_and_instance = parts[0]

        name_and_instance_parts = LongUriSerializer.remove_empty(
            name_and_instance.split(".")
        )
        resource_name = name_and_instance_parts[0]
        resource_instance = (
            name_and_instance_parts[1]
            if len(name_and_instance_parts) > 1
            else None
        )
        resource_message = parts[1] if len(parts) > 1 else None

        u_resource = UResource(name=resource_name)
        if resource_instance is not None:
            u_resource.instance = resource_instance
        if resource_message is not None:
            u_resource.message = resource_message
        if (
            "rpc" in resource_name
            and resource_instance is not None
            and "response" in resource_instance
        ):
            u_resource.id = 0

        return u_resource

    @staticmethod
    def remove_empty(parts):
        result = parts[:]

        # Iterate through the list in reverse and remove empty strings
        while result and result[-1] == "":
            result.pop()

        return result
