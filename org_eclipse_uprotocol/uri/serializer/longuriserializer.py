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

from org_eclipse_uprotocol.uri.datamodel.uauthority import UAuthority
from org_eclipse_uprotocol.uri.datamodel.uentity import UEntity
from org_eclipse_uprotocol.uri.datamodel.uresource import UResource
from org_eclipse_uprotocol.uri.datamodel.uuri import UUri
from org_eclipse_uprotocol.uri.serializer.uriserializer import UriSerializer


class LongUriSerializer(UriSerializer):
    # def __init__(self):
    #     pass
    #
    # @staticmethod
    # def instance():
    #     return LongUriSerializer()

    def serialize(self, uri: UUri) -> str:
        if uri is None or uri.is_empty():
            return ""

        sb = []

        sb.append(self.build_authority_part_of_uri(uri.get_u_authority()))

        if uri.get_u_authority().is_marked_remote():
            sb.append("/")

        if uri.get_u_entity().is_empty():
            return "".join(sb)

        sb.append(self.build_software_entity_part_of_uri(uri.get_u_entity()))

        sb.append(self.build_resource_part_of_uri(uri.get_u_resource()))

        return re.sub('/+$', '', "".join(sb))

    @staticmethod
    def build_resource_part_of_uri(res: UResource) -> str:
        if res.is_empty():
            return ""

        sb = ["/", res.get_name()]

        if res.get_instance():
            sb.append("." + res.get_instance())

        if res.get_message():
            sb.append("#" + res.get_message())

        return "".join(sb)

    @staticmethod
    def build_software_entity_part_of_uri(entity: UEntity) -> str:
        sb = [entity.get_name().strip(), "/"]

        if entity.get_version():
            sb.append(str(entity.get_version()))

        return "".join(sb)

    @staticmethod
    def build_authority_part_of_uri(authority: UAuthority) -> str:
        if authority.is_local():
            return "/"

        partial_uri = ["//"]
        maybe_device = authority.device
        maybe_domain = authority.domain

        if maybe_device:
            partial_uri.append(maybe_device)
            if maybe_domain:
                partial_uri.append(".")

        if maybe_domain:
            partial_uri.append(maybe_domain)

        return "".join(partial_uri)

    def deserialize(self, u_protocol_uri: str) -> UUri:
        if u_protocol_uri is None or u_protocol_uri.strip() == "":
            return UUri.empty()

        uri = u_protocol_uri.split(":")[-1].replace('\\', '/')
        is_local = not uri.startswith("//")
        uri_parts = uri.split("/")
        number_of_parts_in_uri = len(uri_parts)

        if number_of_parts_in_uri == 0 or number_of_parts_in_uri == 1:
            if is_local:
                return UUri.empty()
            else:
                return UUri(UAuthority.long_remote("", ""), UEntity.empty(), UResource.empty())

        use_name = uri_parts[1]
        use_version = ""

        if is_local:
            auth = UAuthority.local()
            if number_of_parts_in_uri > 2:
                use_version = uri_parts[2]
                res = self.parse_from_string(uri_parts[3]) if number_of_parts_in_uri > 3 else UResource.empty()
            else:
                res = UResource.empty()
        else:
            authority_parts = uri_parts[2].split(".")
            device = authority_parts[0]
            domain = ".".join(authority_parts[1:]) if len(authority_parts) > 1 else ""
            auth = UAuthority.long_remote(device, domain)

            if number_of_parts_in_uri > 3:
                use_name = uri_parts[3]
                if number_of_parts_in_uri > 4:
                    use_version = uri_parts[4]
                    res = self.parse_from_string(uri_parts[5]) if number_of_parts_in_uri > 5 else UResource.empty()
                else:
                    res = UResource.empty()
            else:
                return UUri(auth, UEntity.empty(), UResource.empty())

        use_version_int = int(use_version) if use_version.strip() else None

        return UUri(auth, UEntity.long_format(use_name, use_version_int), res)

    @staticmethod
    def parse_from_string(resource_string: str) -> UResource:
        if resource_string is None:
            raise ValueError("Resource must have a command name.")

        parts = resource_string.split("#")
        name_and_instance = parts[0]

        name_and_instance_parts = name_and_instance.split(".")
        resource_name = name_and_instance_parts[0]
        resource_instance = name_and_instance_parts[1] if len(name_and_instance_parts) > 1 else None
        resource_message = parts[1] if len(parts) > 1 else None

        return UResource.long_format_instance_message(resource_name, resource_instance, resource_message)
