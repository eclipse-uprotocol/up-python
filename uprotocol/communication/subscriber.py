"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

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
