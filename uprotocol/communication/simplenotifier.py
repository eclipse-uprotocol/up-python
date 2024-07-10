"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.notifier import Notifier
from uprotocol.communication.upayload import UPayload
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus


class SimpleNotifier(Notifier):
    """
    The following is an example implementation of the Notifier interface that
    wraps the UTransport for implementing the notification pattern to send
    notifications and register to receive notification events.

    *NOTE:* Developers are not required to use these APIs, they can implement their own
    or directly use the UTransport to send notifications and register listeners.
    """

    def __init__(self, transport: UTransport):
        """
        Constructor for the DefaultNotifier.

        :param transport: the transport to use for sending the notifications
        """
        if transport is None:
            raise ValueError(UTransport.TRANSPORT_NULL_ERROR)
        elif not isinstance(transport, UTransport):
            raise ValueError(UTransport.TRANSPORT_NOT_INSTANCE_ERROR)
        self.transport = transport

    async def notify(
        self, topic: UUri, destination: UUri, options: Optional[CallOptions] = None, payload: Optional[UPayload] = None
    ) -> UStatus:
        """
        Send a notification to a given topic.

        :param topic: The topic to send the notification to.
        :param destination: The destination to send the notification to.
        :param options: Call options for the notification.
        :param payload: The payload to send with the notification.
        :return: Returns the UStatus with the status of the notification.
        """
        builder = UMessageBuilder.notification(topic, destination)
        if options:
            builder.with_priority(options.priority)
            builder.with_ttl(options.timeout)
            builder.with_token(options.token)
        return await self.transport.send(builder.build() if payload is None else builder.build_from_upayload(payload))

    async def register_notification_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Register a listener for a notification topic.

        :param topic: The topic to register the listener to.
        :param listener: The listener to be called when a message is received on the topic.
        :return: Returns the UStatus with the status of the listener registration.
        """
        return await self.transport.register_listener(topic, listener, self.transport.get_source())

    async def unregister_notification_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Unregister a listener from a notification topic.

        :param topic: The topic to unregister the listener from.
        :param listener: The listener to be unregistered from the topic.
        :return: Returns the UStatus with the status of the listener that was unregistered.
        """
        return await self.transport.unregister_listener(topic, listener, self.transport.get_source())
