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

from org_eclipse_uprotocol.proto.uri_pb2 import UAuthority
from org_eclipse_uprotocol.proto.uri_pb2 import UEntity
from org_eclipse_uprotocol.proto.uri_pb2 import UResource
from org_eclipse_uprotocol.proto.uri_pb2 import UUri
from org_eclipse_uprotocol.uri.factory.uauthority_factory import UAuthorityFactory
from org_eclipse_uprotocol.uri.factory.uentity_factory import UEntityFactory
from org_eclipse_uprotocol.uri.factory.uresource_factory import UResourceFactory


class UUriFactory:
    """
    A factory is a part of the software that has methods to generate concrete objects, usually of the same type.<br>
    Data representation of uProtocol <b>URI</b>.<br>This class will be used to represent the source and sink (
    destination) parts of the Packet, for example in a CloudEvent Packet. <br>UUri is used as a method to uniquely
    identify devices, services, and resources on the  network.<br>Where software is deployed, what the service is
    called along with a version and the resources in the service. Defining a common URI for the system allows
    applications and/or services to publish and discover each other as well as maintain a database/repository of
    microservices in the various vehicles.<br> Example for long format serialization:
    <pre>//&lt;device&gt;.&lt;domain&gt;/&lt;service&gt;/&lt;version&gt;/&lt;resource&gt;#&lt;message&gt;</pre><br>
     The UUri Factory knows how to generate UUri proto message.<br>
    """

    @staticmethod
    def create_uuri(authority: UAuthority, entity: UEntity, resource: UResource):
        """
        Create an UUri passing the Authority, Entity and Resource proto message
        @param authority: The uAuthority represents the deployment location of a specific Software Entity.
        @param entity: The SW entity information.
        @param resource: The SW resource information
        @return:
        """
        return UUri(authority=authority, entity=entity, resource=resource)

    @staticmethod
    def rpc_response(authority: UAuthority, entity: UEntity) -> UUri:
        """
        Create an RPC Response UUri passing the Authority and Entity information.<br><br>
        @param authority:The uAuthority represents the deployment location of a specific Software Entity.
        @param entity:The SW entity information.
        @return:Returns a UUri of a constructed RPC Response.
        """
        return UUri(authority=authority, entity=entity, resource=UResourceFactory.for_rpc_response())

    @staticmethod
    def empty() -> UUri:
        """
        Static factory method for creating an empty  uri, to avoid working with null<br><br>
        @return:Returns an empty uri to avoid working with null.
        """
        return UUri()

    def is_empty(uuri: UUri) -> bool:
        """
        Indicates that this  URI is an empty container and has no valuable information in building uProtocol sinks or
        sources.<br><br>
        @param uuri: An UUri proto message object
        @return:Returns true if this  URI is an empty container and has no valuable information in building uProtocol
        sinks or sources.
        """
        return UAuthorityFactory.is_empty(uuri.authority) and UEntityFactory.is_empty(
            uuri.entity) and UResourceFactory.is_empty(uuri.resource)

    def is_long_form(uuri: UUri) -> bool:
        """
        Determines if this UUri can be serialized into a long form UUri.<br><br>
        @param uuri: An UUri proto message object
        @return:Returns true if this UUri can be serialized into a long form UUri.
        """
        return UAuthorityFactory.is_long_form(uuri.authority) and (
                UEntityFactory.is_long_form(uuri.entity) or UEntityFactory.is_empty(uuri.entity)) and (
                UResourceFactory.is_long_form(uuri.resource) or UResourceFactory.is_empty(uuri.resource))

    def is_micro_form(uuri: UUri) -> bool:
        """
        Determines if this UUri can be serialized into a micro form UUri.<br><br>
        @param uuri: An UUri proto message object
        @return:Returns true if this UUri can be serialized into a micro form UUri.
        """
        return UAuthorityFactory.is_micro_form(uuri.authority) and UEntityFactory.is_micro_form(
            uuri.entity) and UResourceFactory.is_micro_form(uuri.resource)
