# -------------------------------------------------------------------------
# Copyright (c) 2023 General Motors GTO LLC

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License") you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# -------------------------------------------------------------------------

from cloudevents.http import CloudEvent
from google.protobuf import empty_pb2
from google.protobuf.any_pb2 import Any

from org_eclipse_uprotocol.cloudevent.datamodel.ucloudeventattributes import UCloudEventAttributes
from org_eclipse_uprotocol.cloudevent.datamodel.ucloudeventtype import UCloudEventType
from org_eclipse_uprotocol.uuid.factory.uuidfactory import Factories


class CloudEventFactory:
    PROTOBUF_CONTENT_TYPE = "application/x-protobuf"

    @staticmethod
    def request(application_uri_for_rpc: str, service_method_uri: str, request_id: str, proto_payload: Any,
                attributes: UCloudEventAttributes) -> CloudEvent:
        event_id = CloudEventFactory.generate_cloud_event_id()
        cloud_event = CloudEventFactory.build_base_cloud_event(event_id, application_uri_for_rpc,

                                                               proto_payload.SerializeToString(),
                                                               proto_payload.DESCRIPTOR.full_name, attributes,
                                                               UCloudEventType.REQUEST.type())
        cloud_event.__setitem__("sink", service_method_uri)
        cloud_event.__setitem__("reqid", request_id)
        return cloud_event

    @staticmethod
    def response(application_uri_for_rpc: str, service_method_uri: str, request_id: str, proto_payload: Any,
                 attributes: UCloudEventAttributes) -> CloudEvent:
        event_id = CloudEventFactory.generate_cloud_event_id()
        cloud_event = CloudEventFactory.build_base_cloud_event(event_id, service_method_uri,

                                                               proto_payload.SerializeToString(),
                                                               proto_payload.DESCRIPTOR.full_name, attributes,
                                                               UCloudEventType.RESPONSE.type())
        cloud_event.__setitem__("sink", application_uri_for_rpc)
        cloud_event.__setitem__("reqid", request_id)
        return cloud_event

    @staticmethod
    def failed_response(application_uri_for_rpc: str, service_method_uri: str, request_id: str,
                        communication_status: int, attributes: UCloudEventAttributes) -> CloudEvent:
        event_id = CloudEventFactory.generate_cloud_event_id()
        # Create an Any message packing an Empty message
        empty_proto_payload = Any()
        empty_proto_payload.Pack(empty_pb2.Empty())
        cloud_event = CloudEventFactory.build_base_cloud_event(event_id, service_method_uri,

                                                               empty_proto_payload.SerializeToString(),  # Empty payload
                                                               "google.protobuf.Empty", attributes,
                                                               UCloudEventType.RESPONSE.type())
        cloud_event.__setitem__("sink", application_uri_for_rpc)
        cloud_event.__setitem__("reqid", request_id)
        cloud_event.__setitem__("commstatus", communication_status)

        return cloud_event

    @staticmethod
    def publish(source: str, proto_payload: Any, attributes: UCloudEventAttributes) -> CloudEvent:
        event_id = CloudEventFactory.generate_cloud_event_id()
        cloud_event = CloudEventFactory.build_base_cloud_event(event_id, source, proto_payload.SerializeToString(),
                                                               proto_payload.DESCRIPTOR.full_name, attributes,
                                                               UCloudEventType.PUBLISH.type())
        return cloud_event

    @staticmethod
    def notification(source: str, sink: str, proto_payload: Any, attributes: UCloudEventAttributes) -> CloudEvent:
        event_id = CloudEventFactory.generate_cloud_event_id()
        cloud_event = CloudEventFactory.build_base_cloud_event(event_id, source, proto_payload.SerializeToString(),
                                                               proto_payload.DESCRIPTOR.full_name, attributes,
                                                               UCloudEventType.PUBLISH.type())
        cloud_event.__setitem__("sink", sink)
        return cloud_event

    @staticmethod
    def generate_cloud_event_id() -> str:
        # uuid8
        uuid_inst = Factories.UPROTOCOL.create()
        return str(uuid_inst)

    @staticmethod
    def build_base_cloud_event(id: str, source: str, proto_payload_bytes: bytes, proto_payload_schema: str,
                               attributes: UCloudEventAttributes, type) -> CloudEvent:
        json_attributes = {"ttl": attributes.ttl, "priority": attributes.priority, "hash": attributes.hash,
                           "token": attributes.token, "id": id, "source": source, "type": type}

        cloud_event = CloudEvent(json_attributes, proto_payload_bytes)

        return cloud_event
