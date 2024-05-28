"""
SPDX-FileCopyrightText: Copyright (c) 2023 Contributors to the
Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SPDX-FileType: SOURCE
SPDX-License-Identifier: Apache-2.0
"""

from uprotocol.proto.uprotocol.v1.uattributes_pb2 import UPriority


class CallOptions:
    """
    This class is used when making uRPC calls to pass additional
    options to the call.
    """

    TIMEOUT_DEFAULT = 10000

    def __init__(
        self,
        timeout: int = TIMEOUT_DEFAULT,
        priority: UPriority = UPriority.UPRIORITY_CS4,
        token: str = "",
    ):
        self.timeout = timeout
        self.priority = priority
        self.token = token if token is not None else ""

    def with_timeout(self, timeout: int):
        """
        Add the timeout.

        @param timeout    the timeout.
        @return Returns the CallOptions with the configured
        timeout.
        """
        self.timeout = (
            timeout if timeout > 0 else CallOptions.TIMEOUT_DEFAULT
        )
        return self

    def with_priority(self, priority: int):
        """
        Add the priority.

        @param priority    the priority.
        @return Returns the CallOptions with the configured
        priority.
        """
        self.priority = (
            UPriority.UPRIORITY_CS4
            if priority is None or priority < UPriority.UPRIORITY_CS4
            else priority
        )
        return self

    def with_token(self, token: str):
        """
        Add an OAuth2 access token.

        @param token    An OAuth2 access token.
        @return Returns the CallOptions with the configured
        token.
        """
        self.token = token
        return self

    def build(self):
        """
        Construct the CallOptions from the builder.

        @return Returns a constructed CallOptions
        """

        call_options = CallOptions(
            timeout=self.timeout,
            priority=self.priority,
            token=self.token,
        )

        return call_options

    def equals(self, o):
        if o is None or not isinstance(o, self):
            return False
        return self.timeout == o.timeout and self.token == o.m_token

    def hash_code(self):
        return hash(self)

    def to_string(self):
        return (
            "CallOptions{"
            + "mTimeout="
            + self.timeout
            + ", mToken='"
            + self.token
            + "'"
            + "}"
        )
