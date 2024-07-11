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

from uprotocol.core.usubscription.v3.usubscription_pb2 import (
    SubscriptionStatus,
)
from uprotocol.v1.uri_pb2 import UUri


class SubscriptionChangeHandler(ABC):
    """
    Communication Layer (uP-L2) Subscription Change Handler interface.

    This interface provides APIs to handle subscription state changes for a given topic.
    """

    @abstractmethod
    def handle_subscription_change(self, topic: UUri, status: SubscriptionStatus) -> None:
        """
        Method called to handle/process subscription state changes for a given topic.

        :param topic: The topic that the subscription state changed for.
        :param status: The new status of the subscription.
        """
        pass
