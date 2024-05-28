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

from uprotocol.client.transport_wrapper import TransportWrapper
from uprotocol.client.request_listener import RequestListener
from uprotocol.uri.factory.uri_factory import UriFactory

from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri


class RpcServer(TransportWrapper):
    """
    RpcServer is an interface called by uServices to register method
    listeners for incoming RPC requests from clients.
    """

    def register_request_listener(
        self, method: UUri, listener: RequestListener
    ):
        """
        Register a listener for a particular method URI to be notified
        when requests are sent against said method.

        Note: Only one listener is allowed to be registered per method URI.

        @param method Uri for the method to register the listener for.
        @param listener The listener for handling the request method.
        @return Returns the status of registering the RpcListener.
        """
        return self.get_transport().register_listener(
            UriFactory.any_func(), method, listener
        )

    def unregister_request_listener(
        self, method: UUri, listener: RequestListener
    ):
        """
        Unregister an RPC listener for a given method Uri. Messages
        arriving on this topic will no longer be processed by this listener.
        @param method Resolved UUri for where the listener was registered
        to receive messages from.
        @param listener The method to execute to process the
        date for the topic.
        @return Returns status of registering the RpcListener.
        """
        return self.get_transport().unregister_listener(
            UriFactory.any_func(), method, listener
        )
