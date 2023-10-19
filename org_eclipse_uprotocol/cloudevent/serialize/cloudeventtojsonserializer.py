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
import json

from cloudevents.sdk.event.v1 import Event

from org_eclipse_uprotocol.cloudevent.serialize.cloudeventserializer import CloudEventSerializer


class CloudEventToJsonSerializer(CloudEventSerializer):
    def __init__(self):
        self.serializer = json.JSONEncoder(indent=2, sort_keys=False)

    def cloud_event_to_dict(self, ce: Event):
        """
        Convert a CloudEvent instance to a Python dictionary.
        """
        cloud_event_dict = {"specversion": ce.specversion, "type": ce.type, "source": ce.source, "id": ce.id,
                            "time": ce.time, "datacontenttype": ce.content_type, "dataschema": ce.schema,
                            "subject": ce.subject, "data": ce.data, "extensions": ce.extensions, }
        return cloud_event_dict

    def cloud_dict_to_cloud_event(self, ce_dict: dict):
        """
        Convert a CloudEvent dict to a Cloudevent instance.
        """

        event = Event()
        if 'type' in ce_dict:
            event.SetEventType(ce_dict['type'])
        if 'source' in ce_dict:
            event.SetSource(ce_dict['source'])
        if 'datacontenttype' in ce_dict:
            event.SetContentType(ce_dict['datacontenttype'])
        if 'id' in ce_dict:
            event.SetEventID(ce_dict['id'])
        if 'data' in ce_dict:
            event.SetData(ce_dict['data'])
        if 'extensions' in ce_dict:
            event.SetExtensions(ce_dict['extensions'])
        if 'time' in ce_dict:
            event.SetEventTime(ce_dict['time'])
        if 'dataschema' in ce_dict:
            event.SetSchema(ce_dict['dataschema'])
        if 'subject' in ce_dict:
            event.SetSubject(ce_dict['subject'])

        return event

    def serialize(self, ce: Event) -> bytes:
        ce_dict = self.cloud_event_to_dict(ce)
        return self.serializer.encode(ce_dict).encode('utf-8')

    def deserialize(self, bytes_data: bytes) -> Event:
        cloud_event_dict = json.loads(bytes_data.decode('utf-8'))
        return self.cloud_dict_to_cloud_event(cloud_event_dict)
