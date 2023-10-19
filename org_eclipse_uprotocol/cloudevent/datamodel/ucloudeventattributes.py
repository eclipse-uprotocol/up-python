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

from typing import Optional

from org_eclipse_uprotocol.transport.datamodel.upriority import UPriority


class UCloudEventAttributes:

    def __init__(self, hash_value: str, priority: str, ttl: int, token: str):
        self.hash = hash_value
        self.priority = priority
        self.ttl = ttl
        self.token = token

    @staticmethod
    def empty():
        return UCloudEventAttributes(None, None, None, None)

    def is_empty(self):
        return not any((self.hash, self.priority, self.ttl, self.token))

    def hash(self) -> Optional[str]:
        return None if not self.hash or self.hash.isspace() else self.hash

    def priority(self) -> Optional[str]:
        return self.priority

    def ttl(self) -> Optional[int]:
        return self.ttl

    def token(self) -> Optional[str]:
        return None if not self.token or self.token.isspace() else self.token

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, UCloudEventAttributes):
            return False
        return (
                self.hash == other.hash and self.priority == other.priority and self.ttl == other.ttl and self.token == other.token)

    def __hash__(self):
        return hash((self.hash, self.priority, self.ttl, self.token))

    def __str__(self):
        return f"UCloudEventAttributes{{hash='{self.hash}', priority={self.priority}," \
               f" ttl={self.ttl}, token='{self.token}'}}"


class UCloudEventAttributesBuilder:
    def __init__(self):
        self.hash = None
        self.priority = None
        self.ttl = None
        self.token = None

    def with_hash(self, hash_value: str):
        self.hash = hash_value
        return self

    def with_priority(self, priority: UPriority):
        self.priority = priority
        return self

    def with_ttl(self, ttl: int):
        self.ttl = ttl
        return self

    def with_token(self, token: str):
        self.token = token
        return self

    def build(self):
        return UCloudEventAttributes(self.hash, self.priority.qos_string, self.ttl, self.token)
