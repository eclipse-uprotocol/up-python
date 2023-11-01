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


from org_eclipse_uprotocol.proto.uri_pb2 import UResource


class UResourceFactory:
    """
    A factory is a part of the software that has methods to generate concrete objects, usually of the same type.<br>
    A service API - defined in the UEntity - has Resources and Methods. Both of these are represented by the
    UResource class.<br>A uResource represents a resource from a Service such as "door" and an optional specific
    instance such as "front_left". In addition, it can optionally contain the name of the resource Message type,
    such as "Door". The Message type matches the protobuf service IDL that defines structured data types. <br> An
    UResource is something that can be manipulated/controlled/exposed by a service. Resources are unique when
    prepended with UAuthority that represents the device and UEntity that represents the service.<br> The UResource
    Factory knows how to generate UResource proto message.<br>
    """

    @staticmethod
    def long_format(name: str) -> UResource:
        """
        Build a UResource that can be serialized into a long UUri. Mostly used for publishing messages.<br><br>
        @param name:The name of the resource as a noun such as door or window, or in the case a method that
        manipulates the resource, a verb.
        @return:Returns a UResource that can be serialized into a long UUri.
        """
        return UResource(name=name if name else "")

    @staticmethod
    def long_format_instance_message(name: str, instance: str, message: str) -> UResource:
        """
        Build a UResource that can be serialized into a long UUri. Mostly used for publishing messages.<br><br>
        @param name:The name of the resource as a noun such as door or window, or in the case a method that
        manipulates the resource, a verb.
        @param instance:An instance of a resource such as front_left.
        @param message:The Message type matches the protobuf service IDL message name that defines structured data
        types. A message is a data structure type used to define data that is passed in  events and rpc methods.
        @return:Returns a UResource that can be serialised into a long UUri.
        """
        resource = UResource(name=name if name else "")
        if instance is not None and instance != "":
            resource.instance = instance
        if message is not None and message != "":
            resource.message = message
        return resource

    @staticmethod
    def micro_format(identifier: int):
        """
        Build a UResource that can be serialised into a micro UUri. Mostly used for publishing messages.<br><br>
        @param identifier:The numeric representation of this uResource.
        @return:Returns a UResource that can be serialised into a micro UUri.
        """
        return UResource(id=identifier if identifier else 0)

    @staticmethod
    def for_rpc_request(method_name: str):
        """
        Build a UResource for rpc request, using only the long format.<br><br>
        @param method_name:The RPC method name.
        @return:Returns a UResource used for an RPC request that could be serialised in long format.
        """
        return UResource(name="rpc", instance=method_name if method_name else "")

    @staticmethod
    def for_rpc_request_with_id(method_id: int):
        """
        Build a UResource for rpc request, using only the micro format.<br><br>
        @param method_id:The numeric representation method name for the RPC.
        @return:Returns a UResource used for an RPC request that could be serialised in micro format.
        """
        return UResource(name="rpc", id=method_id if method_id else 0)

    @staticmethod
    def for_rpc_request_with_name_and_id(method_name: str, method_id: int):
        """
        Build a UResource for rpc request, using both the long and micro format information.<br><br>
        @param method_name:The RPC method name.
        @param method_id:The numeric representation method name for the RPC.
        @return:Returns a UResource used for an RPC request that could be serialised in long and micro format.
        """
        resource = UResource(name="rpc")
        if method_name is not None and method_name != "":
            resource.instance = method_name
        if method_id is not None and method_id != 0:
            resource.id = method_id
        return resource

    @staticmethod
    def for_rpc_response():
        """
        Static factory method for creating a response resource that is returned from RPC calls<br><br>
        @return:Returns a response  resource used for response RPC calls.
        """
        return UResource(name="rpc", instance="response")

    @staticmethod
    def is_rpc_method(uresource: UResource) -> bool:
        """
        Returns true if this resource specifies an RPC method call or RPC response.<br><br>
        @param uresource: UResource protobuf message
        @return:Returns true if this resource specifies an RPC method call or RPC response.
        """
        return uresource.name == "rpc" and (uresource.instance.strip() != "" or uresource.id != 0)

    @staticmethod
    def empty():
        """
        Static factory method for creating an empty  resource, to avoid working with null<br><br>
        @return:Returns an empty  resource that has a blank name and no message instance information.
        """
        return UResource()

    @staticmethod
    def is_empty(uresource: UResource) -> bool:
        """
        Indicates that this resource is an empty container and has no valuable information in building uProtocol
        URI.<br><br>
        @param uresource: UResource protobuf message
        @return:Returns true if this resource is an empty container and has no valuable information in building
        uProtocol URI.
        """
        return uresource.name.strip() == "" or uresource.name == "rpc" and not (
                uresource.instance.strip() != "" or uresource.message.strip() != "" or uresource.id != 0)

    @staticmethod
    def is_long_form(uresource: UResource) -> bool:
        """
        Returns true if the uResource contains names so that it can be serialized to long format.<br><br>
        @param uresource: UResource protobuf message
        @return:Returns true if the uResource contains names so that it can be serialized to long format.
        """
        if uresource.name == "rpc":
            return bool(uresource.instance)
        return bool(uresource.name)

    @staticmethod
    def is_micro_form(uresource: UResource) -> bool:
        """
        Returns true if the uResource contains the id's which will allow the Uri part to be serialized into micro
        form.<br><br>
        @param uresource: UResource protobuf message
        @return:Returns true if the uResource can be serialized into micro form.
        """
        return uresource.id != 0

    @staticmethod
    def resolved_format(name: str, instance: str, message: str, identifier: int):
        """
        Build a UResource that has all elements resolved and can be serialized in a long UUri or a micro UUri.<br><br>
        @param name:The name of the resource as a noun such as door or window, or in the case a method that
        manipulates the resource, a verb.
        @param instance:An instance of a resource such as front_left.
        @param message:The Message type matches the protobuf service IDL message name that defines structured data
        types.A message is a data structure type used to define data that is passed in  events and rpc methods.
        @param identifier:The numeric representation of this uResource.
        @return:Returns a UResource that has all the information that is needed to serialize into a long UUri or a
        micro UUri.
        """
        resource = UResource(name if name else "")
        if instance is not None and instance != "":
            resource.instance = instance
        if message is not None and message != "":
            resource.message = message
        if identifier is not None and identifier != 0:
            resource.id = identifier
        return resource
