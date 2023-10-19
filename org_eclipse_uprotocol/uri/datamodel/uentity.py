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
class UEntity:
    EMPTY = None

    def __init__(self, name: str, version: int, identifier: int, marked_resolved: bool):
        if name is None:
            raise ValueError("Software Entity must have a name")
        self.name = name
        self.version = version
        self.id = identifier
        self.marked_resolved = marked_resolved

    @staticmethod
    def resolved_format(name: str, version: int, identifier: int):
        resolved = name and name.strip() and identifier is not None
        return UEntity(name if name else "", version, identifier, resolved)

    @staticmethod
    def long_format(name: str, version: int):
        return UEntity(name if name else "", version, None, False)

    @staticmethod
    def long_format_name(name: str):
        return UEntity(name if name else "", None, None, False)

    @staticmethod
    def micro_format(identifier: int):
        return UEntity("", None, identifier, False)

    @staticmethod
    def micro_format_id_version(identifier: int, version: int):
        return UEntity("", version, identifier, False)

    @staticmethod
    def empty():
        if UEntity.EMPTY is None:
            UEntity.EMPTY = UEntity("", None, None, False)
        return UEntity.EMPTY

    def is_empty(self) -> bool:
        return not (self.name or self.version or self.id)

    def is_resolved(self) -> bool:
        return self.marked_resolved

    def is_long_form(self) -> bool:
        return bool(self.name)

    def is_micro_form(self) -> bool:
        return self.id is not None

    def get_name(self) -> str:
        return self.name

    def get_version(self) -> int:
        return self.version

    def get_id(self) -> int:
        return self.id

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, UEntity):
            return False
        return (
                self.marked_resolved == other.marked_resolved and self.name == other.name and self.version == other.version and self.id == other.id)

    def __hash__(self):
        return hash((self.name, self.version, self.id, self.marked_resolved))

    def __str__(self):
        return f"UEntity{{name='{self.name}', version={self.version}, id={self.id}, markedResolved={self.marked_resolved}}}"


# Initialize EMPTY
UEntity.EMPTY = UEntity("", None, None, False)
