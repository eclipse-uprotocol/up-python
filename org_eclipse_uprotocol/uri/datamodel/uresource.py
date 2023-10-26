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
class UResource:
    """
    A service API - defined in the UEntity - has Resources and Methods. Both of these are represented by the
    UResource class.<br>A uResource represents a resource from a Service such as "door" and an optional specific
    instance such as "front_left". In addition, it can optionally contain the name of the resource Message type,
    such as "Door". The Message type matches the protobuf service IDL that defines structured data types. <br> An
    UResource is something that can be manipulated/controlled/exposed by a service. Resources are unique when
    prepended with UAuthority that represents the device and UEntity that represents the service.
    """
    EMPTY = None
    RESPONSE = None

    def __init__(self, name: str, instance: str, message: str, identifier: int, marked_resolved: bool):
        """
        Create a uResource. The resource is something that is manipulated by a service such as a door.<br><br>
        @param name:The name of the resource as a noun such as door or window, or in the case a method that
        manipulates the resource, a verb.
        @param instance:An instance of a resource such as front_left.
        @param message:The Message type matches the protobuf service IDL message name that defines structured data
        types.A message is a data structure type used to define data that is passed in  events and rpc methods.
        @param identifier:The numeric representation of this uResource.
        @param marked_resolved:Indicates that this uResource was populated with intent of having all data.
        """
        self.name = name if name else ""
        self.instance = instance
        self.message = message
        self.id = identifier
        self.marked_resolved = marked_resolved

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
        resolved = name and name.strip() and identifier is not None
        return UResource(name if name else "", instance, message, identifier, resolved)

    @staticmethod
    def long_format(name: str):
        """
        Build a UResource that can be serialized into a long UUri. Mostly used for publishing messages.<br><br>
        @param name:The name of the resource as a noun such as door or window, or in the case a method that
        manipulates the resource, a verb.
        @return:Returns a UResource that can be serialized into a long UUri.
        """
        return UResource(name if name else "", None, None, None, False)

    @staticmethod
    def long_format_instance_message(name: str, instance: str, message: str):
        """
        Build a UResource that can be serialized into a long UUri. Mostly used for publishing messages.<br><br>
        @param name:The name of the resource as a noun such as door or window, or in the case a method that
        manipulates the resource, a verb.
        @param instance:An instance of a resource such as front_left.
        @param message:The Message type matches the protobuf service IDL message name that defines structured data
        types. A message is a data structure type used to define data that is passed in  events and rpc methods.
        @return:Returns a UResource that can be serialised into a long UUri.
        """
        return UResource(name if name else "", instance, message, None, False)

    @staticmethod
    def micro_format(identifier: int):
        """
        Build a UResource that can be serialised into a micro UUri. Mostly used for publishing messages.<br><br>
        @param identifier:The numeric representation of this uResource.
        @return:Returns a UResource that can be serialised into a micro UUri.
        """
        return UResource("", None, None, identifier, False)

    @staticmethod
    def for_rpc_request(method_name: str):
        """
        Build a UResource for rpc request, using only the long format.<br><br>
        @param method_name:The RPC method name.
        @return:Returns a UResource used for an RPC request that could be serialised in long format.
        """
        return UResource("rpc", method_name, None, None, False)

    @staticmethod
    def for_rpc_request_with_id(method_id: int):
        """
        Build a UResource for rpc request, using only the micro format.<br><br>
        @param method_id:The numeric representation method name for the RPC.
        @return:Returns a UResource used for an RPC request that could be serialised in micro format.
        """
        return UResource("rpc", None, None, method_id, False)

    @staticmethod
    def for_rpc_request_with_name_and_id(method_name: str, method_id: int):
        """
        Build a UResource for rpc request, using both the long and micro format information.<br><br>
        @param method_name:The RPC method name.
        @param method_id:The numeric representation method name for the RPC.
        @return:Returns a UResource used for an RPC request that could be serialised in long and micro format.
        """
        resolved = method_name and method_name.strip() and method_id is not None
        return UResource("rpc", method_name, None, method_id, resolved)

    @staticmethod
    def for_rpc_response():
        """
        Static factory method for creating a response resource that is returned from RPC calls<br><br>
        @return:Returns a response  resource used for response RPC calls.
        """
        return UResource.RESPONSE

    def is_rpc_method(self) -> bool:
        """
        Returns true if this resource specifies an RPC method call or RPC response.<br><br>
        @return:Returns true if this resource specifies an RPC method call or RPC response.
        """
        return self.name == "rpc"

    @staticmethod
    def empty():
        """
        Static factory method for creating an empty  resource, to avoid working with null<br><br>
        @return:Returns an empty  resource that has a blank name and no message instance information.
        """
        if UResource.EMPTY is None:
            UResource.EMPTY = UResource("", None, None, None, False)
        return UResource.EMPTY

    def is_empty(self) -> bool:
        """
        Indicates that this resource is an empty container and has no valuable information in building uProtocol
        URI.<br><br>
        @return:Returns true if this resource is an empty container and has no valuable information in building
        uProtocol URI.
        """
        return not (self.name and self.name.strip()) or self.name == "rpc" and not (
                self.instance or self.message or self.id)

    def get_name(self) -> str:
        """

        @return: Returns the name of the resource as a noun such as door or window, or in the case a method that
        manipulates the resource, a verb.
        """
        return self.name

    def get_id(self) -> int:
        """

        @return: Returns the resource id if it exists.
        """
        return self.id

    def get_instance(self) -> str:
        """
        An instance of a resource such as front_left or in the case of RPC a method name that manipulates the
        resource such as UpdateDoor.<br><br>
        @return:Returns the resource instance of the resource if it exists. If the instance does not exist,
        it is assumed that all the instances of the resource are wanted.
        """
        return self.instance

    def get_message(self) -> str:
        """
        The Message type matches the protobuf service IDL that defines structured data types.<br>A message is a data
        structure type used to define data that is passed in  events and rpc methods.<br><br>
        @return:Returns the Message type matches the protobuf service IDL that defines structured data types.
        """
        return self.message

    def is_resolved(self) -> bool:
        """
        Return true if this resource contains both ID and names.<br>Method type of UResource requires name, instance,
        and ID where a topic type of UResource also requires message to not be null <br><br>
        @return:Returns true of this resource contains resolved information
        """
        return self.marked_resolved

    def is_long_form(self) -> bool:
        """
        Returns true if the uResource contains names so that it can be serialized to long format.<br><br>
        @return:Returns true if the uResource contains names so that it can be serialized to long format.
        """
        if self.name == "rpc":
            return bool(self.instance)
        return bool(self.name)

    def is_micro_form(self) -> bool:
        """
        Returns true if the uResource contains the id's which will allow the Uri part to be serialized into micro
        form.<br><br>
        @return:Returns true if the uResource can be serialized into micro form.
        """
        return self.id is not None

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, UResource):
            return False
        return (
                self.marked_resolved == other.marked_resolved and self.name == other.name and self.instance ==
                other.instance and self.message == other.message and self.id == other.id)

    def __hash__(self):
        return hash((self.name, self.instance, self.message, self.id, self.marked_resolved))

    def __str__(self):
        return (f"UResource{{name='{self.name}', instance='{self.instance}', message='{self.message}', id={self.id}, "
                f"markedResolved={self.marked_resolved}}}")


# Initialize EMPTY and RESPONSE
UResource.EMPTY = UResource("", None, None, None, False)
UResource.RESPONSE = UResource("rpc", "response", None, 0, True)
