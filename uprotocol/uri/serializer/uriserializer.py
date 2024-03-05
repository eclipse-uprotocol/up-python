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


from abc import ABC, abstractmethod
from re import T
from typing import Optional
from uprotocol.proto.uri_pb2 import UUri,UAuthority,UEntity,UResource
from uprotocol.uri.validator.urivalidator import UriValidator


class UriSerializer(ABC):
    """
    UUris are used in transport layers and hence need to be serialized.<br>Each transport supports different
    serialization formats.<br>For more information, please refer to <a
    href="https://github.com/eclipse-uprotocol/uprotocol-spec/blob/main/basics/uri.adoc">
    https://github.com/eclipse-uprotocol/uprotocol-spec/blob/main/basics/uri.adoc</a>
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

    def build_resolved(self, long_uri: str, micro_uri: bytes) -> UUri:
        """
        Build a fully resolved UUri from the serialized long format and the serializes micro format.<br><br>
        @param long_uri:UUri serialized as a Sting.
        @param micro_uri:UUri serialized as a byte[].
        @return:Returns a UUri object serialized from one of the forms.
        """
        if (not long_uri or long_uri.isspace()) and (not micro_uri or len(micro_uri) == 0):
            return UUri()
        from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
        from uprotocol.uri.serializer.microuriserializer import MicroUriSerializer
        long_u_uri = LongUriSerializer().deserialize(long_uri)
        micro_u_uri = MicroUriSerializer().deserialize(micro_uri)
        u_authority = UAuthority()
        u_authority.CopyFrom(micro_u_uri.authority)

        u_authority.name = long_u_uri.authority.name

        u_entity = UEntity()
        u_entity.CopyFrom(micro_u_uri.entity)

        u_entity.name = long_u_uri.entity.name

        u_resource = UResource()
        u_resource.CopyFrom(long_u_uri.resource)
        u_resource.id = micro_u_uri.resource.id

        u_uri = UUri(authority=u_authority, entity=u_entity, resource=u_resource)
        return u_uri if UriValidator.is_resolved(u_uri) else None
