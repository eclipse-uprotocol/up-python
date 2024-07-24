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

from tests.test_communication.mock_utransport import MockUTransport
from uprotocol.client.usubscription.v3.inmemoryusubcriptionclient import InMemoryUSubscriptionClient
from uprotocol.client.usubscription.v3.subscriptionchangehandler import SubscriptionChangeHandler
from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.inmemoryrpcclient import InMemoryRpcClient
from uprotocol.communication.simplenotifier import SimpleNotifier
from uprotocol.communication.upayload import UPayload
from uprotocol.communication.ustatuserror import UStatusError
from uprotocol.core.usubscription.v3.usubscription_pb2 import (
    FetchSubscribersResponse,
    FetchSubscriptionsRequest,
    FetchSubscriptionsResponse,
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
    async def on_receive(self, umsg: UMessage) -> None:
        pass


class TestInMemoryUSubscriptionClient(unittest.IsolatedAsyncioTestCase):
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

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
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

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
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

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
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

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        with self.assertRaises(Exception) as context:
            await subscriber.subscribe(self.topic, self.listener)
        self.assertEqual("Dummy exception", str(context.exception))

        self.rpc_client.invoke_method.assert_called_once()
        self.notifier.register_notification_listener.assert_called_once()
        self.transport.register_listener.assert_not_called()
        self.transport.get_source.assert_called_once()

    async def test_subscribe_when_register_notification_listener_return_failed_status(self):
        self.transport.get_source.return_value = self.source

        self.notifier.register_notification_listener.return_value = UStatus(code=UCode.INTERNAL)

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        with self.assertRaises(UStatusError) as context:
            await subscriber.subscribe(self.topic, self.listener)
        self.assertEqual(UCode.INTERNAL, context.exception.status.code)
        self.assertEqual("Failed to register listener for rpc client", context.exception.status.message)

    async def test_subscribe_using_mock_rpc_client_and_simplernotifier_when_invokemethod_return_an_ustatuserror(self):
        self.transport.get_source.return_value = self.source

        exception = UStatusError.from_code_message(UCode.FAILED_PRECONDITION, "Not permitted")
        self.rpc_client.invoke_method.return_value = exception

        self.notifier.register_notification_listener.return_value = UStatus(code=UCode.OK)

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
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

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
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

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
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

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
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
        self.transport.get_source.return_value = self.source
        self.transport.register_listener.return_value = UStatus(code=UCode.OK)
        self.transport.unregister_listener.return_value = UStatus(code=UCode.OK)
        self.rpc_client.invoke_method.return_value = UPayload.pack(UnsubscribeResponse())

        self.notifier.unregister_notification_listener.return_value = UStatus(code=UCode.OK)

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)
        response = await subscriber.unsubscribe(self.topic, self.listener)
        self.assertEqual(response.message, "")
        self.assertEqual(response.code, UCode.OK)
        subscriber.close()
        self.rpc_client.invoke_method.assert_called_once()
        self.notifier.unregister_notification_listener.assert_called_once()
        self.transport.unregister_listener.assert_called_once()

    async def test_unsubscribe_when_invokemethod_return_an_exception(self):
        self.transport.get_source.return_value = self.source
        self.transport.register_listener.return_value = UStatus(code=UCode.OK)
        self.transport.unregister_listener.return_value = UStatus(code=UCode.OK)
        self.rpc_client.invoke_method.return_value = UStatusError.from_code_message(
            UCode.CANCELLED, "Operation cancelled"
        )
        self.notifier.unregister_notification_listener.return_value = UStatus(code=UCode.OK)
        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)
        response = await subscriber.unsubscribe(self.topic, self.listener)
        self.assertEqual(response.message, "Operation cancelled")
        self.assertEqual(response.code, UCode.CANCELLED)
        subscriber.close()
        self.rpc_client.invoke_method.assert_called_once()
        self.notifier.unregister_notification_listener.assert_called_once()
        self.transport.unregister_listener.assert_not_called()

    async def test_unsubscribe_when_invokemethod_returned_ok_but_we_failed_to_unregister_the_listener(self):
        self.transport.get_source.return_value = self.source
        self.transport.register_listener.return_value = UStatus(code=UCode.OK)
        self.transport.unregister_listener.return_value = UStatusError.from_code_message(UCode.ABORTED, "aborted")
        self.rpc_client.invoke_method.return_value = UPayload.pack(
            SubscriptionResponse(status=SubscriptionStatus(state=SubscriptionStatus.State.SUBSCRIBE_PENDING))
        )
        self.notifier.unregister_notification_listener.return_value = UStatus(code=UCode.OK)
        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
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
            await listener.on_receive(message)
            return UStatus(code=UCode.OK)

        self.notifier.register_notification_listener = AsyncMock(side_effect=register_notification_listener)
        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
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
        notifier = MagicMock(spec=SimpleNotifier)
        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, notifier)
        with self.assertRaises(ValueError) as context:
            await subscriber.unregister_listener(None, self.listener)
        self.assertEqual(str(context.exception), "Unsubscribe topic missing")

    async def test_unregister_listener_missing_listener(self):
        notifier = MagicMock(spec=SimpleNotifier)

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, notifier)
        with self.assertRaises(ValueError) as context:
            await subscriber.unregister_listener(self.topic, None)
        self.assertEqual(str(context.exception), "Request listener missing")

    async def test_unregister_listener_happy_path(self):
        class MyListener(UListener):
            async def on_receive(self, umsg: UMessage) -> None:
                pass

        listener = MyListener()
        notifier = MagicMock(spec=SimpleNotifier)
        self.transport.unregister_listener.return_value = UStatus(code=UCode.OK)

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, notifier)
        # with self.assertRaises(ValueError) as context:
        status = await subscriber.unregister_listener(self.topic, listener)
        self.assertEqual(UCode.OK, status.code)

    async def test_unsubscribe_missing_topic(self):
        notifier = MagicMock(spec=SimpleNotifier)
        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, notifier)
        with self.assertRaises(ValueError) as context:
            await subscriber.unsubscribe(None, self.listener, CallOptions())
        self.assertEqual(str(context.exception), "Unsubscribe topic missing")

    async def test_unsubscribe_missing_listener(self):
        notifier = MagicMock(spec=SimpleNotifier)
        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, notifier)
        with self.assertRaises(ValueError) as context:
            await subscriber.unsubscribe(self.topic, None, CallOptions())
        self.assertEqual(str(context.exception), "Listener missing")

    async def test_unsubscribe_missing_options(self):
        notifier = MagicMock(spec=SimpleNotifier)
        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, notifier)
        with self.assertRaises(ValueError) as context:
            await subscriber.unsubscribe(self.topic, self.listener, None)
        self.assertEqual(str(context.exception), "CallOptions missing")

    async def test_subscribe_missing_topic(self):
        notifier = MagicMock(spec=SimpleNotifier)
        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, notifier)
        with self.assertRaises(ValueError) as context:
            await subscriber.subscribe(None, self.listener, CallOptions())
        self.assertEqual(str(context.exception), "Subscribe topic missing")

    async def test_subscribe_missing_options(self):
        notifier = MagicMock(spec=SimpleNotifier)
        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, notifier)
        with self.assertRaises(ValueError) as context:
            await subscriber.subscribe(self.topic, self.listener, None)
        self.assertEqual(str(context.exception), "CallOptions missing")

    async def test_subscribe_missing_listener(self):
        notifier = MagicMock(spec=SimpleNotifier)
        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, notifier)
        with self.assertRaises(ValueError) as context:
            await subscriber.subscribe(self.topic, None, CallOptions())
        self.assertEqual(str(context.exception), "Request listener missing")

    def test_subscription_client_constructor_transport_none(self):
        with self.assertRaises(ValueError) as context:
            InMemoryUSubscriptionClient(None, None, None)
        self.assertEqual(str(context.exception), UTransport.TRANSPORT_NULL_ERROR)

    def test_subscription_client_constructor_transport_not_instance(self):
        with self.assertRaises(ValueError) as context:
            InMemoryUSubscriptionClient("InvalidTransport", None, None)
        self.assertEqual(str(context.exception), UTransport.TRANSPORT_NOT_INSTANCE_ERROR)

    def test_subscription_client_constructor_with_just_transport(self):
        client = InMemoryUSubscriptionClient(self.transport)
        self.assertTrue(client is not None)

    async def test_register_notification_api_when_passed_a_null_topic(self):
        # Setup mocks
        notifier = AsyncMock()
        notifier.register_notification_listener.return_value = UStatus(code=UCode.OK)

        # Initialize InMemoryUSubscriptionClient
        transport = MagicMock(spec=UTransport)
        subscriber = InMemoryUSubscriptionClient(transport)
        assert subscriber is not None

        # Define the handler
        class MySubscriptionChangeHandler(SubscriptionChangeHandler):
            def handle_subscription_change(self, topic, status):
                raise NotImplementedError("Unimplemented method 'handleSubscriptionChange'")

        handler = MySubscriptionChangeHandler()

        # Assert that passing a null topic raises a ValueError
        with self.assertRaises(ValueError) as context:
            await subscriber.register_for_notifications(None, handler)
        self.assertEqual(str(context.exception), "Topic missing")

        # Verify the notifier interaction
        notifier.register_notification_listener.assert_not_called()

    async def test_register_notification_api_when_passed_a_null_handler(self):
        subscriber = InMemoryUSubscriptionClient(self.transport)
        assert subscriber is not None

        # Assert that passing a null handler raises a ValueError
        with self.assertRaises(ValueError) as context:
            await subscriber.register_for_notifications(MagicMock(spec=UUri), None)
        self.assertEqual(str(context.exception), "Handler missing")

        # Verify the notifier interaction
        self.notifier.register_notification_listener.assert_not_called()

    async def test_register_notification_api_when_passed_a_valid_topic_and_handler(self):
        subscriber = InMemoryUSubscriptionClient(MockUTransport())
        assert subscriber is not None

        # Define the handler
        class MySubscriptionChangeHandler(SubscriptionChangeHandler):
            def handle_subscription_change(self, topic, status):
                raise NotImplementedError("Unimplemented method 'handleSubscriptionChange'")

        handler = MySubscriptionChangeHandler()

        status = await subscriber.register_for_notifications(UUri(), handler)
        self.assertTrue(status is not None)

    async def test_register_notification_api_when_invoke_method_throws_an_exception(self):
        self.notifier.register_notification_listener.return_value = UStatus(code=UCode.OK)

        self.transport.get_source.return_value = self.source

        self.rpc_client.invoke_method.return_value = UStatusError.from_code_message(
            code=UCode.PERMISSION_DENIED, message="Not permitted"
        )

        # Initialize the subscription client
        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        # Define the subscription change handler
        class MySubscriptionChangeHandler(SubscriptionChangeHandler):
            async def handle_subscription_change(self, topic, status):
                raise NotImplementedError("Unimplemented method 'handle_subscription_change'")

        handler = MySubscriptionChangeHandler()
        with self.assertRaises(UStatusError) as context:
            await subscriber.register_for_notifications(self.topic, handler)

        self.assertEqual(UCode.PERMISSION_DENIED, context.exception.status.code)
        self.assertEqual("Not permitted", context.exception.status.message)

    async def test_register_for_notifications_to_the_same_topic_twice_with_same_notification_handler(self):
        self.transport.get_source.return_value = self.source

        self.rpc_client.invoke_method.return_value = UPayload.pack(None)

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        handler = MagicMock(spec=SubscriptionChangeHandler)
        handler.handle_subscription_change.return_value = NotImplementedError(
            "Unimplemented method 'handle_subscription_change'"
        )
        # First register_for_notifications attempt
        result = await subscriber.register_for_notifications(self.topic, handler, CallOptions.DEFAULT)
        self.assertTrue(result is not None)

        # Second register_for_notifications attempt
        result = await subscriber.register_for_notifications(self.topic, handler, CallOptions.DEFAULT)
        self.assertTrue(result is not None)

        self.assertEqual(self.rpc_client.invoke_method.call_count, 2)
        self.assertEqual(self.transport.get_source.call_count, 2)

    async def test_register_for_notifications_to_the_same_topic_twice_with_different_notification_handler(self):
        self.transport.get_source.return_value = self.source

        self.rpc_client.invoke_method.return_value = UPayload.pack(None)

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        handler = MagicMock(spec=SubscriptionChangeHandler)
        handler.handle_subscription_change.return_value = NotImplementedError(
            "Unimplemented method 'handle_subscription_change'"
        )
        # First register_for_notifications attempt
        result = await subscriber.register_for_notifications(self.topic, handler, CallOptions.DEFAULT)
        self.assertTrue(result is not None)
        handler1 = MagicMock(spec=SubscriptionChangeHandler)
        handler1.handle_subscription_change.return_value = NotImplementedError(
            "Unimplemented method 'handle_subscription_change'"
        )
        # Second register_for_notifications attempt
        with self.assertRaises(UStatusError) as context:
            await subscriber.register_for_notifications(self.topic, handler1, CallOptions.DEFAULT)
        self.assertEqual(UCode.ALREADY_EXISTS, context.exception.status.code)
        self.assertEqual("Handler already registered", context.exception.status.message)

        self.assertEqual(self.rpc_client.invoke_method.call_count, 2)
        self.assertEqual(self.transport.get_source.call_count, 2)

    async def test_unregister_notification_api_for_the_happy_path(self):
        handler = MagicMock(spec=SubscriptionChangeHandler)
        handler.handle_subscription_change.return_value = NotImplementedError(
            "Unimplemented method 'handle_subscription_change'"
        )
        self.transport.get_source.return_value = self.source
        self.rpc_client.invoke_method.return_value = UPayload.pack(None)

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)

        try:
            await subscriber.register_for_notifications(self.topic, handler)
            await subscriber.unregister_for_notifications(self.topic, handler)
        except Exception as e:
            self.fail(f"Exception occurred: {e}")

    async def test_unregister_notification_api_topic_missing(self):
        handler = MagicMock(spec=SubscriptionChangeHandler)
        handler.handle_subscription_change.return_value = NotImplementedError(
            "Unimplemented method 'handle_subscription_change'"
        )
        self.transport.get_source.return_value = self.source

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)
        with self.assertRaises(ValueError) as error:
            await subscriber.unregister_for_notifications(None, handler)
        self.assertEqual("Topic missing", str(error.exception))

    async def test_unregister_notification_api_handler_missing(self):
        self.transport.get_source.return_value = self.source

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)
        with self.assertRaises(ValueError) as error:
            await subscriber.unregister_for_notifications(self.topic, None)
        self.assertEqual("Handler missing", str(error.exception))

    async def test_unregister_notification_api_options_none(self):
        handler = MagicMock(spec=SubscriptionChangeHandler)
        handler.handle_subscription_change.return_value = NotImplementedError(
            "Unimplemented method 'handle_subscription_change'"
        )
        self.transport.get_source.return_value = self.source

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)
        with self.assertRaises(ValueError) as error:
            await subscriber.unregister_for_notifications(self.topic, handler, None)
        self.assertEqual("CallOptions missing", str(error.exception))

    async def test_register_notification_api_options_none(self):
        handler = MagicMock(spec=SubscriptionChangeHandler)
        handler.handle_subscription_change.return_value = NotImplementedError(
            "Unimplemented method 'handle_subscription_change'"
        )
        self.transport.get_source.return_value = self.source

        subscriber = InMemoryUSubscriptionClient(self.transport, self.rpc_client, self.notifier)
        self.assertIsNotNone(subscriber)
        with self.assertRaises(ValueError) as error:
            await subscriber.register_for_notifications(self.topic, handler, None)
        self.assertEqual("CallOptions missing", str(error.exception))

    async def test_fetch_subscribers_when_passing_null_topic(self):
        subscriber = InMemoryUSubscriptionClient(self.transport)

        with self.assertRaises(ValueError) as error:
            await subscriber.fetch_subscribers(None)
        self.assertEqual("Topic missing", str(error.exception))

    async def test_fetch_subscribers_when_passing_null_calloptions(self):
        subscriber = InMemoryUSubscriptionClient(self.transport)

        with self.assertRaises(ValueError) as error:
            await subscriber.fetch_subscribers(self.topic, None)
        self.assertEqual("CallOptions missing", str(error.exception))

    async def test_fetch_subscribers_passing_a_valid_topic(self):
        subscriber = InMemoryUSubscriptionClient(MockUTransport())

        try:
            response = await subscriber.fetch_subscribers(self.topic)
            self.assertEqual(response, FetchSubscribersResponse())
        except Exception as e:
            self.fail(f"Exception occurred: {e}")

    async def test_fetch_subscriptions_when_passing_null_request(self):
        subscriber = InMemoryUSubscriptionClient(self.transport)

        with self.assertRaises(ValueError) as error:
            await subscriber.fetch_subscriptions(None)
        self.assertEqual("Request missing", str(error.exception))

    async def test_fetch_subscriptions_when_passing_null_calloptions(self):
        subscriber = InMemoryUSubscriptionClient(self.transport)

        with self.assertRaises(ValueError) as error:
            await subscriber.fetch_subscriptions(FetchSubscriptionsRequest(), None)
        self.assertEqual("CallOptions missing", str(error.exception))

    async def test_fetch_subscriptions_passing_a_valid_fetch_subscription_request(self):
        request = FetchSubscriptionsRequest(topic=self.topic)
        subscriber = InMemoryUSubscriptionClient(MockUTransport())

        try:
            response = await subscriber.fetch_subscriptions(request)
            self.assertEqual(response, FetchSubscriptionsResponse())
        except Exception as e:
            self.fail(f"Exception occurred: {e}")


if __name__ == '__main__':
    unittest.main()
