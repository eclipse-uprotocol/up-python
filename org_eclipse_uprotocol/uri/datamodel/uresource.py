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
    EMPTY = None
    RESPONSE = None

    def __init__(self, name: str, instance: str, message: str, identifier: int, marked_resolved: bool):
        self.name = name if name else ""
        self.instance = instance
        self.message = message
        self.id = identifier
        self.marked_resolved = marked_resolved

    @staticmethod
    def resolved_format(name: str, instance: str, message: str, identifier: int):
        resolved = name and name.strip() and identifier is not None
        return UResource(name if name else "", instance, message, identifier, resolved)

    @staticmethod
    def long_format(name: str):
        return UResource(name if name else "", None, None, None, False)

    @staticmethod
    def long_format_instance_message(name: str, instance: str, message: str):
        return UResource(name if name else "", instance, message, None, False)

    @staticmethod
    def micro_format(identifier: int):
        return UResource("", None, None, identifier, False)

    @staticmethod
    def for_rpc_request(method_name: str):
        return UResource("rpc", method_name, None, None, False)

    @staticmethod
    def for_rpc_request_with_id(method_id: int):
        return UResource("rpc", None, None, method_id, False)

    @staticmethod
    def for_rpc_request_with_name_and_id(method_name: str, method_id: int):
        resolved = method_name and method_name.strip() and method_id is not None
        return UResource("rpc", method_name, None, method_id, resolved)

    @staticmethod
    def for_rpc_response():
        return UResource.RESPONSE

    def is_rpc_method(self) -> bool:
        return self.name == "rpc"

    @staticmethod
    def empty():
        if UResource.EMPTY is None:
            UResource.EMPTY = UResource("", None, None, None, False)
        return UResource.EMPTY

    def is_empty(self) -> bool:
        return not (self.name and self.name.strip()) or self.name == "rpc" and not (
                self.instance or self.message or self.id)

    def get_name(self) -> str:
        return self.name

    def get_id(self) -> int:
        return self.id

    def get_instance(self) -> str:
        return self.instance

    def get_message(self) -> str:
        return self.message

    def is_resolved(self) -> bool:
        return self.marked_resolved

    def is_long_form(self) -> bool:
        if self.name == "rpc":
            return bool(self.instance)
        return bool(self.name)

    def is_micro_form(self) -> bool:
        return self.id is not None

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, UResource):
            return False
        return (
                self.marked_resolved == other.marked_resolved and self.name == other.name and self.instance == other.instance and self.message == other.message and self.id == other.id)

    def __hash__(self):
        return hash((self.name, self.instance, self.message, self.id, self.marked_resolved))

    def __str__(self):
        return f"UResource{{name='{self.name}', instance='{self.instance}', message='{self.message}', id={self.id}, markedResolved={self.marked_resolved}}}"


# Initialize EMPTY and RESPONSE
UResource.EMPTY = UResource("", None, None, None, False)
UResource.RESPONSE = UResource("rpc", "response", None, 0, True)
