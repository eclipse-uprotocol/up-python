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
from unittest.mock import AsyncMock, MagicMock

from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.inmemoryrpcclient import InMemoryRpcClient
from uprotocol.communication.inmemorysubscriber import InMemorySubscriber
from uprotocol.communication.simplenotifier import SimpleNotifier
from uprotocol.communication.subscriptionchangehandler import SubscriptionChangeHandler
from uprotocol.communication.upayload import UPayload
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.core.usubscription.v3.usubscription_pb2 import (
    SubscriptionResponse,
    SubscriptionStatus,
    UnsubscribeResponse,
    Update,
)
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class MyListener(UListener):
    def on_receive(self, umsg: UMessage) -> None:
        pass


class TestInMemorySubscriber(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.transport = MagicMock(spec=UTransport)
        self.rpc_client = MagicMock(spec=InMemoryRpcClient)
        self.notifier = MagicMock(spec=SimpleNotifier)

        self.topic = UUri(authority_name="neelam", ue_id=3, ue_version_major=1, resource_id=0x8000)
        self.source = UUri(authority_name="source_auth", ue_id=4, ue_version_major=1)

        self.listener = MyListener()

    async def test_simple_mock_of_rpc_client_and_notifier(self):
        response = SubscriptionResponse(
            topic=self.topic, status=SubscriptionStatus(state=SubscriptionStatus.State.SUBSCRIBED)
        )

        self.transport.get_source.return_value = self.source
        self.transport.register_listener.return_value = UStatus(code=UCode.OK)

        self.rpc_client.invoke_method.return_value = UPayload.pack(response)

        self.notifier.register_notification_listener.return_value = UStatus(code=UCode.OK)

        subscriber = InMemorySubscriber(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        result = await subscriber.subscribe(self.topic, self.listener)
        self.assertEqual(result.status.state, SubscriptionStatus.State.SUBSCRIBED)

        self.rpc_client.invoke_method.assert_called_once()
        self.notifier.register_notification_listener.assert_called_once()
        self.transport.register_listener.assert_called_once()
        self.transport.get_source.assert_called_once()

    async def test_simple_mock_of_rpc_client_and_notifier_returned_subscribe_pending(self):
        response = SubscriptionResponse(
            topic=self.topic, status=SubscriptionStatus(state=SubscriptionStatus.State.SUBSCRIBE_PENDING)
        )

        self.transport.get_source.return_value = self.source
        self.transport.register_listener.return_value = UStatus(code=UCode.OK)

        self.rpc_client.invoke_method.return_value = UPayload.pack(response)

        self.notifier.register_notification_listener.return_value = UStatus(code=UCode.OK)

        subscriber = InMemorySubscriber(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        subscriber = InMemorySubscriber(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        result = await subscriber.subscribe(self.topic, self.listener)
        self.assertEqual(result.status.state, SubscriptionStatus.State.SUBSCRIBE_PENDING)

        self.rpc_client.invoke_method.assert_called_once()
        self.notifier.register_notification_listener.assert_called_once()
        self.transport.register_listener.assert_called_once()
        self.transport.get_source.assert_called_once()

    async def test_simple_mock_of_rpc_client_and_notifier_returned_unsubscribed(self):
        response = SubscriptionResponse(
            topic=self.topic, status=SubscriptionStatus(state=SubscriptionStatus.State.UNSUBSCRIBED)
        )

        self.transport.get_source.return_value = self.source
        self.transport.register_listener.return_value = UStatus(code=UCode.OK)

        self.rpc_client.invoke_method.return_value = UPayload.pack(response)

        self.notifier.register_notification_listener.return_value = UStatus(code=UCode.OK)

        subscriber = InMemorySubscriber(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        subscriber = InMemorySubscriber(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        result = await subscriber.subscribe(self.topic, self.listener)
        self.assertEqual(result.status.state, SubscriptionStatus.State.UNSUBSCRIBED)

        self.rpc_client.invoke_method.assert_called_once()
        self.notifier.register_notification_listener.assert_called_once()
        self.transport.register_listener.assert_not_called()
        self.transport.get_source.assert_called_once()

    async def test_subscribe_using_mock_rpc_client_and_simplernotifier_when_invokemethod_return_an_exception(self):
        self.transport.get_source.return_value = self.source

        exception = Exception("Dummy exception")
        self.rpc_client.invoke_method.return_value = exception

        self.notifier.register_notification_listener.return_value = UStatus(code=UCode.OK)

        subscriber = InMemorySubscriber(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        with self.assertRaises(Exception) as context:
            await subscriber.subscribe(self.topic, self.listener)
        self.assertEqual("Dummy exception", str(context.exception))

        self.rpc_client.invoke_method.assert_called_once()
        self.notifier.register_notification_listener.assert_called_once()
        self.transport.register_listener.assert_not_called()
        self.transport.get_source.assert_called_once()

    async def test_subscribe_using_mock_rpc_client_and_simplernotifier_when_invokemethod_return_an_ustatuserror(self):
        self.transport.get_source.return_value = self.source

        exception = UStatusError.from_code_message(UCode.FAILED_PRECONDITION, "Not permitted")
        self.rpc_client.invoke_method.return_value = exception

        self.notifier.register_notification_listener.return_value = UStatus(code=UCode.OK)

        subscriber = InMemorySubscriber(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        with self.assertRaises(UStatusError) as context:
            await subscriber.subscribe(self.topic, self.listener)
        self.assertEqual("Not permitted", context.exception.status.message)
        self.assertEqual(UCode.FAILED_PRECONDITION, context.exception.status.code)

        self.rpc_client.invoke_method.assert_called_once()
        self.notifier.register_notification_listener.assert_called_once()
        self.transport.register_listener.assert_not_called()
        self.transport.get_source.assert_called_once()

    async def test_subscribe_when_we_pass_a_subscription_change_notification_handler(self):
        self.transport.get_source.return_value = self.source
        self.transport.register_listener.return_value = UStatus(code=UCode.OK)

        self.rpc_client.invoke_method.return_value = UPayload.pack(
            SubscriptionResponse(topic=self.topic, status=SubscriptionStatus(state=SubscriptionStatus.State.SUBSCRIBED))
        )

        self.notifier.register_notification_listener.return_value = UStatus(code=UCode.OK)

        subscriber = InMemorySubscriber(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        handler = MagicMock(spec=SubscriptionChangeHandler)
        handler.handle_subscription_change.return_value = NotImplementedError(
            "Unimplemented method 'handle_subscription_change'"
        )

        result = await subscriber.subscribe(self.topic, self.listener, CallOptions.DEFAULT, handler)

        self.assertEqual(result.status.state, SubscriptionStatus.State.SUBSCRIBED)

        self.rpc_client.invoke_method.assert_called_once()
        self.notifier.register_notification_listener.assert_called_once()
        self.transport.register_listener.assert_called_once()
        self.transport.get_source.assert_called_once()

    async def test_subscribe_when_we_try_to_subscribe_to_the_same_topic_twice_with_same_notification_handler(self):
        self.transport.get_source.return_value = self.source

        self.rpc_client.invoke_method.return_value = UPayload.pack(
            SubscriptionResponse(topic=self.topic, status=SubscriptionStatus(state=SubscriptionStatus.State.SUBSCRIBED))
        )

        self.notifier.register_notification_listener.return_value = UStatus(code=UCode.OK)

        subscriber = InMemorySubscriber(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        handler = MagicMock(spec=SubscriptionChangeHandler)
        handler.handle_subscription_change.return_value = NotImplementedError(
            "Unimplemented method 'handle_subscription_change'"
        )
        # First subscription attempt
        result = await subscriber.subscribe(self.topic, self.listener, CallOptions.DEFAULT, handler)
        self.assertEqual(result.status.state, SubscriptionStatus.State.SUBSCRIBED)

        # Second subscription attempt
        result = await subscriber.subscribe(self.topic, self.listener, CallOptions.DEFAULT, handler)
        self.assertEqual(result.status.state, SubscriptionStatus.State.SUBSCRIBED)

        self.assertEqual(self.rpc_client.invoke_method.call_count, 2)
        self.notifier.register_notification_listener.assert_called_once()
        self.assertEqual(self.transport.get_source.call_count, 2)

    async def test_subscribe_when_we_try_to_subscribe_to_the_same_topic_twice_with_different_notification_handler(self):
        self.transport.get_source.return_value = self.source

        self.rpc_client.invoke_method.return_value = UPayload.pack(
            SubscriptionResponse(topic=self.topic, status=SubscriptionStatus(state=SubscriptionStatus.State.SUBSCRIBED))
        )

        self.notifier.register_notification_listener.return_value = UStatus(code=UCode.OK)

        subscriber = InMemorySubscriber(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        handler = MagicMock(spec=SubscriptionChangeHandler)

        handler1 = MagicMock(spec=SubscriptionChangeHandler)

        # First subscription attempt
        result = await subscriber.subscribe(self.topic, self.listener, CallOptions.DEFAULT, handler)
        self.assertEqual(result.status.state, SubscriptionStatus.State.SUBSCRIBED)
        # Second subscription attempt should raise an exception
        with self.assertRaises(UStatusError) as context:
            await subscriber.subscribe(self.topic, self.listener, CallOptions.DEFAULT, handler1)
        self.assertEqual("Handler already registered", context.exception.status.message)
        self.assertEqual(UCode.ALREADY_EXISTS, context.exception.status.code)

        self.assertEqual(2, self.rpc_client.invoke_method.call_count)
        self.notifier.register_notification_listener.assert_called_once()
        self.assertEqual(self.transport.get_source.call_count, 2)

    async def test_unsubscribe_using_mock_rpcclient_and_simplernotifier(self):
        self.transport.register_listener.return_value = UStatus(code=UCode.OK)
        self.transport.unregister_listener.return_value = UStatus(code=UCode.OK)
        self.rpc_client.invoke_method.return_value = UPayload.pack(UnsubscribeResponse())

        self.notifier.unregister_notification_listener.return_value = UStatus(code=UCode.OK)

        subscriber = InMemorySubscriber(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)
        response = await subscriber.unsubscribe(self.topic, self.listener)
        self.assertEqual(response.message, "")
        self.assertEqual(response.code, UCode.OK)
        subscriber.close()
        self.rpc_client.invoke_method.assert_called_once()
        self.notifier.unregister_notification_listener.assert_called_once()
        self.transport.unregister_listener.assert_called_once()

    async def test_unsubscribe_when_invokemethod_return_an_exception(self):
        self.transport.register_listener.return_value = UStatus(code=UCode.OK)
        self.transport.unregister_listener.return_value = UStatus(code=UCode.OK)
        self.rpc_client.invoke_method.return_value = UStatusError.from_code_message(
            UCode.CANCELLED, "Operation cancelled"
        )
        self.notifier.unregister_notification_listener.return_value = UStatus(code=UCode.OK)
        subscriber = InMemorySubscriber(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)
        response = await subscriber.unsubscribe(self.topic, self.listener)
        self.assertEqual(response.message, "Operation cancelled")
        self.assertEqual(response.code, UCode.CANCELLED)
        subscriber.close()
        self.rpc_client.invoke_method.assert_called_once()
        self.notifier.unregister_notification_listener.assert_called_once()
        self.transport.unregister_listener.assert_not_called()

    async def test_unsubscribe_when_invokemethod_returned_ok_but_we_failed_to_unregister_the_listener(self):
        self.transport.register_listener.return_value = UStatus(code=UCode.OK)
        self.transport.unregister_listener.return_value = UStatusError.from_code_message(UCode.ABORTED, "aborted")
        self.rpc_client.invoke_method.return_value = UPayload.pack(
            SubscriptionResponse(status=SubscriptionStatus(state=SubscriptionStatus.State.SUBSCRIBE_PENDING))
        )
        self.notifier.unregister_notification_listener.return_value = UStatus(code=UCode.OK)
        subscriber = InMemorySubscriber(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)
        response = await subscriber.unsubscribe(self.topic, self.listener)
        self.assertEqual(response.status.code, UCode.ABORTED)
        self.assertEqual(response.status.message, "aborted")
        subscriber.close()
        self.rpc_client.invoke_method.assert_called_once()
        self.notifier.unregister_notification_listener.assert_called_once()
        self.transport.unregister_listener.assert_called_once()

    async def test_handling_going_from_subscribe_pending_to_subscribed_state(self):
        barrier = asyncio.Event()
        self.transport.get_source.return_value = self.source
        self.transport.register_listener.return_value = UStatus(code=UCode.OK)
        self.rpc_client.invoke_method.return_value = UPayload.pack(
            SubscriptionResponse(status=SubscriptionStatus(state=SubscriptionStatus.State.SUBSCRIBE_PENDING))
        )

        async def register_notification_listener(uri, listener):
            barrier.set()  # Release the barrier
            await barrier.wait()  # Wait for the barrier again
            update = Update(topic=self.topic, status=SubscriptionStatus(state=SubscriptionStatus.State.SUBSCRIBED))
            message = UMessageBuilder.notification(self.topic, self.source).build_from_upayload(UPayload.pack(update))
            listener.on_receive(message)
            return UStatus(code=UCode.OK)

        self.notifier.register_notification_listener = AsyncMock(side_effect=register_notification_listener)
        subscriber = InMemorySubscriber(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)
        result = await subscriber.subscribe(self.topic, self.listener, CallOptions.DEFAULT)
        self.assertEqual(result.status.state, SubscriptionStatus.State.SUBSCRIBE_PENDING)
        # Release the barrier
        barrier.set()
        # Wait for the barrier again to ensure notification handling
        await barrier.wait()

        self.rpc_client.invoke_method.assert_called_once()
        self.notifier.register_notification_listener.assert_called_once()
        self.transport.register_listener.assert_called_once()
        self.transport.get_source.assert_called_once()

    async def test_unregister_listener_missing_topic(self):
        transport = MagicMock(spec=UTransport)
        rpc_client = MagicMock(spec=InMemoryRpcClient)
        notifier = MagicMock(spec=SimpleNotifier)
        subscriber = InMemorySubscriber(transport, rpc_client, notifier)
        with self.assertRaises(ValueError) as context:
            await subscriber.unregister_listener(None, self.listener)
        self.assertEqual(str(context.exception), "Unsubscribe topic missing")

    async def test_unregister_listener_missing_listener(self):
        transport = MagicMock(spec=UTransport)
        rpc_client = MagicMock(spec=InMemoryRpcClient)
        notifier = MagicMock(spec=SimpleNotifier)
        subscriber = InMemorySubscriber(transport, rpc_client, notifier)
        with self.assertRaises(ValueError) as context:
            await subscriber.unregister_listener(self.topic, None)
        self.assertEqual(str(context.exception), "Request listener missing")

    async def test_unsubscribe_missing_topic(self):
        transport = MagicMock(spec=UTransport)
        rpc_client = MagicMock(spec=InMemoryRpcClient)
        notifier = MagicMock(spec=SimpleNotifier)
        subscriber = InMemorySubscriber(transport, rpc_client, notifier)
        with self.assertRaises(ValueError) as context:
            await subscriber.unsubscribe(None, self.listener, CallOptions())
        self.assertEqual(str(context.exception), "Unsubscribe topic missing")

    async def test_unsubscribe_missing_listener(self):
        transport = MagicMock(spec=UTransport)
        rpc_client = MagicMock(spec=InMemoryRpcClient)
        notifier = MagicMock(spec=SimpleNotifier)
        subscriber = InMemorySubscriber(transport, rpc_client, notifier)
        with self.assertRaises(ValueError) as context:
            await subscriber.unsubscribe(self.topic, None, CallOptions())
        self.assertEqual(str(context.exception), "Listener missing")

    async def test_subscribe_missing_topic(self):
        transport = MagicMock(spec=UTransport)
        rpc_client = MagicMock(spec=InMemoryRpcClient)
        notifier = MagicMock(spec=SimpleNotifier)
        subscriber = InMemorySubscriber(transport, rpc_client, notifier)
        with self.assertRaises(ValueError) as context:
            await subscriber.subscribe(None, self.listener, CallOptions())
        self.assertEqual(str(context.exception), "Subscribe topic missing")

    async def test_subscribe_missing_listener(self):
        transport = MagicMock(spec=UTransport)
        rpc_client = MagicMock(spec=InMemoryRpcClient)
        notifier = MagicMock(spec=SimpleNotifier)
        subscriber = InMemorySubscriber(transport, rpc_client, notifier)
        with self.assertRaises(ValueError) as context:
            await subscriber.subscribe(self.topic, None, CallOptions())
        self.assertEqual(str(context.exception), "Request listener missing")


if __name__ == '__main__':
    unittest.main()
