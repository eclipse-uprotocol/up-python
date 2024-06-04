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


from cloudevents.http import CloudEvent

from uprotocol.cloudevent.serialize.cloudeventserializer import (
    CloudEventSerializer,
)
from uprotocol.cloudevent import cloudevents_pb2


class CloudEventToProtobufSerializer(CloudEventSerializer):
    """
    CloudEventSerializer to serialize and deserialize CloudEvents to protobuf format.
    """

    def __init__(self):
        pass

    def serialize(self, http_event: CloudEvent) -> bytes:
        proto_event = cloudevents_pb2.CloudEvent()
        # Set required attributes
        proto_event.id = http_event["id"]
        proto_event.source = http_event["source"]
        proto_event.spec_version = http_event["specversion"]
        proto_event.type = http_event["type"]

        # Set optional & extension attributes
        for key, value in http_event.get_attributes().items():
            if key not in ["specversion", "id", "source", "type", "data"]:
                attribute_value = proto_event.attributes[key]
                if isinstance(value, bool):
                    attribute_value.ce_boolean = value
                elif isinstance(value, int):
                    attribute_value.ce_integer = value
                elif isinstance(value, str):
                    attribute_value.ce_string = value
                elif isinstance(value, bytes):
                    attribute_value.ce_bytes = value

        # Set data
        data = http_event.get_data()
        if isinstance(data, bytes):
            proto_event.binary_data = data
        elif isinstance(data, str):
            proto_event.text_data = data

        return proto_event.SerializeToString()

    def deserialize(self, bytes_data: bytes) -> CloudEvent:
        proto_event = cloudevents_pb2.CloudEvent()
        proto_event.ParseFromString(bytes_data)

        json_attributes = {
            "id": proto_event.id,
            "source": proto_event.source,
            "type": proto_event.type,
            "specversion": proto_event.spec_version,
        }

        # Set optional & extension attributes
        for key in proto_event.attributes:
            if key not in ["specversion", "id", "source", "type", "data"]:
                attribute_value = proto_event.attributes[key]
                if attribute_value.HasField("ce_boolean"):
                    json_attributes[key] = attribute_value.ce_boolean
                elif attribute_value.HasField("ce_integer"):
                    json_attributes[key] = attribute_value.ce_integer
                elif attribute_value.HasField("ce_string"):
                    json_attributes[key] = attribute_value.ce_string
                elif attribute_value.HasField("ce_bytes"):
                    json_attributes[key] = attribute_value.ce_bytes

        # Set data
        data = bytearray()
        if proto_event.HasField("binary_data"):
            data = proto_event.binary_data
        elif proto_event.HasField("text_data"):
            data = proto_event.text_data

        cloud_event = CloudEvent(json_attributes, data)

        return cloud_event
