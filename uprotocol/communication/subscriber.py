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
from typing import Optional

from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.subscriptionchangehandler import SubscriptionChangeHandler
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
    async def subscribe(
        self,
        topic: UUri,
        listener: UListener,
        options: Optional[CallOptions] = None,
        handler: Optional[SubscriptionChangeHandler] = None,
    ) -> SubscriptionResponse:
        """
        Subscribes to a given topic asynchronously.

        The API will return a SubscriptionResponse or raise an exception if the subscription fails.
        It registers the listener to be called when messages are received and allows the caller to register
        a SubscriptionChangeHandler that is called whenever the subscription state changes
        (e.g., SubscriptionStatus.State.PENDING_SUBSCRIBED to SubscriptionStatus.State.SUBSCRIBED,
        SubscriptionStatus.State.SUBSCRIBED to SubscriptionStatus.State.UNSUBSCRIBED, etc.).

        :param topic: The topic to subscribe to.
        :param listener: The UListener that is called when published messages are received.
        :param options: The CallOptions to provide additional information (timeout, token, etc.).
        :param handler: SubscriptionChangeHandler to handle changes to subscription states.
        :return: Returns the SubscriptionResponse or raises an exception with the failure reason as UStatus.
        """
        pass

    @abstractmethod
    async def unsubscribe(
        self, topic: UUri, listener: UListener, options: Optional[CallOptions] = CallOptions.DEFAULT
    ) -> UStatus:
        """
        Unsubscribes from a given topic.

        The subscriber no longer wishes to be subscribed to the specified topic, trigger an unsubscribe
        request to the USubscription service.

        :param topic: The topic to unsubscribe to.
        :param listener: The listener to be called when a message is received on the topic.
        :param options: The call options for the subscription.
        :return: Returns UStatus with the result from the unsubscribe request.
        """
        pass

    @abstractmethod
    async def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Unregisters a listener from a topic asynchronously.

        This method will only unregister the listener for a given subscription, allowing the uE to remain subscribed
        even if the listener is removed.

        :param topic: The topic to subscribe to.
        :param listener: The listener to be called when a message is received on the topic.
        :return: Returns UStatus with the status of the listener unregister request.
        """
        pass
