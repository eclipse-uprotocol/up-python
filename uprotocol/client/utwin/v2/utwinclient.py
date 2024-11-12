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
from typing import Optional

from uprotocol.communication.calloptions import CallOptions
from uprotocol.v1.uri_pb2 import UUriBatch


class UTwinClient(ABC):
    """
    The uTwin client-side interface.

    UTwin is used to fetch the last published message for a given topic. This is the client-side of the
    UTwin Service contract and communicates with a local uTwin service to fetch the last message for a given topic.
    """

    @abstractmethod
    def get_last_messages(
        self, topics: UUriBatch, options: Optional[CallOptions] = CallOptions.DEFAULT
    ) -> asyncio.Future:
        """
        Fetch the last messages for a batch of topics.

        :param topics: UUriBatch - Batch of 1 or more topics to fetch the last messages for.
        :param options: CallOptions - The Optional call options.
        :return: asyncio.Future that completes successfully with GetLastMessagesResponse if uTwin was able
                 to fetch the topics or completes exceptionally with UStatus with the failure reason.
                 Such as UCode.NOT_FOUND, UCode.PERMISSION_DENIED, etc.
        """
        pass
