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

import unittest

from tests.test_client.utransport_impl import UTransportImpl

from uprotocol.client.notifier import Notifier

from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri
from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UCode, UStatus
from uprotocol.transport.ulistener import UListener


def create_topic():
    return UUri(
        authority_name="hartley",
        ue_id=3,
        ue_version_major=1,
        resource_id=0x8000,
    )


def create_destination_uri():
    return UUri(authority_name="hartley", ue_id=4, ue_version_major=1)


class NotifierImpl(Notifier):
    def __init__(self):
        self.source = UUri(
            authority_name="hartley", ue_id=1, ue_version_major=1
        )
        self.mtransport = UTransportImpl(self.source)

    def get_transport(self):
        return self.mtransport


class NotificationListener(UListener):
    def on_receive(self, message):
        raise NotImplementedError("Unimplemented method 'on_receive'")


class TestNotifier(unittest.TestCase):

    def test_create_notifier(self):
        """
        Test Creating a Notifier
        """
        notifier = NotifierImpl()
        self.assertIsNotNone(notifier)

    def test_notify_without_payload(self):
        """
        Test calling notify without a payload
        """
        notifier: NotifierImpl = NotifierImpl()
        status = notifier.notify(create_topic(), create_destination_uri())
        self.assertEqual(status.code, UCode.OK)

    def test_notify_api_with_google_protobuf_message(self):
        """
        Test calling notify Api passing google.protobuf.Message as payload
        """
        notifier: NotifierImpl = NotifierImpl()
        status: UStatus = notifier.notify(
            create_topic(), create_destination_uri(), UUri()
        )
        self.assertEqual(status.code, UCode.OK)

    def test_register_notification_listener(self):
        """
        Test calling registerNotificationListener
        """
        notifier: NotifierImpl = NotifierImpl()
        status: UStatus = notifier.register_notification_listener(
            create_topic(), NotificationListener()
        )
        self.assertEqual(status.code, UCode.OK)

    def test_unregister_notification_listener(self):
        """
        Test calling registerNotificationListener
        """
        notifier: NotifierImpl = NotifierImpl()
        status: UStatus = notifier.unregister_notification_listener(
            create_topic(), NotificationListener()
        )
        self.assertEqual(status.code, UCode.OK)
