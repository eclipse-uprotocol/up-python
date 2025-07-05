""" SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import unittest
from unittest.mock import MagicMock

from uprotocol.client.usubscription.v3.inmemoryusubcriptionclient import InMemoryUSubscriptionClient
from uprotocol.client.usubscription.v3.subscriptionchangehandler import SubscriptionChangeHandler
from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.inmemoryrpcclient import InMemoryRpcClient
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.core.usubscription.v3 import usubscription_pb2
from uprotocol.core.usubscription.v3.usubscription_pb2 import (
    FetchSubscribersResponse,
    FetchSubscriptionsRequest,
    FetchSubscriptionsResponse,
    SubscriptionResponse,
    SubscriptionStatus,
)
from uprotocol.transport.ulistener import UListener
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus
from uprotocol.transport.utransport import UTransport


class MyListener(UListener):
    async def on_receive(self, umsg):
        pass


class TestInMemoryUSubscriptionClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.transport = MagicMock(spec=UTransport)
        self.rpc_client = MagicMock(spec=InMemoryRpcClient)
        self.topic = UUri(authority_name="neelam", ue_id=3, ue_version_major=1, resource_id=0x8000)
        self.listener = MyListener()
        # Return a valid UUri when get_source is called
        self.transport.get_source.return_value = self.topic

    async def test_subscribe_success(self):
        async def coro_response(*args, **kwargs):
            return SubscriptionResponse(
                topic=self.topic,
                status=SubscriptionStatus(state=SubscriptionStatus.State.SUBSCRIBED)
            )

        self.rpc_client.invoke_method.side_effect = coro_response

        client = InMemoryUSubscriptionClient(self.transport, rpc_client=self.rpc_client)
        result = await client.subscribe(self.topic, self.listener)
        self.assertEqual(result.status.state, SubscriptionStatus.State.SUBSCRIBED)
        self.rpc_client.invoke_method.assert_called_once()

    async def test_subscribe_with_error(self):
        self.rpc_client.invoke_method.side_effect = UStatusError.from_code_message(
            UCode.PERMISSION_DENIED, "Denied"
        )
        client = InMemoryUSubscriptionClient(self.transport, rpc_client=self.rpc_client)
        with self.assertRaises(UStatusError):
            await client.subscribe(self.topic, self.listener)

    async def test_unsubscribe_success(self):
        async def coro_response(*args, **kwargs):
            return UStatus(code=UCode.OK)

        self.rpc_client.invoke_method.side_effect = coro_response

        client = InMemoryUSubscriptionClient(self.transport, rpc_client=self.rpc_client)
        status = await client.unsubscribe(self.topic, self.listener)
        self.assertEqual(status.code, UCode.OK)
        self.rpc_client.invoke_method.assert_called_once()

    async def test_unsubscribe_error(self):
        error = UStatusError.from_code_message(UCode.INTERNAL, "Internal Error")
        self.rpc_client.invoke_method.side_effect = error

        client = InMemoryUSubscriptionClient(self.transport, rpc_client=self.rpc_client)
        with self.assertRaises(UStatusError) as cm:
            await client.unsubscribe(self.topic, self.listener)
        self.assertEqual(cm.exception.status.code, UCode.INTERNAL)

    async def test_register_for_notifications_success(self):
        async def coro_response(*args, **kwargs):
            return UStatus(code=UCode.OK)

        self.rpc_client.invoke_method.side_effect = coro_response

        class DummyHandler(SubscriptionChangeHandler):
            async def handle_subscription_change(self, topic, status):
                pass

        handler = DummyHandler()
        client = InMemoryUSubscriptionClient(self.transport, rpc_client=self.rpc_client)
        status = await client.register_for_notifications(self.topic, handler)
        self.assertEqual(status.code, UCode.OK)

    async def test_register_for_notifications_error(self):
        self.rpc_client.invoke_method.side_effect = UStatusError.from_code_message(
            UCode.FAILED_PRECONDITION, "Failed"
        )

        class DummyHandler(SubscriptionChangeHandler):
            async def handle_subscription_change(self, topic, status):
                pass

        handler = DummyHandler()
        client = InMemoryUSubscriptionClient(self.transport, rpc_client=self.rpc_client)
        with self.assertRaises(UStatusError):
            await client.register_for_notifications(self.topic, handler)

    async def test_unregister_for_notifications_success(self):
        async def coro_response(*args, **kwargs):
            return UStatus(code=UCode.OK)

        self.rpc_client.invoke_method.side_effect = coro_response

        class DummyHandler(SubscriptionChangeHandler):
            async def handle_subscription_change(self, topic, status):
                pass

        handler = DummyHandler()
        client = InMemoryUSubscriptionClient(self.transport, rpc_client=self.rpc_client)
        status = await client.unregister_for_notifications(self.topic, handler)
        self.assertEqual(status.code, UCode.OK)

    async def test_fetch_subscribers_success(self):
        expected_response = FetchSubscribersResponse()

        async def coro_response(*args, **kwargs):
            return expected_response

        self.rpc_client.invoke_method.side_effect = coro_response
        client = InMemoryUSubscriptionClient(self.transport, rpc_client=self.rpc_client)
        response = await client.fetch_subscribers(self.topic)
        self.assertEqual(response, expected_response)

    async def test_fetch_subscriptions_success(self):
        request = FetchSubscriptionsRequest(topic=self.topic)
        expected_response = FetchSubscriptionsResponse()

        async def coro_response(*args, **kwargs):
            return expected_response

        self.rpc_client.invoke_method.side_effect = coro_response
        client = InMemoryUSubscriptionClient(self.transport, rpc_client=self.rpc_client)
        response = await client.fetch_subscriptions(request)
        self.assertEqual(response, expected_response)


if __name__ == '__main__':
    unittest.main()
