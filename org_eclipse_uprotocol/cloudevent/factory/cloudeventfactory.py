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
from cloudevents.sdk.event import v1
from cloudevents.sdk.event.v1 import Event
from google.protobuf import empty_pb2
from google.protobuf.any_pb2 import Any

from org_eclipse_uprotocol.cloudevent.datamodel.ucloudeventattributes import UCloudEventAttributes
from org_eclipse_uprotocol.cloudevent.datamodel.ucloudeventtype import UCloudEventType
from org_eclipse_uprotocol.cloudevent.factory.ucloudevent import UCloudEvent
from org_eclipse_uprotocol.cloudevent.serialize.base64protobufserializer import Base64ProtobufSerializer
from org_eclipse_uprotocol.transport.datamodel.upriority import UPriority
from org_eclipse_uprotocol.uri.datamodel.uauthority import UAuthority
from org_eclipse_uprotocol.uri.datamodel.uentity import UEntity
from org_eclipse_uprotocol.uri.datamodel.uresource import UResource
from org_eclipse_uprotocol.uri.datamodel.uuri import UUri
from org_eclipse_uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from org_eclipse_uprotocol.uuid.factory.uuidfactory import Factories


class CloudEventFactory:
    PROTOBUF_CONTENT_TYPE = "application/x-protobuf"

    @staticmethod
    def request(application_uri_for_rpc: str, service_method_uri: str, request_id: str, proto_payload: Any,
                attributes: UCloudEventAttributes) -> Event:
        event_id = CloudEventFactory.generate_cloud_event_id()
        event = CloudEventFactory.build_base_cloud_event(event_id, application_uri_for_rpc,
                                                         Base64ProtobufSerializer.deserialize(
                                                             proto_payload.SerializeToString()),
                                                         proto_payload.DESCRIPTOR.full_name, attributes)
        event.SetEventType(UCloudEventType.REQUEST.type())
        ext = event.Get("Extensions")[0]
        ext["sink"] = service_method_uri
        ext["reqid"] = request_id
        event.SetExtensions(ext)
        return event

    @staticmethod
    def response(application_uri_for_rpc: str, service_method_uri: str, request_id: str, proto_payload: Any,
                 attributes: UCloudEventAttributes) -> Event:
        event_id = CloudEventFactory.generate_cloud_event_id()
        event = CloudEventFactory.build_base_cloud_event(event_id, service_method_uri,
                                                         Base64ProtobufSerializer.deserialize(
                                                             proto_payload.SerializeToString()),
                                                         proto_payload.DESCRIPTOR.full_name, attributes)
        event.SetEventType(UCloudEventType.RESPONSE.type())
        ext = event.Get("Extensions")[0]
        ext["sink"] = application_uri_for_rpc
        ext["reqid"] = request_id
        event.SetExtensions(ext)

        return event

    @staticmethod
    def failed_response(application_uri_for_rpc: str, service_method_uri: str, request_id: str,
                        communication_status: int, attributes: UCloudEventAttributes) -> Event:
        event_id = CloudEventFactory.generate_cloud_event_id()
        # Create an Any message packing an Empty message
        empty_proto_payload = Any()
        empty_proto_payload.Pack(empty_pb2.Empty())
        event = CloudEventFactory.build_base_cloud_event(event_id, service_method_uri,
                                                         Base64ProtobufSerializer.deserialize(
                                                             empty_proto_payload.SerializeToString()),  # Empty payload
                                                         "google.protobuf.Empty", attributes)
        event.SetEventType(UCloudEventType.RESPONSE.type())
        ext = event.Get("Extensions")[0]
        ext["sink"] = application_uri_for_rpc
        ext["reqid"] = request_id
        ext["commstatus"] = communication_status
        event.SetExtensions(ext)

        return event

    @staticmethod
    def publish(source: str, proto_payload: Any, attributes: UCloudEventAttributes) -> Event:
        event_id = CloudEventFactory.generate_cloud_event_id()
        event = CloudEventFactory.build_base_cloud_event(event_id, source, Base64ProtobufSerializer.deserialize(
            proto_payload.SerializeToString()), proto_payload.DESCRIPTOR.full_name, attributes)
        event.SetEventType(UCloudEventType.PUBLISH.type())
        return event

    @staticmethod
    def notification(source: str, sink: str, proto_payload: Any, attributes: UCloudEventAttributes) -> Event:
        event_id = CloudEventFactory.generate_cloud_event_id()
        event = CloudEventFactory.build_base_cloud_event(event_id, source, Base64ProtobufSerializer.deserialize(
            proto_payload.SerializeToString()), proto_payload.DESCRIPTOR.full_name, attributes)
        event.SetEventType(UCloudEventType.PUBLISH.type())
        ext = event.Get("Extensions")[0]
        ext["sink"] = sink
        event.SetExtensions(ext)
        return event

    @staticmethod
    def generate_cloud_event_id() -> str:
        # uuid8
        uuid_inst = Factories.UPROTOCOL.create()
        return str(uuid_inst)

    @staticmethod
    def build_base_cloud_event(id: str, source: str, proto_payload_bytes: str, proto_payload_schema: str,
                               attributes: UCloudEventAttributes) -> Event:
        # Set extensions
        extensions = {}
        if attributes.ttl:
            extensions["ttl"] = attributes.ttl

        if attributes.priority:
            extensions["priority"] = attributes.priority

        if attributes.hash:
            extensions["hash"] = attributes.hash

        if attributes.token:
            extensions["token"] = attributes.token

        cloud_event = v1.Event()
        cloud_event.SetEventID(id)
        cloud_event.SetSource(source)
        cloud_event.SetData(proto_payload_bytes)
        cloud_event.SetExtensions(extensions)
        return cloud_event
