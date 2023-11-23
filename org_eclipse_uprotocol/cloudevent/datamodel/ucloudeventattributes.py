# -------------------------------------------------------------------------

# Copyright (c) 2023 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: 2023 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0

# -------------------------------------------------------------------------

from typing import Optional

from org_eclipse_uprotocol.proto.uattributes_pb2 import UPriority
from org_eclipse_uprotocol.proto.uattributes_pb2 import UPriority


class UCloudEventAttributes:
    """
    Specifies the properties that can configure the UCloudEvent.
    """

    def __init__(self, priority: UPriority, hash_value: str = None, ttl: int = None, token: str = None):
        """
        Construct the properties object.<br><br>
        @param hash_value: an HMAC generated on the data portion of the CloudEvent message using the device key.
        @param priority: uProtocol Prioritization classifications.
        @param ttl: How long this event should live for after it was generated (in milliseconds). Events without this
        attribute (or value is 0) MUST NOT timeout.
        @param token: Oauth2 access token to perform the access request defined in the request message.
        """
        self.hash = hash_value
        self.priority = priority
        self.ttl = ttl
        self.token = token

    @staticmethod
    def empty():
        """
        Static factory method for creating an empty  cloud event attributes object, to avoid working with null<br><br>
        @return: Returns an empty  cloud event attributes that indicates that there are no added additional
        attributes to configure.
        """
        return UCloudEventAttributes(None, None, None, None)

    def is_empty(self):
        """
        Indicates that there are no added additional attributes to configure when building a CloudEvent.<br><br>
        @return: Returns true if this attributes container is an empty container and has no valuable information in
        building a CloudEvent.
        """
        return (self.hash is None or self.hash.isspace()) and (self.ttl is None) and (
                    self.token is None or self.token.isspace()) and (self.priority is None or self.priority.isspace())

    def get_hash(self) -> str:
        """
        An HMAC generated on the data portion of the CloudEvent message using the device key.<br><br>
        @return: Returns an Optional hash attribute.
        """
        return self.hash if self.hash and self.hash.strip() else None

    def get_priority(self) -> UPriority:
        """
        uProtocol Prioritization classifications.<br><br>
        @return: Returns an Optional priority attribute.
        """
        return self.priority

    def get_ttl(self) -> int:
        """
        How long this event should live for after it was generated (in milliseconds).<br><br>
        @return: Returns an Optional time to live attribute.
        """
        return self.ttl

    def get_token(self) -> str:
        """
        Oauth2 access token to perform the access request defined in the request message.<br><br>
        @return: Returns an Optional OAuth token attribute.
        """
        return self.token if self.token and self.token.strip() else None

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, UCloudEventAttributes):
            return False
        return (
                self.hash == other.hash and self.priority == other.priority and self.ttl == other.ttl and self.token
                == other.token)

    def __hash__(self):
        return hash((self.hash, self.priority, self.ttl, self.token))

    def __str__(self):
        return f"UCloudEventAttributes{{hash='{self.hash}', priority={self.priority}," \
               f" ttl={self.ttl}, token='{self.token}'}}"


class UCloudEventAttributesBuilder:
    """
    Builder for constructing the UCloudEventAttributes.
    """

    def __init__(self):
        self.hash = None
        self.priority = None
        self.ttl = None
        self.token = None

    def with_hash(self, hash_value: str):
        """
        Add an HMAC generated on the data portion of the CloudEvent message using the device key.<br><br>
        @param hash_value: hash an HMAC generated on the data portion of the CloudEvent message using the device key.
        @return:  Returns the UCloudEventAttributesBuilder with the configured hash.
        """
        self.hash = hash_value
        return self

    def with_priority(self, priority: UPriority):
        """
        Add a uProtocol Prioritization classifications.<br><br>
        @param priority: priority uProtocol Prioritization classifications.
        @return: Returns the UCloudEventAttributesBuilder with the configured priority.
        """
        self.priority = UPriority.Name(priority)
        return self

    def with_ttl(self, ttl: int):
        """
        Add a time to live which is how long this event should live for after it was generated (in milliseconds).
        Events without this attribute (or value is 0) MUST NOT timeout.<br><br>
        @param ttl: How long this event should live for after it was generated (in milliseconds). Events without this
        attribute (or value is 0) MUST NOT timeout.
        @return: Returns the UCloudEventAttributesBuilder with the configured time to live.
        """
        self.ttl = ttl
        return self

    def with_token(self, token: str):
        """
        Add an Oauth2 access token to perform the access request defined in the request message.<br><br>
        @param token: An Oauth2 access token to perform the access request defined in the request message.
        @return: Returns the UCloudEventAttributesBuilder with the configured OAuth token.
        """
        self.token = token
        return self

    def build(self):
        """
        Construct the UCloudEventAttributes from the builder.<br><br>
        @return: Returns a constructed UProperty.
        """
        return UCloudEventAttributes(self.priority, self.hash, self.ttl, self.token)


if __name__ == "__main__":
    # Example usage:
    attributes = UCloudEventAttributesBuilder().with_hash("abc123").with_priority(UPriority.UPRIORITY_CS0).with_ttl(
        1000).with_token("xyz456").build()
    print(attributes)
