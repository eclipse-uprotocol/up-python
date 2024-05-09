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


from cloudevents.conversion import to_json
from cloudevents.http import CloudEvent, from_json

from uprotocol.cloudevent.serialize.cloudeventserializer import CloudEventSerializer


class CloudEventToJsonSerializer(CloudEventSerializer):
    """
    CloudEventSerializer to serialize and deserialize CloudEvents to JSON format.
    """

    def serialize(self, ce: CloudEvent) -> bytes:
        return to_json(ce)

    def deserialize(self, bytes_data: bytes) -> CloudEvent:
        return from_json(bytes_data)
