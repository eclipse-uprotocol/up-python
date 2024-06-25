"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import asyncio
import unittest

from tests.test_communication.mock_utransport import MockUTransport
from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.upclient import UPClient
from uprotocol.core.usubscription.v3.usubscription_pb2 import (
    SubscriptionStatus,
)
from uprotocol.transport.ulistener import UListener
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri

transport = MockUTransport()
subscriber = UPClient(transport)


class TestSubscriber(unittest.TestCase):
    # Listener to receive published messages on
    class MyListener(UListener):
        def on_receive(self, umsg: UMessage) -> None:
            # Handle receiving subscriptions here
            print("received published message", umsg)

    listener = MyListener()

    async def test_subscribe(self):
        # Topic to subscribe to
        topic = UUri(ue_id=4, ue_version_major=1, resource_id=0x8000)
        result_future = await subscriber.subscribe(topic, self.listener, CallOptions(timeout=5000))
        # check for successfully subscribed
        self.assertTrue(result_future.status.state == SubscriptionStatus.State.SUBSCRIBED)
        print('passed test_subscribe', result_future.status.state)

    async def test_unsubscribe(self):
        # Topic to unsubscribe to
        topic = UUri(ue_id=4, ue_version_major=1, resource_id=0x8000)
        status = await subscriber.unsubscribe(topic, self.listener, None)
        # check for successfully unsubscribed
        self.assertEqual(status.code, UCode.OK)
        print('passed test_unsubscribe', status.code)

    def test_run_async(self):
        # Run async_test_methods() using asyncio.run()
        asyncio.run(self.test_subscribe())
        asyncio.run(self.test_unsubscribe())


if __name__ == '__main__':
    unittest.main()
