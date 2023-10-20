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

from org_eclipse_uprotocol.uri.datamodel.uauthority import UAuthority
from org_eclipse_uprotocol.uri.datamodel.uentity import UEntity
from org_eclipse_uprotocol.uri.datamodel.uresource import UResource


class UUri:
    EMPTY = None

    def __init__(self, authority: UAuthority, entity: UEntity, resource: UResource):
        self.authority = authority if authority else UAuthority.empty()
        self.entity = entity if entity else UEntity.empty()
        self.resource = resource if resource else UResource.empty()

    @staticmethod
    def rpc_response(authority: UAuthority, entity: UEntity):
        return UUri(authority, entity, UResource.for_rpc_response())

    @staticmethod
    def empty():
        if UUri.EMPTY is None:
            UUri.EMPTY = UUri(UAuthority.empty(), UEntity.empty(), UResource.empty())
        return UUri.EMPTY

    def is_empty(self):
        return self.authority.is_empty() and self.entity.is_empty() and self.resource.is_empty()

    def is_resolved(self) -> bool:
        return self.authority.is_resolved() and self.entity.is_resolved() and self.resource.is_resolved()

    def is_long_form(self) -> bool:
        return self.authority.is_long_form() and (self.entity.is_long_form() or self.entity.is_empty()) and (
                self.resource.is_long_form() or self.resource.is_empty())

    def is_micro_form(self) -> bool:
        return self.authority.is_micro_form() and self.entity.is_micro_form() and self.resource.is_micro_form()

    def get_u_authority(self) -> UAuthority:
        return self.authority

    def get_u_entity(self) -> UEntity:
        return self.entity

    def get_u_resource(self) -> UResource:
        return self.resource

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, UUri):
            return False
        return self.authority == other.authority and self.entity == other.entity and self.resource == other.resource

    def __hash__(self):
        return hash((self.authority, self.entity, self.resource))

    def __str__(self):
        return f"UUri{{uAuthority={self.authority}, uEntity={self.entity}, uResource={self.resource}}}"


# Initialize EMPTY
UUri.EMPTY = UUri(UAuthority.empty(), UEntity.empty(), UResource.empty())
