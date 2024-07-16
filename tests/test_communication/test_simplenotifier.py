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

from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.simplenotifier import SimpleNotifier
from uprotocol.communication.upayload import UPayload
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class TestSimpleNotifier(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.transport = MagicMock(spec=UTransport)
        self.source = UUri(authority_name="neelam", ue_id=3, ue_version_major=1, resource_id=0x8000)
        self.sink = UUri(ue_id=4, ue_version_major=1)

    async def test_send_notification(self):
        self.transport.send.return_value = UStatus(code=UCode.OK)
        notifier = SimpleNotifier(self.transport)
        status = await notifier.notify(self.source, self.sink)
        self.assertEqual(status.code, UCode.OK)
        self.transport.send.assert_called_once()

    async def test_send_notification_with_payload(self):
        self.transport.send.return_value = UStatus(code=UCode.OK)

        uri = UUri(authority_name="Neelam")
        notifier = SimpleNotifier(self.transport)
        status = await notifier.notify(self.source, self.sink, payload=UPayload.pack(uri))
        self.assertEqual(status.code, UCode.OK)
        self.transport.send.assert_called_once()

    async def test_send_notification_with_payload_and_calloptions(self):
        self.transport.send.return_value = UStatus(code=UCode.OK)

        uri = UUri(authority_name="Neelam")
        notifier = SimpleNotifier(self.transport)
        status = await notifier.notify(self.source, self.sink, CallOptions.DEFAULT, UPayload.pack(uri))
        self.assertEqual(status.code, UCode.OK)
        self.transport.send.assert_called_once()

    async def test_register_listener(self):
        self.transport.register_listener.return_value = UStatus(code=UCode.OK)
        self.transport.get_source.return_value = self.source

        class TestListener(UListener):
            def on_receive(self, message: UMessage):
                pass

        listener = TestListener()
        notifier = SimpleNotifier(self.transport)
        status = await notifier.register_notification_listener(self.source, listener)
        self.assertEqual(status.code, UCode.OK)
        self.transport.register_listener.assert_called_once()
        self.transport.get_source.assert_called_once()

    async def test_unregister_notification_listener(self):
        self.transport.register_listener.return_value = UStatus(code=UCode.OK)
        self.transport.get_source.return_value = self.source
        self.transport.unregister_listener.return_value = UStatus(code=UCode.OK)

        class TestListener(UListener):
            def on_receive(self, message: UMessage):
                pass

        listener = TestListener()
        notifier = SimpleNotifier(self.transport)
        status = await notifier.register_notification_listener(self.source, listener)
        self.assertEqual(status.code, UCode.OK)

        status = await notifier.unregister_notification_listener(self.source, listener)
        self.assertEqual(status.code, UCode.OK)
        self.transport.register_listener.assert_called_once()
        self.assertEqual(self.transport.get_source.call_count, 2)
        self.transport.unregister_listener.assert_called_once()

    async def test_unregister_listener_not_registered(self):
        self.transport.get_source.return_value = self.source
        self.transport.unregister_listener.return_value = UStatus(code=UCode.NOT_FOUND)

        class TestListener(UListener):
            def on_receive(self, message: UMessage):
                pass

        listener = TestListener()
        notifier = SimpleNotifier(self.transport)
        status = await notifier.unregister_notification_listener(self.source, listener)
        self.assertEqual(status.code, UCode.NOT_FOUND)
        self.transport.register_listener.assert_not_called()
        self.transport.get_source.assert_called_once()
        self.transport.unregister_listener.assert_called_once()

    def test_simplenotifier_constructor_transport_none(self):
        with self.assertRaises(ValueError) as context:
            SimpleNotifier(None)
        self.assertEqual(str(context.exception), UTransport.TRANSPORT_NULL_ERROR)

    def test_simplenotifier_constructor_transport_not_instance(self):
        with self.assertRaises(ValueError) as context:
            SimpleNotifier("InvalidTransport")
        self.assertEqual(str(context.exception), UTransport.TRANSPORT_NOT_INSTANCE_ERROR)

    async def test_send_notification_with_options(self):
        self.transport.send.return_value = UStatus(code=UCode.OK)
        self.notifier = SimpleNotifier(self.transport)
        result = await self.notifier.notify(self.source, self.sink, CallOptions.DEFAULT)

        self.assertEqual(result.code, UCode.OK)


if __name__ == '__main__':
    unittest.main()
