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

import unittest
import socket

from uprotocol.proto.uri_pb2 import UAuthority, UEntity, UResource, UUri
from uprotocol.uri.factory.uentity_factory import UEntityFactory
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.uri.serializer.microuriserializer import MicroUriSerializer
from uprotocol.uri.serializer.shorturiserializer import ShortUriSerializer

from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.proto.core.usubscription.v3.usubscription_pb2 import (
    DESCRIPTOR as USubscriptionFileDescriptor,
)
from uprotocol.proto.uprotocol_options_pb2 import (
    notification_topic as Notification_Topic,
)
from uprotocol.proto.uprotocol_options_pb2 import UServiceTopic

from google.protobuf.descriptor import ServiceDescriptor, FileDescriptor
from google.protobuf.descriptor_pb2 import ServiceOptions
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer


class TestUriSerializer(unittest.TestCase):

    def get_uresource(
        self, container: RepeatedCompositeFieldContainer
    ) -> UResource:
        if len(container) == 0:
            resrc = UResource()
        else:
            first_topic: UServiceTopic = container[0]
            id: int = first_topic.id
            name: str = first_topic.name
            message: str = first_topic.message

            resrc = UResource()
            if id is not None:
                resrc.id = id
            if name is not None:
                resrc.name = name
            if message is not None:
                resrc.message = message
        return resrc

    def check_given_test_data_is_formed_correctly(self, uuri: UUri):
        self.assertFalse(UriValidator.is_empty(uuri))
        self.assertTrue(UriValidator.is_micro_form(uuri))
        self.assertTrue(UriValidator.is_long_form(uuri))
        self.assertTrue(UriValidator.is_short_form(uuri))

    def test_build_resolved_full_information_compare(self):

        file_descriptor: FileDescriptor = USubscriptionFileDescriptor
        service_descriptor: ServiceDescriptor = (
            file_descriptor.services_by_name["uSubscription"]
        )
        options: ServiceOptions = service_descriptor.GetOptions()
        container: RepeatedCompositeFieldContainer = options.Extensions[
            Notification_Topic
        ]

        uresrc: UResource = self.get_uresource(container)
        uentity: UEntity = UEntityFactory.from_proto(service_descriptor)
        uuri: UUri = UUri(entity=uentity, resource=uresrc)

        actual_long_uri: str = LongUriSerializer().serialize(uuri)
        actual_short_uri: str = ShortUriSerializer().serialize(uuri)
        actual_micro_uri: bytes = MicroUriSerializer().serialize(uuri)

        expected_longuri_given_no_uauthority: str = (
            "/core.usubscription/3/SubscriptionChange#Update"
        )
        expected_shorturi_given_no_uauthority: str = "/0/3/32768"
        expected_micro_uri_given_no_uauthority = bytearray(
            b"\x01\x00\x80\x00\x00\x00\x03\x00"
        )

        self.check_given_test_data_is_formed_correctly(uuri)

        self.assertEqual(expected_longuri_given_no_uauthority, actual_long_uri)
        self.assertEqual(
            expected_shorturi_given_no_uauthority, actual_short_uri
        )
        self.assertEqual(
            expected_micro_uri_given_no_uauthority, actual_micro_uri
        )

    def test_build_resolved_full_information_compare_with_ipv4(self):
        file_descriptor: FileDescriptor = USubscriptionFileDescriptor
        service_descriptor: ServiceDescriptor = (
            file_descriptor.services_by_name["uSubscription"]
        )
        options: ServiceOptions = service_descriptor.GetOptions()
        container: RepeatedCompositeFieldContainer = options.Extensions[
            Notification_Topic
        ]

        uresrc: UResource = self.get_uresource(container)
        uentity: UEntity = UEntityFactory.from_proto(service_descriptor)

        ipv4_address: str = "192.168.1.100"
        ipv4_packed_ip: bytes = socket.inet_pton(socket.AF_INET, ipv4_address)

        authority: UAuthority = UAuthority(
            name="vcu.veh.gm.com", ip=ipv4_packed_ip
        )
        uuri: UUri = UUri(entity=uentity, resource=uresrc, authority=authority)

        self.check_given_test_data_is_formed_correctly(uuri)

        actual_long_uri: str = LongUriSerializer().serialize(uuri)
        actual_short_uri: str = ShortUriSerializer().serialize(uuri)
        actual_micro_uri: bytes = MicroUriSerializer().serialize(uuri)

        expected_longuri_given_ipv4_uathority: str = (
            "//vcu.veh.gm.com/core.usubscription/3/SubscriptionChange#Update"
        )
        expected_shorturi_given_ipv4_uathority: str = (
            "//192.168.1.100/0/3/32768"
        )
        expected_microuri_given_ipv4_uathority = bytearray(
            b"\x01\x01\x80\x00\x00\x00\x03\x00\xc0\xa8\x01d"
        )

        self.assertEqual(
            expected_longuri_given_ipv4_uathority, actual_long_uri
        )
        self.assertEqual(
            expected_shorturi_given_ipv4_uathority, actual_short_uri
        )
        self.assertEqual(
            expected_microuri_given_ipv4_uathority, actual_micro_uri
        )

    def test_build_resolved_full_information_compare_with_id(self):
        file_descriptor: FileDescriptor = USubscriptionFileDescriptor
        service_descriptor: ServiceDescriptor = (
            file_descriptor.services_by_name["uSubscription"]
        )
        options: ServiceOptions = service_descriptor.GetOptions()
        container: RepeatedCompositeFieldContainer = options.Extensions[
            Notification_Topic
        ]

        uresrc: UResource = self.get_uresource(container)
        uentity: UEntity = UEntityFactory.from_proto(service_descriptor)

        authority: UAuthority = UAuthority(
            name="1G1YZ23J9P5800001.veh.gm.com", id=b"1G1YZ23J9P5800001"
        )
        uuri: UUri = UUri(entity=uentity, resource=uresrc, authority=authority)

        self.check_given_test_data_is_formed_correctly(uuri)

        actual_long_uri: str = LongUriSerializer().serialize(uuri)
        actual_short_uri: str = ShortUriSerializer().serialize(uuri)
        actual_micro_uri: bytes = MicroUriSerializer().serialize(uuri)

        expected_longuri_given_id_uathority: str = (
            "//1G1YZ23J9P5800001.veh.gm.com/core.usubscription/3/SubscriptionChange#Update"
        )
        expected_shorturi_given_id_uathority: str = (
            "//1G1YZ23J9P5800001/0/3/32768"
        )
        expected_microuri_given_id_uathority = bytearray(
            b"\x01\x03\x80\x00\x00\x00\x03\x00\x111G1YZ23J9P5800001"
        )

        self.assertEqual(expected_longuri_given_id_uathority, actual_long_uri)
        self.assertEqual(
            expected_shorturi_given_id_uathority, actual_short_uri
        )
        self.assertEqual(
            expected_microuri_given_id_uathority, actual_micro_uri
        )

    def test_build_resolved_full_information_compare_with_ipv6(self):
        file_descriptor: FileDescriptor = USubscriptionFileDescriptor
        service_descriptor: ServiceDescriptor = (
            file_descriptor.services_by_name["uSubscription"]
        )
        options: ServiceOptions = service_descriptor.GetOptions()
        container: RepeatedCompositeFieldContainer = options.Extensions[
            Notification_Topic
        ]

        uresrc: UResource = self.get_uresource(container)
        uentity: UEntity = UEntityFactory.from_proto(service_descriptor)

        # inet_pton(): Convert IP address from its family-specific string format -> a packed, binary format
        ipv6_address: str = "2001:db8:85a3:0:0:8a2e:370:7334"
        ipv6_packed_ip: bytes = socket.inet_pton(socket.AF_INET6, ipv6_address)

        authority: UAuthority = UAuthority(
            name="vcu.veh.gm.com", ip=ipv6_packed_ip
        )
        uuri: UUri = UUri(entity=uentity, resource=uresrc, authority=authority)

        self.check_given_test_data_is_formed_correctly(uuri)

        actual_long_uri: str = LongUriSerializer().serialize(uuri)
        actual_short_uri: str = ShortUriSerializer().serialize(uuri)
        actual_micro_uri: bytes = MicroUriSerializer().serialize(uuri)

        expected_longuri_given_ipv6_uathority: str = (
            "//vcu.veh.gm.com/core.usubscription/3/SubscriptionChange#Update"
        )
        expected_shorturi_given_ipv6_uathority: str = (
            "//2001:db8:85a3::8a2e:370:7334/0/3/32768"
        )
        expected_microuri_given_ipv6_uathority = bytearray(
            b"\x01\x02\x80\x00\x00\x00\x03\x00 \x01\r\xb8\x85\xa3\x00\x00\x00\x00\x8a.\x03ps4"
        )

        self.assertEqual(
            expected_longuri_given_ipv6_uathority, actual_long_uri
        )
        self.assertEqual(
            expected_shorturi_given_ipv6_uathority, actual_short_uri
        )
        self.assertEqual(
            expected_microuri_given_ipv6_uathority, actual_micro_uri
        )


if __name__ == "__main__":
    unittest.main()
