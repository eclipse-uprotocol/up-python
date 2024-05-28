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

from tests.test_client.utransport_impl import UTransportImpl

from uprotocol.client.publisher import Publisher

from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri
from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UCode


def create_topic():
    return UUri(
        authority_name="hartley",
        ue_id=3,
        ue_version_major=1,
        resource_id=0x8000,
    )


class PublisherImpl(Publisher):
    def __init__(self):
        self.source = UUri(ue_id=1, ue_version_major=1)
        self.mtransport = UTransportImpl(self.source)

    def get_transport(self):
        return self.mtransport


class TestPublisher(unittest.TestCase):

    def test_create_publisher(self):
        """
        Test Creating a Publisher
        """
        publisher: PublisherImpl = PublisherImpl()
        self.assertIsNotNone(publisher)

    def test_publish_api_with_google_protobuf_message(self):
        """
        Test calling publish API with google protobuf message
        """
        publisher: PublisherImpl = PublisherImpl()
        status = publisher.publish(create_topic(), UUri())
        self.assertEqual(status.code, UCode.OK)

    def test_publish_api_without_payload(self):
        """
        Test calling publish API without a payload
        """
        publisher: PublisherImpl = PublisherImpl()
        status = publisher.publish(create_topic())
        self.assertEqual(status.code, UCode.OK)
