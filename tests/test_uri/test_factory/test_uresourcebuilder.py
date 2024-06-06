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

from uprotocol.proto.uprotocol_options_pb2 import UServiceTopic
from uprotocol.uri.factory.uresourcebuilder import UResourceBuilder


class TestUResourceBuilder(unittest.TestCase):
    def test_from_id_valid_id(self):
        id = 0
        resource = UResourceBuilder.from_id(id)
        self.assertEqual(resource.name, "rpc")
        self.assertEqual(resource.instance, "response")
        self.assertEqual(resource.id, 0)

    def test_from_id_invalid_id(self):
        id = -1
        with self.assertRaises(ValueError) as context:
            UResourceBuilder.from_id(id)
        self.assertEqual(str(context.exception), "Value out of range: -1")

    def test_from_id_valid_id_below_min_topic_id(self):
        id = 0x7FFF
        resource = UResourceBuilder.from_id(id)
        self.assertEqual(resource.name, "rpc")
        self.assertEqual(resource.instance, "")
        self.assertEqual(resource.id, 0x7FFF)

    def test_from_id_valid_id_above_min_topic_id(self):
        id = 0x8000
        resource = UResourceBuilder.from_id(id)
        self.assertEqual(resource.name, "")
        self.assertEqual(resource.instance, "")
        self.assertEqual(resource.id, 0x8000)

    def test_from_uservice_topic_valid_service_topic(self):
        topic = UServiceTopic(name="SubscriptionChange", id=0, message="Update")
        resource = UResourceBuilder.from_uservice_topic(topic)
        self.assertEqual(resource.name, "SubscriptionChange")
        self.assertEqual(resource.instance, "")
        self.assertEqual(resource.id, 0)
        self.assertEqual(resource.message, "Update")

    def test_from_uservice_topic_valid_service_topic_with_instance(self):
        topic = UServiceTopic(name="door.front_left", id=0x8000, message="Door")
        resource = UResourceBuilder.from_uservice_topic(topic)
        self.assertEqual(resource.name, "door")
        self.assertEqual(resource.instance, "front_left")
        self.assertEqual(resource.id, 0x8000)
        self.assertEqual(resource.message, "Door")

    def test_from_uservice_topic_invalid_service_topic(self):
        topic = None
        with self.assertRaises(ValueError) as context:
            UResourceBuilder.from_uservice_topic(topic)
        self.assertEqual(str(context.exception), "topic cannot be None.")


if __name__ == "__main__":
    unittest.main()
