"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import unittest

from tests.test_communication.mock_utransport import MockUTransport
from uprotocol.communication.simplepublisher import SimplePublisher
from uprotocol.communication.upayload import UPayload
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.uri_pb2 import UUri


class TestSimplePublisher(unittest.TestCase):
    def create_topic(self):
        return UUri(authority_name="neelam", ue_id=3, ue_version_major=1, resource_id=0x8000)

    def test_send_publish(self):
        publisher = SimplePublisher(MockUTransport())
        status = publisher.publish(self.create_topic(), None)
        self.assertEqual(status.code, UCode.OK)

    def test_send_publish_with_stuffed_payload(self):
        uri = UUri(authority_name="Neelam")
        publisher = SimplePublisher(MockUTransport())
        status = publisher.publish(self.create_topic(), UPayload.pack_to_any(uri))
        self.assertEqual(status.code, UCode.OK)


if __name__ == '__main__':
    unittest.main()
