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
from org_eclipse_uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from org_eclipse_uprotocol.uri.serializer.uriserializer import UriSerializer


class ShortUriSerializer(UriSerializer):
    SCHEME = "s:"  # Required Scheme
    INSTANCE = None

    def __init__(self):
        pass

    @classmethod
    def instance(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = ShortUriSerializer()
        return cls.INSTANCE

    def serialize(self, uri):
        if uri is None or uri.is_empty():
            return ""

        sb = [self.SCHEME]
        sb.append(self.build_authority_part_of_uri(uri.get_u_authority()))

        if uri.get_u_authority().is_marked_remote():
            sb.append("/")

        if uri.get_u_entity().is_empty():
            return ''.join(sb)

        sb.append(self.build_software_entity_part_of_uri(uri.get_u_entity()))
        sb.append(self.build_resource_part_of_uri(uri.get_u_resource()))

        return re.sub('/+$', '', ''.join(sb))

    def deserialize(self, u_protocol_uri):
        if u_protocol_uri is None or u_protocol_uri.isspace() or self.SCHEME not in u_protocol_uri:
            return UUri.empty()

        uri = u_protocol_uri[u_protocol_uri.index(":") + 1:].replace('\\', '/')
        is_local = not uri.startswith("//")

        uri_parts = uri.split("/")
        number_of_parts_in_uri = len(uri_parts)

        if number_of_parts_in_uri == 0 or number_of_parts_in_uri == 1:
            return UUri.empty() if is_local else UUri(UAuthority.long_remote("", ""), UEntity.empty(),
                                                      UResource.empty())

        use_name = ""
        use_version = ""
        u_resource = UResource.empty()
        authority_parts = uri_parts[2].split(".")
        device = authority_parts[0]
        domain = ""

        if len(authority_parts) > 1:
            domain = ".".join(authority_parts[1:])

        u_authority = UAuthority.long_remote(device, domain)

        if len(uri_parts) > 3:
            use_name = uri_parts[3]

            if number_of_parts_in_uri > 4:
                use_version = uri_parts[4]

                if number_of_parts_in_uri > 5:
                    try:
                        resource_id = int(uri_parts[5])
                        u_resource = UResource.micro_format(resource_id)
                    except ValueError:
                        return UUri.empty()
                else:
                    u_resource = UResource.empty()
            else:
                u_resource = UResource.empty()
        else:
            return UUri(u_authority, UEntity.empty(), UResource.empty())

        use_version_int = None
        try:
            if use_version.strip():
                use_version_int = int(use_version)
        except ValueError:
            return UUri.empty()

        use_id = None
        try:
            if use_name.strip():
                use_id = int(use_name)
        except ValueError:
            return UUri.empty()

        return UUri(u_authority, UEntity.micro_format_id_version(use_id, use_version_int), u_resource)

    def build_resource_part_of_uri(self, u_resource):
        if u_resource.is_empty() or not u_resource.is_micro_form():
            return ""
        sb = ["/"]
        if u_resource.get_id():
            sb.append(str(u_resource.get_id()))

        return ''.join(sb)

    def build_software_entity_part_of_uri(self, ue: UEntity):
        sb = []
        if ue.get_id():
            sb.append(str(ue.get_id()))
        sb.append("/")
        if ue.get_version():
            sb.append(str(ue.get_version()))
        return ''.join(sb)

    def build_authority_part_of_uri(self, authority: UAuthority):
        if authority.is_local():
            return "/"
        partial_uri = "//"
        device = authority.device
        domain = authority.domain

        if device:
            partial_uri += device
            if domain:
                partial_uri += "."

        if domain:
            partial_uri += domain

        return partial_uri


if __name__ == '__main__':
    # Example usage
    # Create a UUri object
    u_authority = UAuthority.long_remote("vcu", "vin")
    # u_entity = UEntity.micro_format_id_version(1, 2)
    u_entity = UEntity.resolved_format("neelam", 1, 2)
    # u_resource = UResource.micro_format(3)
    u_resource = UResource.resolved_format("salary", "raise", "Salary", 4)
    u_uri = UUri(u_authority, u_entity, u_resource)

    # Serialize the UUri object
    serializer = ShortUriSerializer.instance()
    serialized_uri = serializer.serialize(u_uri)
    print("Serialized URI:", serialized_uri)

    # Deserialize a string to a UUri object
    deserialized_uri = serializer.deserialize(serialized_uri)
    print("Deserialized UUri:", deserialized_uri)
