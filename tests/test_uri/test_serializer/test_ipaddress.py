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

import socket
import unittest

from uprotocol.uri.serializer.ipaddress import IpAddress


class TestIpAddress(unittest.TestCase):
    def test_to_bytes_with_null_ip_address(self):
        bytes_ = IpAddress.to_bytes(None)
        self.assertEqual(len(bytes_), 0)

    def test_to_bytes_with_empty_ip_address(self):
        bytes_ = IpAddress.to_bytes("")
        self.assertEqual(len(bytes_), 0)

    def test_to_bytes_with_invalid_ip_address(self):
        bytes_ = IpAddress.to_bytes("invalid")
        self.assertEqual(len(bytes_), 0)

    def test_to_bytes_with_valid_ipv4_address(self):
        bytes_ = IpAddress.to_bytes("192.168.1.100")
        self.assertEqual(len(bytes_), 4)
        self.assertEqual(socket.inet_ntoa(bytes_), "192.168.1.100")

    def test_to_bytes_with_valid_ipv6_address(self):
        bytes_ = IpAddress.to_bytes("2001:db8:85a3:0:0:8a2e:370:7334")
        self.assertEqual(len(bytes_), 16)
        self.assertEqual(
            socket.inet_ntop(socket.AF_INET6, bytes_),
            "2001:db8:85a3::8a2e:370:7334",
        )

    def test_is_valid_with_null_ip_address(self):
        self.assertFalse(IpAddress.is_valid(None))

    def test_is_valid_with_empty_ip_address(self):
        self.assertFalse(IpAddress.is_valid(""))

    def test_is_valid_with_invalid_ip_address(self):
        self.assertFalse(IpAddress.is_valid("invalid"))

    def test_is_valid_with_valid_ipv4_address(self):
        self.assertTrue(IpAddress.is_valid("192.168.1.100"))

    def test_is_valid_with_valid_ipv6_address(self):
        self.assertTrue(IpAddress.is_valid("2001:db8:85a3:0:0:8a2e:370:7334"))

    def test_is_valid_with_invalid_ipv4_address(self):
        self.assertFalse(IpAddress.is_valid("192.168.1.2586"))

    def test_is_valid_with_invalid_ipv4_passing_large_number(self):
        self.assertFalse(IpAddress.is_valid("2875687346587326457836485623874658723645782364875623847562378465.1.1.abc"))

    def test_is_valid_with_invalid_ipv4_passing_negative(self):
        self.assertFalse(IpAddress.is_valid("-1.1.1.abc"))

    def test_is_valid_with_invalid_ipv4_passing_characters(self):
        self.assertFalse(IpAddress.is_valid("1.1.1.abc"))

    def test_is_valid_with_invalid_ipv6_address(self):
        self.assertFalse(IpAddress.is_valid("ZX1:db8::"))

    def test_is_valid_with_invalid_ipv6_address_passing_weird_values(self):
        self.assertFalse(IpAddress.is_valid("-1:ZX1:db8::"))

    def test_is_valid_with_invalid_ipv6_address_that_has_way_too_many_groups(
        self,
    ):
        self.assertFalse(IpAddress.is_valid("2001:db8:85a3:0:0:8a2e:370:7334:1234"))

    def test_is_valid_with_valid_ipv6_address_that_has_8_groups(self):
        self.assertTrue(IpAddress.is_valid("2001:db8:85a3:0:0:8a2e:370:7334"))

    def test_is_valid_with_invalid_ipv6_address_with_too_many_empty_groups(
        self,
    ):
        self.assertFalse(IpAddress.is_valid("2001::85a3::8a2e::7334"))

    def test_is_valid_with_valid_ipv6_address_with_one_empty_group(self):
        self.assertTrue(IpAddress.is_valid("2001:db8:85a3::8a2e:370:7334"))

    def test_is_valid_with_invalid_ipv6_address_that_ends_with_a_colon(self):
        self.assertFalse(IpAddress.is_valid("2001:db8:85a3::8a2e:370:7334:"))

    def test_is_valid_with_invalid_ipv6_address_that_doesnt_have_double_colon_and_not_enough_groups(
        self,
    ):
        self.assertFalse(IpAddress.is_valid("2001:db8:85a3:0:0:8a2e:370"))

    def test_is_valid_with_valid_ipv6_address_that_ends_with_double_colons(
        self,
    ):
        self.assertTrue(IpAddress.is_valid("2001:db8:85a3:8a2e::"))

    def test_is_valid_with_all_number_values(self):
        self.assertTrue(IpAddress.is_valid("123:456:7890::"))

    def test_is_valid_with_valid_lowercase_hexidecimal_letters(self):
        self.assertTrue(IpAddress.is_valid("abcd:ef12:3456::"))

    def test_is_valid_with_valid_uppercase_hexidecimal_letters(self):
        self.assertTrue(IpAddress.is_valid("ABCD:EF12:3456::"))

    def test_is_valid_with_invalid_uppercase_hexidecimal_letters(self):
        self.assertFalse(IpAddress.is_valid("ABCD:EFG2:3456::"))

    def test_is_valid_with_invalid_lowercase_hexidecimal_letters(self):
        self.assertFalse(IpAddress.is_valid("-C=[]:E{12g:3456"))

    def test_is_valid_with_invalid_digit1(self):
        self.assertFalse(IpAddress.is_valid("aC=[]:E{12g:3456"))

    def test_is_valid_with_invalid_digit2(self):
        self.assertFalse(IpAddress.is_valid("aCd[:E{12g:3456"))

    def test_is_valid_with_invalid_digit3(self):
        self.assertFalse(IpAddress.is_valid("aCd:E{2g:3456"))

    def test_is_valid_with_invalid_ipv6_address_that_has_double_colon_and_8_groups(
        self,
    ):
        self.assertTrue(IpAddress.is_valid("dead:beef:85a3::0:0:8a2e:370"))

    def test_is_valid_with_invalid_ipv6_address_that_has_only_7_groups(self):
        self.assertFalse(IpAddress.is_valid("dead:beef:85a3:0:0:8a2e:370"))


if __name__ == "__main__":
    unittest.main()
