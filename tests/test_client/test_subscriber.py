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

import time
import unittest

from tests.test_client.utransport_impl import UTransportImpl

from uprotocol.client.subscriber import Subscriber
from uprotocol.transport.ulistener import UListener

from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri
from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UStatus, UCode


def create_topic():
    return UUri(
        authority_name="hartley",
        ue_id=3,
        ue_version_major=1,
        resource_id=0x8000,
    )


class SubscriptionListener(UListener):
    def on_receive(self, message):
        raise NotImplementedError("Unimplemented method 'on_receive'")


class SubscriberImpl(Subscriber):
    def __init__(self):
        self.source = UUri(
            authority_name="hartley",
            ue_id=1,
            ue_version_major=1,
            resource_id=1,
        )
        self.mtransport = UTransportImpl(self.source)

    def get_transport(self):
        return self.mtransport


class TestSubscriber(unittest.TestCase):

    def test_create_subscriber(self):
        """
        Test Creating a Subscriber
        """
        subscriber: SubscriberImpl = SubscriberImpl()
        self.assertIsNotNone(subscriber)

    def test_subscribe_api(self):
        """
        Test Subscribe API
        """
        subscriber: SubscriberImpl = SubscriberImpl()
        listener = SubscriptionListener()
        topic: UUri = create_topic()
        print("topic", topic)
        status: UStatus = subscriber.subscribe(topic, listener)
        self.assertEqual(status.code, UCode.OK)

    # def test_unsubscribe_api(self):
    #     """
    #     Test Unsubscribe API
    #     """
    #     subscriber: SubscriberImpl = SubscriberImpl()
    #     listener = SubscriptionListener()
    #     topic = create_topic()
    #     status: UStatus = subscriber.unsubscribe(topic, listener)
    #     self.assertEqual(status.code, UCode.OK)


if __name__ == "__main__":
    unittest.main()
