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
from unittest.mock import MagicMock

from uprotocol.communication.simplepublisher import SimplePublisher
from uprotocol.communication.upayload import UPayload
from uprotocol.transport.utransport import UTransport
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class TestSimplePublisher(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.transport = MagicMock(spec=UTransport)
        self.topic = UUri(authority_name="neelam", ue_id=3, ue_version_major=1, resource_id=2)

    async def test_send_publish(self):
        self.transport.send.return_value = UStatus(code=UCode.OK)
        publisher = SimplePublisher(self.transport)
        status = await publisher.publish(self.topic)
        self.assertEqual(status.code, UCode.OK)
        self.transport.send.assert_called_once()

    async def test_send_publish_with_stuffed_payload(self):
        self.transport.send.return_value = UStatus(code=UCode.OK)
        uri = UUri(authority_name="Neelam")
        publisher = SimplePublisher(self.transport)
        status = await publisher.publish(self.topic, payload=UPayload.pack_to_any(uri))
        self.assertEqual(status.code, UCode.OK)
        self.transport.send.assert_called_once()

    def test_constructor_transport_none(self):
        with self.assertRaises(ValueError) as context:
            SimplePublisher(None)
        self.assertEqual(str(context.exception), UTransport.TRANSPORT_NULL_ERROR)

    def test_constructor_transport_not_instance(self):
        with self.assertRaises(ValueError) as context:
            SimplePublisher("InvalidTransport")
        self.assertEqual(str(context.exception), UTransport.TRANSPORT_NOT_INSTANCE_ERROR)

    async def test_publish_topic_none(self):
        publisher = SimplePublisher(self.transport)
        uri = UUri(authority_name="Neelam")
        with self.assertRaises(ValueError) as context:
            await publisher.publish(None, payload=UPayload.pack_to_any(uri))
        self.assertEqual(str(context.exception), "Publish topic missing")


if __name__ == '__main__':
    unittest.main()
