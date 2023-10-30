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

from abc import ABC, abstractmethod
from re import T
from typing import Optional

from org_eclipse_uprotocol.proto.uri_pb2 import UUri
from org_eclipse_uprotocol.uri.factory.uauthority_factory import UAuthorityFactory
from org_eclipse_uprotocol.uri.factory.uentity_factory import UEntityFactory
from org_eclipse_uprotocol.uri.factory.uresource_factory import UResourceFactory
from org_eclipse_uprotocol.uri.factory.uuri_factory import UUriFactory


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

    def build_resolved(self, long_uri: str, micro_uri: bytes) -> Optional[UUri]:
        """
        Build a fully resolved {@link UUri} from the serialized long format and the serializes micro format.<br><br>
        @param long_uri:UUri serialized as a Sting.
        @param micro_uri:UUri serialized as a byte[].
        @return:Returns a UUri object serialized from one of the forms.
        """
        if (not long_uri or long_uri.isspace()) and (not micro_uri or len(micro_uri) == 0):
            return UUriFactory.empty()
        from org_eclipse_uprotocol.uri.serializer.longuriserializer import LongUriSerializer
        from org_eclipse_uprotocol.uri.serializer.microuriserializer import MicroUriSerializer
        long_u_uri = LongUriSerializer().deserialize(long_uri)
        micro_u_uri = MicroUriSerializer().deserialize(micro_uri)

        u_authority = (UAuthorityFactory.local() if UAuthorityFactory.is_local(
            long_u_uri.authority) else UAuthorityFactory.resolved_remote(long_u_uri.authority.name or None,
                                                                         micro_u_uri.authority.ip or None))

        u_entity = UEntityFactory.resolved_format(long_u_uri.entity.name, long_u_uri.entity.version_major or None,
                                                  long_u_uri.entity.version_minor or None,
                                                  micro_u_uri.entity.id or None)

        u_resource = UResourceFactory.resolved_format(long_u_uri.resource.name,
                                               long_u_uri.resource.instance or None,
                                               long_u_uri.resource.message or None,
                                               micro_u_uri.resource.id or None)

        u_uri = UUri(u_authority, u_entity, u_resource)
        return u_uri if u_uri.is_resolved() else None
