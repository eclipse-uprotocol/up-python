"""
SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to the
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

import socket


class IpAddress:
    @staticmethod
    def to_bytes(ip_address):
        if ip_address is None or ip_address.strip() == "":
            return b""

        if IpAddress.is_valid_ipv4_address(ip_address):
            return IpAddress.convert_ipv4_to_byte_array(ip_address)
        elif IpAddress.is_valid_ipv6_address(ip_address):
            return IpAddress.convert_ipv6_to_byte_array(ip_address)
        else:
            return b""

    @staticmethod
    def is_valid(ip_address):
        return (
            (ip_address is not None)
            and not ip_address.strip() == ""
            and (IpAddress.is_valid_ipv4_address(ip_address) or IpAddress.is_valid_ipv6_address(ip_address))
        )

    @staticmethod
    def is_valid_ipv4_address(ip_address):
        try:
            return len(ip_address.split(".")) == 4 and socket.inet_pton(socket.AF_INET, ip_address)
        except OSError:
            return False

    @staticmethod
    def convert_ipv4_to_byte_array(ip_address):
        return bytes(socket.inet_pton(socket.AF_INET, ip_address))

    @staticmethod
    def is_valid_ipv6_address(ip_address):
        try:
            return len(ip_address.split(":")) <= 8 and socket.inet_pton(socket.AF_INET6, ip_address)
        except OSError:
            return False

    @staticmethod
    def convert_ipv6_to_byte_array(ip_address):
        return bytes(socket.inet_pton(socket.AF_INET6, ip_address))
