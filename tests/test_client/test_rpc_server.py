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
from uprotocol.client.request_listener import RequestListener
from uprotocol.client.rpc_server import RpcServer
from uprotocol.transport.utransport import UTransport

from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri
from uprotocol.proto.uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.proto.uprotocol.v1.ustatus_pb2 import UStatus, UCode


class MyRequestListener(RequestListener):

    def __init__(self, transport: UTransport):
        self.transport = transport

    def get_transport(self) -> UTransport:
        return self.transport

    def on_receive(self, message: UMessage, response_future):
        """
        Bare impl of on_receive for tests
        """
        pass


class RpcServerImpl(RpcServer):

    def __init__(self):
        self.source = UUri(authority_name="hartley", ue_id=1, ue_version_major=1)
        self.transport = UTransportImpl(self.source)

    def get_transport(self) -> UTransport:
        return self.transport


def create_method_uri():
    return UUri(
        authority_name="hartley",
        ue_id=10,
        ue_version_major=1,
        resource_id=3,
    )


class TestRpcServer(unittest.TestCase):

    def test_happy_get_transport(self):
        """
        Test happy path get transport
        """
        server: RpcServer = RpcServerImpl()
        self.assertIsNotNone(server.get_transport())

    def test_registering_request_listener(self):
        """
        Test registering a request listener.
        """
        server: RpcServer = RpcServerImpl()
        listener = MyRequestListener(server.get_transport())
        status: UStatus = server.register_request_listener(create_method_uri(), listener)
        self.assertEqual(status.code, UCode.OK)

    def test_unregistering_request_listener(self):
        """
        Test unregistering a request listener.
        """
        server: RpcServer = RpcServerImpl()
        listener = MyRequestListener(server.get_transport())
        status: UStatus = server.unregister_request_listener(create_method_uri(), listener)
        self.assertEqual(status.code, UCode.OK)
