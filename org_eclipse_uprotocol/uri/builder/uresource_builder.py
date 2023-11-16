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


from org_eclipse_uprotocol.proto.uri_pb2 import UResource


class UResourceBuilder:
    MAX_RPC_ID = 1000

    @staticmethod
    def for_rpc_response():
        return UResource(name="rpc", instance="response", id=0)

    @staticmethod
    def for_rpc_request(method, id=None):
        uresource = UResource(name="rpc")
        if method is not None:
            uresource.instance = method
        if id is not None:
            uresource.id = id

        return uresource

    @staticmethod
    def for_rpc_request_with_id(id):
        return UResourceBuilder.for_rpc_request(None, id)

    @staticmethod
    def from_id(id):
        if id is None:
            raise ValueError("id cannot be None")

        return UResourceBuilder.for_rpc_request_with_id(id) if id < UResourceBuilder.MAX_RPC_ID else UResource(id=id)
