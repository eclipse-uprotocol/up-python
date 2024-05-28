"""
SPDX-FileCopyrightText: Copyright (c) 2023 Contributors to the
Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SPDX-FileType: SOURCE
SPDX-License-Identifier: Apache-2.0
"""

from multimethod import multimethod
from google.protobuf.message import Message

from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri
from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UStatus

from uprotocol.client.transport_wrapper import TransportWrapper
from uprotocol.transport.builder.umessage_builder import UMessageBuilder
from uprotocol.transport.ulistener import UListener


class Notifier(TransportWrapper):
    """
    Notification Interface

    Notifier is an interface that provides the API to send notifications or
    register listeners that are called when a notification is received.
    """

    @multimethod
    def notify(self, topic: UUri, destination: UUri) -> UStatus:
        """
        Send a notification to a given topic.

        @param topic The topic to send the notification to.
        @param destination The destination to send the notification to.
        @return Returns the UStatus with the status of the notification.
        """
        return self.get_transport().send(
            UMessageBuilder.notification(topic, destination).build()
        )

    @multimethod
    def notify(
        self, topic: UUri, destination: UUri, message: Message
    ) -> UStatus:
        """
        Send a notification to a given topic with Message payload. <br>

        @param topic The topic to send the notification to.
        @param destination The destination to send the notification to.
        @param payload The payload to send with the notification.
        @return Returns the UStatus with the status of the notification.
        """
        return self.get_transport().send(
            UMessageBuilder.notification(topic, destination).build(message)
        )

    def register_notification_listener(
        self, topic: UUri, listener: UListener
    ) -> UStatus:
        """
        Register a listener for a notification topic.

        @param topic The topic to register the listener to.
        @param listener The listener to be called when a message is
        received on the topic.
        @return Returns the @link UStatus with the status of the
        listener registration.
        """
        return self.get_transport().register_listener(
            topic, self.get_transport().get_source(), listener
        )

    def unregister_notification_listener(
        self, topic: UUri, listener: UListener
    ) -> UStatus:
        """
        Unregister a listener from a notification topic.

        @param topic The topic to unregister the listener from.
        @param listener The listener to be unregistered from the topic.
        @return Returns the UStatus with the status of the listener
        that was unregistered.
        """
        return self.get_transport().unregister_listener(
            topic, self.get_transport().get_source(), listener
        )
