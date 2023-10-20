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

import ipaddress
from typing import Optional


class UAuthority:
    EMPTY = None

    def __init__(self, device: str, domain: str, address: ipaddress.IPv4Address, marked_remote: bool,
                 marked_resolved: bool):
        self.device = device.lower() if device else None
        self.domain = domain.lower() if domain else None
        self.address = address
        self.marked_remote = marked_remote
        self.marked_resolved = marked_resolved

    @staticmethod
    def local():
        return UAuthority.EMPTY

    @staticmethod
    def long_remote(device: str, domain: str):

        return UAuthority(device, domain, None, True, False)

    @staticmethod
    def micro_remote(address: ipaddress.IPv4Address):
        return UAuthority(None, None, address, True, False)

    @staticmethod
    def resolved_remote(device: str, domain: str, address: ipaddress.IPv4Address):
        resolved = device is not None and device.strip() != "" and address is not None
        return UAuthority(device, domain, address, True, resolved)

    @staticmethod
    def empty():

        return UAuthority.EMPTY

    def is_remote(self) -> bool:
        return self.is_marked_Remote()

    #
    def is_local(self) -> bool:
        return self.is_empty() and not self.is_marked_Remote()

    def is_marked_Remote(self) -> bool:
        return self.marked_remote

    def device(self) -> Optional[str]:
        return self.device if self.device else None

    def domain(self) -> Optional[str]:
        return self.domain if self.domain else None

    def address(self) -> Optional[ipaddress.IPv4Address]:
        try:
            return ipaddress.IPv4Address(self.address)
        except ValueError:
            return None

    def is_marked_remote(self) -> bool:
        return self.marked_remote

    def is_resolved(self) -> bool:
        return self.marked_resolved

    def is_long_form(self) -> bool:
        return self.is_local() or self.device is not None

    def is_micro_form(self) -> bool:
        return self.is_local() or self.address is not None

    def is_empty(self) -> bool:
        return all([self.domain is None or self.domain.strip() == "", self.device is None or self.device.strip() == "",
                    self.address is None])

    def __eq__(self, other):
        if not isinstance(other, UAuthority):
            return False
        return (
                self.marked_remote == other.marked_remote and self.device == other.device and self.domain == other.domain)

    def __hash__(self):
        return hash((self.device, self.domain, self.marked_remote))

    def __str__(self):
        return f"UAuthority{{device='{self.device}', domain='{self.domain}', markedRemote={self.marked_remote}}}"


# Initialize EMPTY
UAuthority.EMPTY = UAuthority(None, None, None, False, True)
