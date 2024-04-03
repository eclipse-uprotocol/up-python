# -------------------------------------------------------------------------

# Copyright (c) 2023 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: 2023 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0

# -------------------------------------------------------------------------


import re
from uprotocol.proto.uri_pb2 import UResource
from multimethod import multimethod
from typing import Union


class UResourceBuilder:
    MAX_RPC_ID = 1000

    # The minimum topic ID, below this value are methods.
    MIN_TOPIC_ID = 0x8000

    @staticmethod
    def for_rpc_response():
        return UResource(name="rpc", instance="response", id=0)

    @multimethod
    def for_rpc_request(method: Union[str, None]):
        return UResourceBuilder.for_rpc_request(method, None)

    @multimethod
    def for_rpc_request(method: Union[str, None], id: Union[int, None] = None):
        uresource = UResource(name="rpc")
        if method is not None:
            uresource.instance = method
        if id is not None:
            uresource.id = id

        return uresource

    @multimethod
    def for_rpc_request(id: int):
        if id is None:
            raise ValueError("id cannot be None")
        return UResourceBuilder.for_rpc_request(None, id)

    @staticmethod
    def from_id(id):
        if id is None:
            raise ValueError("id cannot be None")

        return (
            UResourceBuilder.for_rpc_response()
            if id == 0
            else (
                UResourceBuilder.for_rpc_request(id)
                if id < UResourceBuilder.MIN_TOPIC_ID
                else UResource(id=id)
            )
        )

    @staticmethod
    def from_uservice_topic(topic):
        """
        Build a UResource from a UServiceTopic that is defined in protos and
        available from generated stubs.
        @param topic The UServiceTopic to build the UResource from.
        @return Returns a UResource for an RPC request.
        """
        if topic is None:
            raise ValueError("topic cannot be None.")
        name_and_instance_parts = re.split(r"[\\.]", topic.name)
        resource_name = name_and_instance_parts[0]
        resource_instance = (
            None
            if len(name_and_instance_parts) <= 1
            else name_and_instance_parts[1]
        )

        resource = UResource(
            name=resource_name, id=topic.id, message=topic.message
        )
        if resource_instance is not None:
            resource.instance = resource_instance

        return resource
