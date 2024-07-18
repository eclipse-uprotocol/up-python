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

from uprotocol.client.usubscription.v3.subscriptionchangehandler import SubscriptionChangeHandler
from uprotocol.communication.calloptions import CallOptions
from uprotocol.core.usubscription.v3.usubscription_pb2 import (
    FetchSubscribersResponse,
    FetchSubscriptionsRequest,
    FetchSubscriptionsResponse,
    NotificationsResponse,
    SubscriptionResponse,
)
from uprotocol.transport.ulistener import UListener
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class USubscriptionClient(ABC):
    """
    The client-side interface for communicating with the USubscription service asynchronously.

    Provides methods for subscribing, unsubscribing, registering listeners, fetching subscribers,
    fetching subscriptions, and handling subscription change notifications.
    """

    @abstractmethod
    async def subscribe(
        self,
        topic: UUri,
        listener: UListener,
        options: Optional[CallOptions] = CallOptions.DEFAULT,
        handler: Optional[SubscriptionChangeHandler] = None,
    ) -> SubscriptionResponse:
        """
        Subscribes to a given topic asynchronously.

        The API will return a SubscriptionResponse or raise an exception if the subscription
        was not successful. The optional passed SubscriptionChangeHandler is used to receive
        notifications of changes to the subscription status like a transition from
        SubscriptionStatus.State.SUBSCRIBE_PENDING to SubscriptionStatus.State.SUBSCRIBED that
        occurs when we subscribe to remote topics that the device we are on has not yet a
        subscriber that has subscribed to said topic.

        :param topic: The topic to subscribe to.
        :param listener: The listener to be called when messages are received.
        :param options: The CallOptions to be used for the subscription.
        :param handler: SubscriptionChangeHandler to handle changes to subscription states.

        :return: Returns a SubscriptionResponse or raises an exception with the failure reason
            as UStatus. UCode.ALREADY_EXISTS will be raised if you call this API multiple times
            passing a different handler.
        """
        pass

    @abstractmethod
    async def unsubscribe(
        self, topic: UUri, listener: UListener, options: Optional[CallOptions] = CallOptions.DEFAULT
    ) -> UStatus:
        """
        Unsubscribes from a given topic asynchronously.

        The subscriber no longer wishes to be subscribed to said topic so we issue an unsubscribe
        request to the USubscription service. The API will return a UStatus with the result of
        the unsubscribe request. If we are unable to unsubscribe to the topic with the USubscription
        service, the listener and handler (if any) will remain registered.

        :param topic: The topic to unsubscribe from.
        :param listener: The listener to be called when a message is received on the topic.
        :param options: The CallOptions to be used for the unsubscribe request.

        :return: Returns a UStatus with the result from the unsubscribe request.
        """
        pass

    @abstractmethod
    async def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Unregister a listener and remove any registered SubscriptionChangeHandler for the topic.

        This method is used to remove handlers/listeners without notifying the uSubscription service
        so that we can be persistently subscribed even when the uE is not running.

        :param topic: The topic to unsubscribe from.
        :param listener: The listener to be called when a message is received on the topic.

        :return: Returns a UStatus with the status of the listener unregister request.
        """
        pass

    @abstractmethod
    async def register_for_notifications(
        self, topic: UUri, handler: SubscriptionChangeHandler, options: Optional[CallOptions] = CallOptions.DEFAULT
    ) -> NotificationsResponse:
        """
        Register for Subscription Change Notifications.

        This API allows producers to register to receive subscription change notifications for
        topics that they produce only.

        NOTE: Subscribers are automatically registered to receive notifications when they call
        `subscribe()` API passing a SubscriptionChangeHandler so they do not need to
        call this API.

        :param topic: The topic to register for notifications.
        :param handler: The SubscriptionChangeHandler to handle the subscription changes.
        :param options: The CallOptions to be used for the request. Default is CallOptions.DEFAULT.

        :return: Returns NotificationsResponse completed successfully if uSubscription service accepts the
                 request to register the caller to be notified of subscription changes, or
                 returns UStatus that indicates the failure reason.
        """
        pass

    @abstractmethod
    async def unregister_for_notifications(
        self, topic: UUri, handler: SubscriptionChangeHandler, options: Optional[CallOptions] = CallOptions.DEFAULT
    ) -> NotificationsResponse:
        """
        Unregister for subscription change notifications.

        :param topic: The topic to unregister for notifications.
        :param handler: The SubscriptionChangeHandler to be unregistered.
        :param options: The CallOptions to be used for the request. Default is CallOptions.DEFAULT.

        :return: Returns NotificationsResponse completed successfully with the status of the API call to
        uSubscription service, or completed unsuccessfully with UStatus with the reason for the failure.
        """
        pass

    @abstractmethod
    async def fetch_subscribers(
        self, topic: UUri, options: Optional[CallOptions] = CallOptions.DEFAULT
    ) -> FetchSubscribersResponse:
        """
        Fetch the list of subscribers for a given produced topic.

        :param topic: The topic to fetch the subscribers for.
        :param options: The CallOptions to be used for the request.

        :return: Returns FetchSubscribersResponse completed successfully with the list of subscribers,
                 or completed unsuccessfully with UStatus with the reason for the failure.
        """
        pass

    @abstractmethod
    async def fetch_subscriptions(
        self, request: FetchSubscriptionsRequest, options: Optional[CallOptions] = CallOptions.DEFAULT
    ) -> FetchSubscriptionsResponse:
        """
        Fetch list of Subscriptions for a given topic.

        API provides more information than fetchSubscribers() in that it also returns
        SubscribeAttributes per subscriber that might be useful to the producer to know.

        :param request: The request to fetch subscriptions for.
        :param options: The CallOptions to be used for the request.

        :return: Returns FetchSubscriptionsResponse completed successfully with the subscription
                 information per subscriber to the topic, or completed unsuccessfully with UStatus
                 with the reason for the failure. UCode.PERMISSION_DENIED is returned if the topic
                 ue_id does not equal the caller's ue_id.
        """
        pass
