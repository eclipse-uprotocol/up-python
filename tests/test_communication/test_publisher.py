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
from uprotocol.communication.uclient import UClient
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.uri_pb2 import UUri


class TestPublisher(unittest.TestCase):
    def test_send_publish(self):
        # Topic to publish
        topic = UUri(ue_id=4, ue_version_major=1, resource_id=0x8000)

        # Mock transport to use
        transport = MockUTransport()

        # Create publisher instance using mock transport
        publisher = UClient(transport)

        # Send the publish message
        status = publisher.publish(topic, None)
        # Assert that the status code is OK
        self.assertEqual(status.code, UCode.OK)


if __name__ == '__main__':
    unittest.main()
