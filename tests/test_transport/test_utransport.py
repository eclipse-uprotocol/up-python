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

from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.proto.umessage_pb2 import UMessage
import unittest
from uprotocol.proto.uri_pb2 import UUri


class MyListener(UListener):
    def on_receive(self, message):
        super().on_receive(message)
        pass


class HappyUTransport(UTransport):

    def send(self, message):
        super().send(message)

        return UStatus(
            code=UCode.INVALID_ARGUMENT if message is None else UCode.OK
        )

    def register_listener(self, topic, listener):
        super().register_listener(topic, listener)
        listener.on_receive(UMessage())
        return UStatus(code=UCode.OK)

    def unregister_listener(self, topic, listener):
        super().unregister_listener(topic, listener)
        return UStatus(code=UCode.OK)


class SadUTransport(UTransport):
    def send(self, message):
        super().send(message)
        return UStatus(code=UCode.INTERNAL)

    def register_listener(self, topic, listener):
        super().register_listener(topic, listener)
        listener.on_receive(None)
        return UStatus(code=UCode.INTERNAL)

    def unregister_listener(self, topic, listener):
        super().unregister_listener(topic, listener)
        return UStatus(code=UCode.INTERNAL)


class UTransportTest(unittest.TestCase):
    def test_happy_send_message_parts(self):
        transport = HappyUTransport()
        status = transport.send(UMessage())
        self.assertEqual(status.code, UCode.OK)

    def test_happy_send_message(self):
        transport = HappyUTransport()
        status = transport.send(UMessage())
        self.assertEqual(status.code, UCode.OK)

    def test_happy_register_listener(self):
        transport = HappyUTransport()
        status = transport.register_listener(UUri(), MyListener())
        self.assertEqual(status.code, UCode.OK)

    def test_happy_register_unlistener(self):
        transport = HappyUTransport()
        status = transport.unregister_listener(UUri(), MyListener())
        self.assertEqual(status.code, UCode.OK)

    def test_sending_null_message(self):
        transport = HappyUTransport()
        status = transport.send(None)
        self.assertEqual(status.code, UCode.INVALID_ARGUMENT)

    def test_unhappy_send_message_parts(self):
        transport = SadUTransport()
        status = transport.send(UMessage())
        self.assertEqual(status.code, UCode.INTERNAL)

    def test_unhappy_send_message(self):
        transport = SadUTransport()
        status = transport.send(UMessage())
        self.assertEqual(status.code, UCode.INTERNAL)

    def test_unhappy_register_listener(self):
        transport = SadUTransport()
        status = transport.register_listener(UUri(), MyListener())
        self.assertEqual(status.code, UCode.INTERNAL)

    def test_unhappy_register_unlistener(self):
        transport = SadUTransport()
        status = transport.unregister_listener(UUri(), MyListener())
        self.assertEqual(status.code, UCode.INTERNAL)


if __name__ == "__main__":
    unittest.main()
