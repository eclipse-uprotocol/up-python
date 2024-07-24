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

from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class MyListener(UListener):
    async def on_receive(self, message):
        await super().on_receive(message)
        pass


class HappyUTransport(UTransport):
    async def close(self) -> None:
        pass

    async def send(self, message):
        return UStatus(code=UCode.INVALID_ARGUMENT if message is None else UCode.OK)

    async def register_listener(self, source_filter: UUri, listener: UListener, sink_filter: UUri = None) -> UStatus:
        await listener.on_receive(UMessage())
        return UStatus(code=UCode.OK)

    async def unregister_listener(self, source_filter: UUri, listener, sink_filter: UUri = None):
        return UStatus(code=UCode.OK)

    def get_source(self):
        return UUri()


class SadUTransport(UTransport):
    async def close(self) -> None:
        pass

    async def send(self, message):
        return UStatus(code=UCode.INTERNAL)

    async def register_listener(self, source_filter: UUri, listener: UListener, sink_filter: UUri = None) -> UStatus:
        await listener.on_receive(None)
        return UStatus(code=UCode.INTERNAL)

    async def unregister_listener(self, source_filter: UUri, listener, sink_filter: UUri = None):
        return UStatus(code=UCode.INTERNAL)

    def get_source(self):
        return UUri()


class UTransportTest(unittest.IsolatedAsyncioTestCase):
    async def test_happy_send_message_parts(self):
        transport = HappyUTransport()
        status = await transport.send(UMessage())
        self.assertEqual(status.code, UCode.OK)

    async def test_happy_register_listener(self):
        transport = HappyUTransport()
        status = await transport.register_listener(UUri(), MyListener(), None)
        self.assertEqual(status.code, UCode.OK)

    async def test_happy_register_unlistener(self):
        transport = HappyUTransport()
        status = await transport.unregister_listener(UUri(), MyListener(), None)
        self.assertEqual(status.code, UCode.OK)

    async def test_sending_null_message(self):
        transport = HappyUTransport()
        status = await transport.send(None)
        self.assertEqual(status.code, UCode.INVALID_ARGUMENT)

    async def test_unhappy_send_message_parts(self):
        transport = SadUTransport()
        status = await transport.send(UMessage())
        self.assertEqual(status.code, UCode.INTERNAL)

    async def test_unhappy_register_listener(self):
        transport = SadUTransport()
        status = await transport.register_listener(UUri(), MyListener(), None)
        self.assertEqual(status.code, UCode.INTERNAL)

    async def test_unhappy_register_unlistener(self):
        transport = SadUTransport()
        status = await transport.unregister_listener(UUri(), MyListener(), None)
        self.assertEqual(status.code, UCode.INTERNAL)


if __name__ == "__main__":
    unittest.main()
