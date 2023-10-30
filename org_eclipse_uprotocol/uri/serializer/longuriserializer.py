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

import re

from org_eclipse_uprotocol.proto.uri_pb2 import UUri
from org_eclipse_uprotocol.proto.uri_pb2 import UAuthority
from org_eclipse_uprotocol.proto.uri_pb2 import UResource
from org_eclipse_uprotocol.proto.uri_pb2 import UEntity



from org_eclipse_uprotocol.uri.factory.uauthority_factory import UAuthorityFactory
from org_eclipse_uprotocol.uri.factory.uentity_factory import UEntityFactory
from org_eclipse_uprotocol.uri.factory.uresource_factory import UResourceFactory
from org_eclipse_uprotocol.uri.factory.uuri_factory import UUriFactory

from org_eclipse_uprotocol.uri.serializer.uriserializer import UriSerializer


class LongUriSerializer(UriSerializer):
    """
    UUri Serializer that serializes a UUri to a long format string per
    <a href=https://github.com/eclipse-uprotocol/uprotocol-spec/blob/main/basics/uri.adoc>
    https://github.com/eclipse-uprotocol/uprotocol-spec/blob/main/basics/uri.adoc</a>
    """

    def serialize(self, uri: UUri) -> str:
        """
        Support for serializing {@link UUri} objects into their String format.<br><br>
        @param uri: UUri object to be serialized to the String format.
        @return:Returns the String format of the supplied UUri that can be used as a sink or a source in a
        uProtocol publish communication.
        """
        if uri is None or UUriFactory.is_empty(uri):
            return ""

        sb = []

        sb.append(self.build_authority_part_of_uri(uri.authority))

        if not UAuthorityFactory.is_local(uri.authority):
            sb.append("/")

        if UEntityFactory.is_empty(uri.entity):
            return "".join(sb)

        sb.append(self.build_software_entity_part_of_uri(uri.entity))

        sb.append(self.build_resource_part_of_uri(uri.resource))

        return re.sub('/+$', '', "".join(sb))

    @staticmethod
    def build_resource_part_of_uri(res: UResource) -> str:
        if UResourceFactory.is_empty(res):
            return ""

        sb = ["/", res.name]

        if res.instance:
            sb.append("." + res.instance)

        if res.message:
            sb.append("#" + res.message)

        return "".join(sb)

    @staticmethod
    def build_software_entity_part_of_uri(entity: UEntity) -> str:
        """
        Create the service part of the uProtocol URI from an UEntity object.<br><br>
        @param entity:Software Entity representing a service or an application.
        @return: Returns the String representation of the UEntity in the uProtocol URI.
        """
        sb = [entity.name.strip(), "/"]

        if entity.version_major:
            sb.append(str(entity.version_major))

        return "".join(sb)

    @staticmethod
    def build_authority_part_of_uri(authority: UAuthority) -> str:
        """
        Create the authority part of the uProtocol URI from an UAuthority object.<br><br>
        @param authority:represents the deployment location of a specific  Software Entity in the Ultiverse.
        @return:Returns the String representation of the  Authority in the uProtocol URI.
        """
        if UAuthorityFactory.is_local(authority):
            return "/"

        partial_uri = ["//"]
        maybe_name = authority.name

        if maybe_name:
            partial_uri.append(maybe_name)

        return "".join(partial_uri)

    def deserialize(self, u_protocol_uri: str) -> UUri:
        """
        Deserialize a String into a UUri object.<br><br>
        @param u_protocol_uri:A long format uProtocol URI.
        @return:Returns an UUri data object.
        """
        if u_protocol_uri is None or u_protocol_uri.strip() == "":
            return UUri.empty()

        uri = u_protocol_uri.split(":")[-1].replace('\\', '/')
        is_local = not uri.startswith("//")
        uri_parts = uri.split("/")
        number_of_parts_in_uri = len(uri_parts)

        if number_of_parts_in_uri == 0 or number_of_parts_in_uri == 1:
            if is_local:
                return UUriFactory.empty()
            else:
                return UUriFactory.create_uuri(UAuthority.long_remote("", ""), UEntity.empty(), UResource.empty())

        use_name = uri_parts[1]
        use_version = ""

        if is_local:
            auth = UAuthorityFactory.local()
            if number_of_parts_in_uri > 2:
                use_version = uri_parts[2]
                res = self.parse_from_string(uri_parts[3]) if number_of_parts_in_uri > 3 else UResource.empty()
            else:
                res = UResourceFactory.empty()
        else:
            authority_parts = uri_parts[2].split(".")
            device = authority_parts[0]
            domain = ".".join(authority_parts[1:]) if len(authority_parts) > 1 else ""
            auth = UAuthorityFactory.long_remote(device+domain)

            if number_of_parts_in_uri > 3:
                use_name = uri_parts[3]
                if number_of_parts_in_uri > 4:
                    use_version = uri_parts[4]
                    res = self.parse_from_string(uri_parts[5]) if number_of_parts_in_uri > 5 else UResource.empty()
                else:
                    res = UResourceFactory.empty()
            else:
                return UUriFactory.create_uuri(auth, UEntity.empty(), UResource.empty())

        use_version_int = int(use_version) if use_version.strip() else None

        return UUriFactory.create_uuri(auth, UEntityFactory.long_format(use_name,version_major= use_version_int), res)

    @staticmethod
    def parse_from_string(resource_string: str) -> UResource:
        """
        Static factory method for creating a UResource using a string that contains name + instance + message.<br><br>
        @param resource_string:String that contains the UResource information.
        @return:Returns a UResource object.
        """
        if resource_string is None:
            raise ValueError("Resource must have a command name.")

        parts = resource_string.split("#")
        name_and_instance = parts[0]

        name_and_instance_parts = name_and_instance.split(".")
        resource_name = name_and_instance_parts[0]
        resource_instance = name_and_instance_parts[1] if len(name_and_instance_parts) > 1 else None
        resource_message = parts[1] if len(parts) > 1 else None

        return UResourceFactory.long_format_instance_message(resource_name, resource_instance, resource_message)
