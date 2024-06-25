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

from uprotocol.communication.upayload import UPayload
from uprotocol.transport.ulistener import UListener
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class Notifier(ABC):
    """
    Communication Layer (uP-L2) Notifier Interface.

    Notifier is an interface that provides the APIs to send notifications (to a client) or
    register/unregister listeners to receive the notifications.
    """

    @abstractmethod
    def notify(self, topic: UUri, destination: UUri, payload: UPayload) -> UStatus:
        """
        Send a notification to a given topic passing a payload.

        :param topic: The topic to send the notification to.
        :param destination: The destination to send the notification to.
        :param payload: The payload to send with the notification.
        :return: Returns the UStatus with the status of the notification.
        """
        pass

    @abstractmethod
    def register_notification_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Register a listener for a notification topic.

        :param topic: The topic to register the listener to.
        :param listener: The listener to be called when a message is received on the topic.
        :return: Returns the UStatus with the status of the listener registration.
        """
        pass

    @abstractmethod
    def unregister_notification_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Unregister a listener from a notification topic.

        :param topic: The topic to unregister the listener from.
        :param listener: The listener to be unregistered from the topic.
        :return: Returns the UStatus with the status of the listener that was unregistered.
        """
        pass
