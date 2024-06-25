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
from abc import ABC, abstractmethod

from uprotocol.communication.calloptions import CallOptions
from uprotocol.core.usubscription.v3.usubscription_pb2 import (
    SubscriptionResponse,
)
from uprotocol.transport.ulistener import UListener
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class Subscriber(ABC):
    """
    Communication Layer (uP-L2) Subscriber interface.

    This interface provides APIs to subscribe and unsubscribe to a given topic.
    """

    @abstractmethod
    async def subscribe(self, topic: UUri, listener: UListener, options: CallOptions) -> SubscriptionResponse:
        """
        Subscribe to a given topic asynchronously.

        :param topic: The topic to subscribe to.
        :param listener: The listener to be called when a message is received on the topic.
        :param options: The call options for the subscription.
        :return: Returns the SubscriptionResponse upon successful subscription
        """
        pass

    @abstractmethod
    async def unsubscribe(self, topic: UUri, listener: UListener, options: CallOptions) -> UStatus:
        """
        Unsubscribe to a given topic asynchronously.

        :param topic: The topic to unsubscribe to.
        :param listener: The listener to be called when a message is received on the topic.
        :param options: The call options for the subscription.
        :return: Returns UStatus with the result from the unsubscribe request.
        """
        pass

    @abstractmethod
    async def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Unregister a listener from a topic asynchronously.

        :param topic: The topic to subscribe to.
        :param listener: The listener to be called when a message is received on the topic.
        :return: Returns UStatus with the status of the listener unregister request.
        """
        pass


# Example usage:
if __name__ == "__main__":
    # Concrete implementation of Subscriber
    class ConcreteSubscriber(Subscriber):
        async def subscribe(self, topic: UUri, listener: UListener, options: CallOptions) -> SubscriptionResponse:
            """
            Example implementation of subscribe method.

            :param topic: The topic to subscribe to.
            :param listener: The listener to be called when a message is received on the topic.
            :param options: The call options for the subscription.
            :return: Returns the SubscriptionResponse upon successful subscription.
            """
            await asyncio.sleep(1)  # Simulate asynchronous operation
            return SubscriptionResponse()

        async def unsubscribe(self, topic: UUri, listener: UListener, options: CallOptions) -> UStatus:
            """
            Example implementation of unsubscribe method.

            :param topic: The topic to unsubscribe to.
            :param listener: The listener to be called when a message is received on the topic.
            :param options: The call options for the subscription.
            :return: Returns None.
            """
            await asyncio.sleep(1)  # Simulate asynchronous operation
            return UStatus(message=f"Unsubscribed from topic: {topic}")

        async def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
            """
            Example implementation of unregister_listener method.

            :param topic: The topic to subscribe to.
            :param listener: The listener to be called when a message is received on the topic.
            :return: Returns None.
            """
            await asyncio.sleep(1)  # Simulate asynchronous operation
            return UStatus(message=f"Listener unregistered from topic: {topic}")

    # Example usage function
    async def example_usage(subscriber: Subscriber, topic: UUri, listener: UListener, options: CallOptions):
        try:
            response = await subscriber.subscribe(topic, listener, options)
            print("Subscribe response:", response)
        except Exception as e:
            print("Subscribe failed:", e)

        try:
            await subscriber.unsubscribe(topic, listener, options)
            print("Unsubscribe completed")
        except Exception as e:
            print("Unsubscribe failed:", e)

        try:
            await subscriber.unregister_listener(topic, listener)
            print("Unregister listener completed")
        except Exception as e:
            print("Unregister listener failed:", e)

    class MyListener(UListener):
        def on_receive(self, message):
            super().on_receive(message)
            print(message)

    # Run example usage with ConcreteSubscriber
    asyncio.run(
        example_usage(
            subscriber=ConcreteSubscriber(),
            topic=UUri(ue_id=1, ue_version_major=1, resource_id=0),
            listener=MyListener(),
            options=CallOptions(),
        )
    )
