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
    """
    Data representation of uProtocol <b>URI</b>.<br>This class will be used to represent the source and sink (
    destination) parts of the Packet, for example in a CloudEvent Packet. <br>UUri is used as a method to uniquely
    identify devices, services, and resources on the  network.<br>Where software is deployed, what the service is
    called along with a version and the resources in the service. Defining a common URI for the system allows
    applications and/or services to publish and discover each other as well as maintain a database/repository of
    microservices in the various vehicles.<br> Example for long format serialization:
    <pre>//&lt;device&gt;.&lt;domain&gt;/&lt;service&gt;/&lt;version&gt;/&lt;resource&gt;#&lt;message&gt;</pre>
    """
    EMPTY = None

    def __init__(self, authority: UAuthority, entity: UEntity, resource: UResource):
        """
        Create a full URI.<br><br>
        @param authority:The uAuthority represents the deployment location of a specific Software Entity .
        @param entity:The uEntity in the role of a service or in the role of an application is the software and version.
        @param resource:The uResource is something that is manipulated by a service such as a Door.
        """
        self.authority = authority if authority else UAuthority.empty()
        self.entity = entity if entity else UEntity.empty()
        self.resource = resource if resource else UResource.empty()

    @staticmethod
    def rpc_response(authority: UAuthority, entity: UEntity):
        """
        Create an RPC Response UUri passing the Authority and Entity information.<br><br>
        @param authority:The uAuthority represents the deployment location of a specific Software Entity.
        @param entity:The SW entity information.
        @return:Returns a UUri of a constructed RPC Response.
        """
        return UUri(authority, entity, UResource.for_rpc_response())

    @staticmethod
    def empty():
        """
        Static factory method for creating an empty  uri, to avoid working with null<br><br>
        @return:Returns an empty uri to avoid working with null.
        """
        if UUri.EMPTY is None:
            UUri.EMPTY = UUri(UAuthority.empty(), UEntity.empty(), UResource.empty())
        return UUri.EMPTY

    def is_empty(self):
        """
        Indicates that this  URI is an empty container and has no valuable information in building uProtocol sinks or
        sources.<br><br>
        @return:Returns true if this  URI is an empty container and has no valuable information in building uProtocol
        sinks or sources.
        """
        return self.authority.is_empty() and self.entity.is_empty() and self.resource.is_empty()

    def is_resolved(self) -> bool:
        """
        Returns true if URI contains both names and numeric representations of the names inside its belly.<br>Meaning
        that this UUri can be serialized to long or micro formats.<br><br>
        @return:Returns true if URI contains both names and numeric representations of the names inside its
        belly.Meaning that this UUri can be serialized to long or micro formats.
        """
        return self.authority.is_resolved() and self.entity.is_resolved() and self.resource.is_resolved()

    def is_long_form(self) -> bool:
        """
        Determines if this UUri can be serialized into a long form UUri.<br><br>
        @return:Returns true if this UUri can be serialized into a long form UUri.
        """
        return self.authority.is_long_form() and (self.entity.is_long_form() or self.entity.is_empty()) and (
                self.resource.is_long_form() or self.resource.is_empty())

    def is_micro_form(self) -> bool:
        """
        Determines if this UUri can be serialized into a micro form UUri.<br><br>
        @return:Returns true if this UUri can be serialized into a micro form UUri.
        """
        return self.authority.is_micro_form() and self.entity.is_micro_form() and self.resource.is_micro_form()

    def get_u_authority(self) -> UAuthority:
        """

        @return: Returns the Authority represents the deployment location of a specific Software Entity.
        """
        return self.authority

    def get_u_entity(self) -> UEntity:
        """

        @return:Returns the USE in the role of a service or in the role of an application.
        """
        return self.entity

    def get_u_resource(self) -> UResource:
        """

        @return: Returns the resource, something that is manipulated by a service such as a Door.
        """
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
