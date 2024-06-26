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
from uprotocol.communication.simplenotifier import SimpleNotifier
from uprotocol.communication.upayload import UPayload
from uprotocol.transport.ulistener import UListener
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri


class TestSimpleNotifier(unittest.TestCase):
    def create_topic(self):
        return UUri(authority_name="neelam", ue_id=3, ue_version_major=1, resource_id=0x8000)

    def create_destination_uri(self):
        return UUri(ue_id=4, ue_version_major=1)

    def test_send_notification(self):
        notifier = SimpleNotifier(MockUTransport())
        status = notifier.notify(self.create_topic(), self.create_destination_uri(), None)
        self.assertEqual(status.code, UCode.OK)

    def test_send_notification_with_payload(self):
        uri = UUri(authority_name="Neelam")
        notifier = SimpleNotifier(MockUTransport())
        status = notifier.notify(self.create_topic(), self.create_destination_uri(), UPayload.pack(uri))
        self.assertEqual(status.code, UCode.OK)

    def test_register_listener(self):
        class TestListener(UListener):
            def on_receive(self, message: UMessage):
                pass

        listener = TestListener()
        notifier = SimpleNotifier(MockUTransport())
        status = notifier.register_notification_listener(self.create_topic(), listener)
        self.assertEqual(status.code, UCode.OK)

    def test_unregister_notification_listener(self):
        class TestListener(UListener):
            def on_receive(self, message: UMessage):
                pass

        listener = TestListener()
        notifier = SimpleNotifier(MockUTransport())
        status = notifier.register_notification_listener(self.create_topic(), listener)
        self.assertEqual(status.code, UCode.OK)

        status = notifier.unregister_notification_listener(self.create_topic(), listener)
        self.assertEqual(status.code, UCode.OK)

    def test_unregister_listener_not_registered(self):
        class TestListener(UListener):
            def on_receive(self, message: UMessage):
                pass

        listener = TestListener()
        notifier = SimpleNotifier(MockUTransport())
        status = notifier.unregister_notification_listener(self.create_topic(), listener)
        self.assertEqual(status.code, UCode.INVALID_ARGUMENT)


if __name__ == '__main__':
    unittest.main()
