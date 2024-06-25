"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from dataclasses import dataclass, field

from uprotocol.v1.uattributes_pb2 import UPriority


@dataclass(frozen=True)
class CallOptions:
    DEFAULT = None
    timeout: int = field(default=10000)
    priority: UPriority = field(default=UPriority.UPRIORITY_CS4)
    token: str = field(default="")

    def __post_init__(self):
        if self.timeout is None:
            raise ValueError("timeout cannot be None")
        if self.priority is None:
            raise ValueError("priority cannot be None")
        if self.token is None:
            raise ValueError("token cannot be None")


# Default instance
CallOptions.DEFAULT = CallOptions()

# Example usage:
if __name__ == "__main__":
    options = CallOptions()
    options1 = CallOptions(timeout=5000, priority=UPriority.UPRIORITY_CS4)
    options2 = CallOptions(token="gbb")
