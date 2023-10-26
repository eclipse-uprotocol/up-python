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

import io
import ipaddress
import socket
from enum import Enum
from typing import Optional

from org_eclipse_uprotocol.uri.datamodel.uauthority import UAuthority
from org_eclipse_uprotocol.uri.datamodel.uentity import UEntity
from org_eclipse_uprotocol.uri.datamodel.uresource import UResource
from org_eclipse_uprotocol.uri.datamodel.uuri import UUri
from org_eclipse_uprotocol.uri.serializer.uriserializer import UriSerializer


class AddressType(Enum):
    """
    The type of address used for Micro URI.
    """
    LOCAL = 0
    IPv4 = 1
    IPv6 = 2

    def getValue(self):
        return self.value

    @classmethod
    def from_value(cls, value):
        for addr_type in cls:
            if addr_type.value == value:
                return addr_type
        return None  # Return None if no matching enum value is found


class MicroUriSerializer(UriSerializer):
    """
    UUri Serializer that serializes a UUri to a byte[] (micro format) per <a
    href="https://github.com/eclipse-uprotocol/uprotocol-spec/blob/main/basics/uri.adoc">
    https://github.com/eclipse-uprotocol/uprotocol-spec/blob/main/basics/uri.adoc</a>
    """
    LOCAL_MICRO_URI_LENGTH = 8
    IPV4_MICRO_URI_LENGTH = 12
    IPV6_MICRO_URI_LENGTH = 24
    UP_VERSION = 0x1

    def serialize(self, uri: UUri) -> bytes:
        """
        Serialize a UUri into a byte[] following the Micro-URI specifications.<br><br>
        @param uri:The UUri data object.
        @return:Returns a byte[] representing the serialized UUri.
        """
        if uri is None or uri.is_empty() or not uri.is_micro_form():
            return bytearray()

        maybe_address = uri.get_u_authority().address
        maybe_ue_id = uri.get_u_entity().id
        maybe_uresource_id = uri.get_u_resource().id

        os = io.BytesIO()
        os.write(bytes([self.UP_VERSION]))

        if maybe_address:
            os.write(
                bytes([AddressType.IPv4.getValue()]) if isinstance(maybe_address, ipaddress.IPv4Address) else bytes(
                    [AddressType.IPv6.getValue()]))
        else:
            os.write(bytes([AddressType.LOCAL.getValue()]))

        os.write(maybe_uresource_id.to_bytes(2, byteorder='big'))

        maybe_uauthority_address_bytes = self.calculate_uauthority_bytes(uri.get_u_authority())
        if maybe_uauthority_address_bytes:
            os.write(maybe_uauthority_address_bytes)

        os.write(maybe_ue_id.to_bytes(2, byteorder='big'))

        version = uri.get_u_entity().get_version()
        os.write(version.to_bytes(1, byteorder='big') if version else b'\x00')
        os.write(b'\x00')  # Unused byte

        return os.getvalue()

    def calculate_uauthority_bytes(self, uauthority: UAuthority) -> Optional[bytes]:
        maybe_address = uauthority.address
        return maybe_address.packed if maybe_address else None

    def deserialize(self, micro_uri: bytes) -> UUri:
        """
        Deserialize a byte[] into a UUri object.<br><br>
        @param micro_uri:A byte[] uProtocol micro URI.
        @return:Returns an UUri data object from the serialized format of a microUri.
        """
        if micro_uri is None or len(micro_uri) < self.LOCAL_MICRO_URI_LENGTH:
            return UUri.empty()

        if micro_uri[0] != self.UP_VERSION:
            return UUri.empty()

        uresource_id = int.from_bytes(micro_uri[2:4], byteorder='big')
        address_type = AddressType.from_value(micro_uri[1])

        if address_type == AddressType.LOCAL and len(micro_uri) != self.LOCAL_MICRO_URI_LENGTH:
            return UUri.empty()
        elif address_type == AddressType.IPv4 and len(micro_uri) != self.IPV4_MICRO_URI_LENGTH:
            return UUri.empty()
        elif address_type == AddressType.IPv6 and len(micro_uri) != self.IPV6_MICRO_URI_LENGTH:
            return UUri.empty()

        index = 4
        if address_type == AddressType.LOCAL:
            u_authority = UAuthority.local()
        else:
            try:
                inet_address = socket.inet_ntop(socket.AF_INET, micro_uri[
                                                                index:index + 4]) if address_type == AddressType.IPv4\
                    else socket.inet_ntop(
                    socket.AF_INET6, micro_uri[index:index + 16])
                u_authority = UAuthority.micro_remote(ipaddress.ip_address(inet_address))
            except:
                u_authority = UAuthority.local()
            index += 4 if address_type == AddressType.IPv4 else 16

        ue_id = int.from_bytes(micro_uri[index:index + 2], byteorder='big')
        ui_version = micro_uri[index + 2]

        return UUri(u_authority, UEntity.micro_format_id_version(ue_id, ui_version if ui_version != 0 else None),
                    UResource.micro_format(uresource_id))
