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


from cloudevents.http import CloudEvent
from google.protobuf import empty_pb2
from google.protobuf.any_pb2 import Any

from org_eclipse_uprotocol.cloudevent.datamodel.ucloudeventattributes import UCloudEventAttributes
from org_eclipse_uprotocol.cloudevent.factory.ucloudevent import UCloudEvent
from org_eclipse_uprotocol.proto.uattributes_pb2 import UMessageType
from org_eclipse_uprotocol.uuid.factory.uuidfactory import Factories
from org_eclipse_uprotocol.uuid.serializer.longuuidserializer import LongUuidSerializer


# A factory is a part of the software has methods to generate concrete objects, usually of the same type or
# interface. CloudEvents is a specification for describing events in a common way. We will use CloudEvents to
# formulate all kinds of  events (messages) that will be sent to and from devices. The CloudEvent factory knows how
# to generate CloudEvents of the 4 core types: req.v1, res.v1, pub.v1, and file.v1
class CloudEventFactory:
    PROTOBUF_CONTENT_TYPE = "application/x-protobuf"

    @staticmethod
    def request(application_uri_for_rpc: str, service_method_uri: str, request_id: str, proto_payload: Any,
                attributes: UCloudEventAttributes) -> CloudEvent:
        """
        Create a CloudEvent for an event for the use case of: RPC Request message.
        @param application_uri_for_rpc: The uri for the application requesting the RPC.
        @param service_method_uri: The uri for the method to be called on the service Ex. :/body.access/1/rpc.UpdateDoor
        @param request_id:The attribute id from the original request
        @param proto_payload:Protobuf Any object with the Message command to be executed on the sink service.
        @param attributes: Additional attributes such as ttl, hash, priority and token.
        @return: Returns an  request CloudEvent.
        """
        event_id = CloudEventFactory.generate_cloud_event_id()
        cloud_event = CloudEventFactory.build_base_cloud_event(event_id, application_uri_for_rpc,

                                                               proto_payload.SerializeToString(),
                                                               proto_payload.DESCRIPTOR.full_name, attributes,
                                                               UCloudEvent.get_event_type(
                                                                   UMessageType.UMESSAGE_TYPE_REQUEST)
                                                               )
        cloud_event.__setitem__("sink", service_method_uri)
        cloud_event.__setitem__("reqid", request_id)

        return cloud_event

    @staticmethod
    def response(application_uri_for_rpc: str, service_method_uri: str, request_id: str, proto_payload: Any,
                 attributes: UCloudEventAttributes) -> CloudEvent:
        """
        Create a CloudEvent for an event for the use case of: RPC Response message.
        @param application_uri_for_rpc: The destination of the response. The uri for the original application that
        requested the RPC and this response is for.
        @param service_method_uri: The uri for the method that was called on the service Ex.
        :/body.access/1/rpc.UpdateDoor
        @param request_id:The cloud event id from the original request cloud event that this response if for.
        @param proto_payload: The protobuf serialized response message as defined by the application interface or the
        UStatus message containing the details of an error.
        @param attributes: Additional attributes such as ttl, hash and priority.
        @return: Returns an  response CloudEvent.
        """
        event_id = CloudEventFactory.generate_cloud_event_id()
        cloud_event = CloudEventFactory.build_base_cloud_event(event_id, service_method_uri,

                                                               proto_payload.SerializeToString(),
                                                               proto_payload.DESCRIPTOR.full_name, attributes,
                                                               UCloudEvent.get_event_type(
                                                                   UMessageType.UMESSAGE_TYPE_RESPONSE))
        cloud_event.__setitem__("sink", application_uri_for_rpc)
        cloud_event.__setitem__("reqid", request_id)

        return cloud_event

    @staticmethod
    def failed_response(application_uri_for_rpc: str, service_method_uri: str, request_id: str,
                        communication_status: int, attributes: UCloudEventAttributes) -> CloudEvent:
        """
        Create a CloudEvent for an event for the use case of: RPC Response message that failed.
        @param application_uri_for_rpc: The destination of the response. The uri for the original application that
        requested the RPC and this response is for.
        @param service_method_uri: The uri for the method that was called on the service Ex.
        :/body.access/1/rpc.UpdateDoor
        @param request_id:The cloud event id from the original request cloud event that this response if for.
        @param communication_status: A {@link Code} value that indicates of a platform communication error while
        delivering this CloudEvent.
        @param attributes:Additional attributes such as ttl, hash and priority.
        @return:Returns an  response CloudEvent Response for the use case of RPC Response message that failed.
        """
        event_id = CloudEventFactory.generate_cloud_event_id()
        # Create an Any message packing an Empty message
        empty_proto_payload = Any()
        empty_proto_payload.Pack(empty_pb2.Empty())
        cloud_event = CloudEventFactory.build_base_cloud_event(event_id, service_method_uri,

                                                               empty_proto_payload.SerializeToString(),  # Empty payload
                                                               "google.protobuf.Empty", attributes,
                                                               UCloudEvent.get_event_type(
                                                                   UMessageType.UMESSAGE_TYPE_RESPONSE)
                                                               )
        cloud_event.__setitem__("sink", application_uri_for_rpc)
        cloud_event.__setitem__("reqid", request_id)
        cloud_event.__setitem__("commstatus", communication_status)

        return cloud_event

    @staticmethod
    def publish(source: str, proto_payload: Any, attributes: UCloudEventAttributes) -> CloudEvent:
        """
        Create a CloudEvent for an event for the use case of: Publish generic message.
        @param source:The  uri of the topic being published.
        @param proto_payload:protobuf Any object with the Message to be published.
        @param attributes:Additional attributes such as ttl, hash and priority.
        @return:Returns a publish CloudEvent.
        """
        event_id = CloudEventFactory.generate_cloud_event_id()
        cloud_event = CloudEventFactory.build_base_cloud_event(event_id, source, proto_payload.SerializeToString(),
                                                               proto_payload.DESCRIPTOR.full_name, attributes,
                                                               UCloudEvent.get_event_type(
                                                                   UMessageType.UMESSAGE_TYPE_PUBLISH))

        return cloud_event

    @staticmethod
    def notification(source: str, sink: str, proto_payload: Any, attributes: UCloudEventAttributes) -> CloudEvent:
        """
        Create a CloudEvent for an event for the use case of: Publish a notification message. A published event
        containing the sink (destination) is often referred to as a notification, it is an event sent to a specific
        consumer.
        @param source: The  uri of the topic being published.
        @param sink:  The  uri of the destination of this notification.
        @param proto_payload: protobuf Any object with the Message to be published.
        @param attributes:  Additional attributes such as ttl, hash and priority.
        @return: Returns a publish CloudEvent.
        """
        event_id = CloudEventFactory.generate_cloud_event_id()
        cloud_event = CloudEventFactory.build_base_cloud_event(event_id, source, proto_payload.SerializeToString(),
                                                               proto_payload.DESCRIPTOR.full_name, attributes,
                                                               UCloudEvent.get_event_type(
                                                                   UMessageType.UMESSAGE_TYPE_PUBLISH))
        cloud_event.__setitem__("sink", sink)

        return cloud_event

    @staticmethod
    def generate_cloud_event_id() -> str:
        """
        Generate a UUIDv8
        @return:  Returns a UUIDv8 id.
        """
        uuid_inst = Factories.UPROTOCOL.create()
        return LongUuidSerializer.instance().serialize(uuid_inst)

    @staticmethod
    def build_base_cloud_event(id: str, source: str, proto_payload_bytes: bytes, proto_payload_schema: str,
                               attributes: UCloudEventAttributes, type) -> CloudEvent:
        """
        Base CloudEvent builder that is the same for all CloudEvent types.
        
        @param id:Event unique identifier.
        @param source: Identifies who is sending this event in the format of a uProtocol URI that can be built from a
        {@link UUri} object.
        @param proto_payload_bytes:The serialized Event data with the content type of "application/x-protobuf".
        @param proto_payload_schema:The schema of the proto payload bytes, for example you can use
        <code>protoPayload.getTypeUrl()</code> on your service/app object.
        @param attributes:Additional cloud event attributes that can be passed in. All attributes are optional and
        will be added only if they were configured.
        @param type: Type of the cloud event
        @return:Returns a CloudEventBuilder that can be additionally configured and then by calling .build()
        construct a CloudEvent ready to be serialized and sent to the transport layer.
        """
        json_attributes = {"id": id, "source": source, "type": type}
        if attributes.get_hash() is not None:
            json_attributes['hash'] = attributes.get_hash()
        if attributes.get_ttl() is not None:
            json_attributes['ttl'] = attributes.get_ttl()
        if attributes.get_priority() is not None:
            json_attributes['priority'] = attributes.get_priority()
        if attributes.get_token() is not None:
            json_attributes['token'] = attributes.get_token()

        cloud_event = CloudEvent(json_attributes, proto_payload_bytes)

        return cloud_event
