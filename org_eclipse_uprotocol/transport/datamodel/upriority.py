# -------------------------------------------------------------------------

# Copyright (c) 2023 General Motors GTO LLC

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# -------------------------------------------------------------------------
from enum import Enum, unique


@unique
class UPriority(Enum):
    # Low Priority. No bandwidth assurance such as File Transfer.
    LOW = ("CS0", 0)
    # Standard, undifferentiated application such as General (unclassified).
    STANDARD = ("CS1", 1)
    # Operations, Administration, and Management such as Streamer messages (sub, connect, etc…)
    OPERATIONS = ("CS2", 2)
    # Multimedia streaming such as Video Streaming
    MULTIMEDIA_STREAMING = ("CS3", 3)
    # Real-time interactive such as High priority (rpc events)
    REALTIME_INTERACTIVE = ("CS4", 4)
    # Signaling such as Important
    SIGNALING = ("CS5", 5)
    # Network control such as Safety Critical
    NETWORK_CONTROL = ("CS6", 6)

    @property
    def qos_string(self):
        return self.value[0]

    @property
    def int_value(self):
        return self.value[1]

    @classmethod
    def from_int(cls, value: int):
        for item in cls:
            if item.value[1] == value:
                return item
        return None

    @classmethod
    def from_string(cls, value: str):
        for item in cls:
            if item.value[0] == value:
                return item
        return None
