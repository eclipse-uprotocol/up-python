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

from enum import Enum
from typing import Optional


class UCloudEventType(Enum):
    """
    Enumeration for the core types of uProtocol CloudEvents.
    """
    PUBLISH = "pub.v1"
    REQUEST = "req.v1"
    RESPONSE = "res.v1"

    def type(self) -> str:
        return self.value

    @staticmethod
    def value_of_type(typestr: str) -> Optional['UCloudEventType']:
        """
        Convert a String type into a maybe UCloudEventType.<br><br>
        @param typestr: The String value of the UCloudEventType.
        @return: returns the UCloudEventType associated with the provided String.
        """
        for ce_type in UCloudEventType:
            if ce_type.type() == typestr:
                return ce_type
        return None
