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


import io
import struct
from enum import Enum

from uprotocol.proto.uri_pb2 import UAuthority
from uprotocol.proto.uri_pb2 import UEntity
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.uri.factory.uresource_builder import UResourceBuilder
from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.uri.validator.urivalidator import UriValidator


class AddressType(Enum):
    """
    The type of address used for Micro URI.
    """
    LOCAL = 0
    IPv4 = 1
    IPv6 = 2
    ID = 3

    def getValue(self):
        return bytes(self.value)

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

        if uri is None or UriValidator.is_empty(uri) or not UriValidator.is_micro_form(uri):
            return bytearray()

        maybe_ue_id = uri.entity.id
        maybe_uresource_id = uri.resource.id

        os = io.BytesIO()
        os.write(bytes([self.UP_VERSION]))

        if uri.authority.HasField('ip'):
            length: int = len(uri.authority.ip)
            if length == 4:
                address_type = AddressType.IPv4
            elif length == 16:
                address_type = AddressType.IPv6
            else:
                return bytearray()
        elif uri.authority.HasField('id'):
            address_type = AddressType.ID
        else:
            address_type = AddressType.LOCAL

        os.write(address_type.value.to_bytes(1, 'big'))

        # URESOURCE_ID
        os.write((maybe_uresource_id >> 8).to_bytes(1, 'big'))
        os.write((maybe_uresource_id & 0xFF).to_bytes(1, 'big'))

        # UENTITY_ID
        os.write((maybe_ue_id >> 8).to_bytes(1, 'big'))
        os.write((maybe_ue_id & 0xFF).to_bytes(1, 'big'))

        # UE_VERSION
        unsigned_value = uri.entity.version_major
        if unsigned_value > 127:
            signed_byte = unsigned_value - 256
        else:
            signed_byte = unsigned_value
        os.write(struct.pack('b', signed_byte))
        # UNUSED
        os.write(bytes([0]))

        # Populating the UAuthority
        if address_type != AddressType.LOCAL:
            # Write the ID length if the type is ID
            if address_type == AddressType.ID:
                os.write(len(uri.authority.id).to_bytes(1, 'big'))

            try:
                if uri.authority.HasField("ip"):
                    os.write(uri.authority.ip)
                elif uri.authority.HasField("id"):
                    os.write(uri.authority.id)
            except Exception as e:
                print(e)  # Handle the exception as needed

        return os.getvalue()

    def deserialize(self, micro_uri: bytes) -> UUri:
        """
        Deserialize a byte[] into a UUri object.<br><br>
        @param micro_uri:A byte[] uProtocol micro URI.
        @return:Returns an UUri data object from the serialized format of a microUri.
        """
        if micro_uri is None or len(micro_uri) < self.LOCAL_MICRO_URI_LENGTH:
            return UUri()

        if micro_uri[0] != self.UP_VERSION:
            return UUri()

        u_resource_id = ((micro_uri[2] & 0xFF) << 8) | (micro_uri[3] & 0xFF)
        addresstype = AddressType.from_value(micro_uri[1])

        # Validate Type is found
        if addresstype is None:
            return UUri()

        # Validate that the micro_uri is the correct length for the type
        address_type = addresstype
        if address_type == AddressType.LOCAL and len(micro_uri) != self.LOCAL_MICRO_URI_LENGTH:
            return UUri()
        elif address_type == AddressType.IPv4 and len(micro_uri) != self.IPV4_MICRO_URI_LENGTH:
            return UUri()
        elif address_type == AddressType.IPv6 and len(micro_uri) != self.IPV6_MICRO_URI_LENGTH:
            return UUri()

        # UENTITY_ID
        ue_id = ((micro_uri[4] & 0xFF) << 8) | (micro_uri[5] & 0xFF)

        # UE_VERSION
        ui_version = micro_uri[6]

        u_authority = None
        if address_type in (AddressType.IPv4, AddressType.IPv6):
            length = 4 if address_type == AddressType.IPv4 else 16
            data = micro_uri[8:8 + length]
            u_authority = UAuthority(ip=bytes(data))
        elif address_type == AddressType.ID:
            length = micro_uri[8]
            u_authority = UAuthority(id=bytes(micro_uri[9:9 + length]))

        uri = UUri(entity=UEntity(id=ue_id, version_major=ui_version), resource=UResourceBuilder.from_id(u_resource_id))

        if u_authority is not None:
            uri.authority.CopyFrom(u_authority)

        return uri
