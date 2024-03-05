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

from abc import ABC, abstractmethod
from concurrent.futures import Future

from uprotocol.proto.umessage_pb2 import UMessage

class URpcListener(ABC):
    '''
    uService (servers) implement this to receive requests messages from clients. <br>
    The service must implement the onReceive(UMessage, CompletableFuture) method to handle
    the request and then complete the future passed to the method that triggers the uLink library to
    send (over the transport) the response.
    '''
    
    @abstractmethod
    def on_receive(message: UMessage, response_future: Future) -> None:
        '''
        Method called to handle/process events.
        @param message Message received.
        '''
        pass