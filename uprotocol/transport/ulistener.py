"""
SPDX-FileCopyrightText: 2023 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from abc import ABC, abstractmethod

from uprotocol.v1.umessage_pb2 import UMessage


class UListener(ABC):
    """For any implementation that defines some kind of callback or function that will be called to handle incoming
    messages.
    """

    @abstractmethod
    def on_receive(self, umsg: UMessage) -> None:
        """Method called to handle/process messages.<br><br>
        @param umsg: UMessage to be sent.
        """
        pass
