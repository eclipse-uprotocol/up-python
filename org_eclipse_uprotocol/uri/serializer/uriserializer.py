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

from org_eclipse_uprotocol.uri.datamodel.uauthority import UAuthority
from org_eclipse_uprotocol.uri.datamodel.uentity import UEntity
from org_eclipse_uprotocol.uri.datamodel.uresource import UResource
from org_eclipse_uprotocol.uri.datamodel.uuri import UUri


class UriSerializer(ABC):
    @abstractmethod
    def deserialize(self, uri: T) -> UUri:
        pass

    @abstractmethod
    def serialize(self, uri: UUri) -> T:
        pass

    def build_resolved(self, long_uri: str, micro_uri: bytes) -> Optional[UUri]:
        if (not long_uri or long_uri.isspace()) and (not micro_uri or len(micro_uri) == 0):
            return Optional.of(UUri.empty())
        from org_eclipse_uprotocol.uri.serializer.longuriserializer import LongUriSerializer
        from org_eclipse_uprotocol.uri.serializer.microuriserializer import MicroUriSerializer
        long_u_uri = LongUriSerializer().deserialize(long_uri)
        micro_u_uri = MicroUriSerializer().deserialize(micro_uri)

        u_authority = (UAuthority.local() if long_u_uri.get_u_authority().is_local() else UAuthority.resolved_remote(
            long_u_uri.get_u_authority().device or None, long_u_uri.get_u_authority().domain or None,
            micro_u_uri.get_u_authority().address or None))

        u_entity = UEntity.resolved_format(long_u_uri.get_u_entity().get_name(),
                                           long_u_uri.get_u_entity().get_version() or None,
                                           micro_u_uri.get_u_entity().get_id() or None)

        u_resource = UResource.resolved_format(long_u_uri.get_u_resource().get_name(),
                                               long_u_uri.get_u_resource().get_instance() or None,
                                               long_u_uri.get_u_resource().get_message() or None,
                                               micro_u_uri.get_u_resource().get_id() or None)

        u_uri = UUri(u_authority, u_entity, u_resource)
        return u_uri if u_uri.is_resolved() else None
