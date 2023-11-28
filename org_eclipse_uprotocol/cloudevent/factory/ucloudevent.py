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


from datetime import datetime, timedelta

from cloudevents.http import CloudEvent
from google.protobuf import any_pb2
from google.protobuf.message import DecodeError
from org_eclipse_uprotocol.proto.ustatus_pb2 import UCode
from org_eclipse_uprotocol.proto.uattributes_pb2 import UMessageType
from org_eclipse_uprotocol.uuid.factory.uuidutils import UUIDUtils
from org_eclipse_uprotocol.uuid.serializer.longuuidserializer import LongUuidSerializer


class UCloudEvent:
    """
    Class to extract  information from a CloudEvent.
    """

    @staticmethod
    def get_source(ce: CloudEvent) -> str:
        """
        Extract the source from a cloud event. The source is a mandatory attribute. The CloudEvent constructor does
        not allow creating a cloud event without a source.<br><br>
        @param ce:CloudEvent with source to be extracted.
        @return:Returns the String value of a CloudEvent source attribute.
        """
        return UCloudEvent.extract_string_value_from_attributes("source", ce)

    @staticmethod
    def get_data_content_type(ce: CloudEvent) -> str:
        """
        Extract the source from a cloud event. The source is a mandatory attribute. The CloudEvent constructor does
        not allow creating a cloud event without a source.<br><br>
        @param ce:CloudEvent with source to be extracted.
        @return:Returns the String value of a CloudEvent source attribute.
        """
        return UCloudEvent.extract_string_value_from_attributes("datacontenttype", ce)

    @staticmethod
    def get_data_schema(ce: CloudEvent) -> str:
        """
        Extract the source from a cloud event. The source is a mandatory attribute. The CloudEvent constructor does
        not allow creating a cloud event without a source.<br><br>
        @param ce:CloudEvent with source to be extracted.
        @return:Returns the String value of a CloudEvent source attribute.
        """
        return UCloudEvent.extract_string_value_from_attributes("dataschema", ce)

    @staticmethod
    def get_type(ce: CloudEvent) -> str:
        """
        Extract the type from a cloud event. The source is a mandatory attribute. The CloudEvent constructor does
        not allow creating a cloud event without a type.<br><br>
        @param ce:CloudEvent with source to be extracted.
        @return:Returns the String value of a CloudEvent type attribute.
        """
        return UCloudEvent.extract_string_value_from_attributes("type", ce)

    @staticmethod
    def get_id(ce: CloudEvent) -> str:
        """
        Extract the id from a cloud event. The id is a mandatory attribute. The CloudEvent constructor does
        not allow creating a cloud event without an id.<br><br>
        @param ce:CloudEvent with source to be extracted.
        @return:Returns the String value of a CloudEvent id attribute.
        """
        return UCloudEvent.extract_string_value_from_attributes("id", ce)

    @staticmethod
    def get_specversion(ce: CloudEvent) -> str:
        """
        Extract the specversion from a cloud event. <br><br>
        @param ce:CloudEvent with source to be extracted.
        @return:Returns the String value of a CloudEvent spec version attribute.
        """
        return UCloudEvent.extract_string_value_from_attributes("specversion", ce)

    @staticmethod
    def get_sink(ce: CloudEvent) -> str:
        """
        Extract the sink from a cloud event. The sink attribute is optional.<br><br>
        @param ce:CloudEvent with sink to be extracted.
        @return:Returns an Optional String value of a CloudEvent sink attribute if it exists, otherwise an
        Optional.empty() is returned.
        """
        return UCloudEvent.extract_string_value_from_attributes("sink", ce)

    @staticmethod
    def get_request_id(ce: CloudEvent) -> str:
        """
        Extract the request id from a cloud event that is a response RPC CloudEvent. The attribute is optional.<br><br>
        @param ce: the response RPC CloudEvent with request id to be extracted.
        @return: Returns an Optional String value of a response RPC CloudEvent request id attribute if it exists,
        otherwise an Optional.empty() is returned.
        """
        return UCloudEvent.extract_string_value_from_attributes("reqid", ce)

    @staticmethod
    def get_hash(ce: CloudEvent) -> str:
        """
        Extract the hash attribute from a cloud event. The hash attribute is optional.<br><br>
        @param ce: CloudEvent with hash to be extracted.
        @return:Returns an Optional String value of a CloudEvent hash attribute if it exists, otherwise an
        Optional.empty() is returned.
        """
        return UCloudEvent.extract_string_value_from_attributes("hash", ce)

    @staticmethod
    def get_priority(ce: CloudEvent) -> str:
        """
        Extract the string value of the priority attribute from a cloud event. The priority attribute is
        optional.<br><br>
        @param ce:CloudEvent with priority to be extracted.
        @return:Returns an Optional String value of a CloudEvent priority attribute if it exists,  otherwise an
        Optional.empty() is returned.
        """
        return UCloudEvent.extract_string_value_from_attributes("priority", ce)

    @staticmethod
    def get_ttl(ce: CloudEvent) -> int:
        """
        Extract the integer value of the ttl attribute from a cloud event. The ttl attribute is optional.<br><br>
        @param ce:CloudEvent with ttl to be extracted.
        @return: Returns an Optional String value of a CloudEvent ttl attribute if it exists,otherwise an
        Optional.empty() is returned.
        """
        ttl_str = UCloudEvent.extract_string_value_from_attributes("ttl", ce)
        return int(ttl_str) if ttl_str is not None else None

    @staticmethod
    def get_token(ce: CloudEvent) -> str:
        """
        Extract the string value of the token attribute from a cloud event. The token attribute is optional.<br><br>
        @param ce: CloudEvent with token to be extracted.
        @return:Returns an Optional String value of a CloudEvent priority token if it exists, otherwise an
        Optional.empty() is returned.
        """
        return UCloudEvent.extract_string_value_from_attributes("token", ce)

    @staticmethod
    def get_communication_status(ce: CloudEvent) -> int:
        """
        Extract the integer value of the communication status attribute from a cloud event. The communication status
        attribute is optional. If there was a platform communication error that occurred while delivering this
        cloudEvent, it will be indicated in this attribute. If the attribute does not exist, it is assumed that
        everything was UCode.OK_VALUE.<br><br>
        @param ce: CloudEvent with the platformError to be extracted.
        @return: Returns a {@link UCode} value that indicates of a platform communication error while delivering this
        CloudEvent or UCode.OK_VALUE.
        """
        comm_status = UCloudEvent.extract_string_value_from_attributes("commstatus", ce)
        return int(comm_status) if comm_status is not None else UCode.OK

    @staticmethod
    def has_communication_status_problem(ce: CloudEvent) -> bool:
        """
        Indication of a platform communication error that occurred while trying to deliver the CloudEvent.<br><br>
        @param ce:CloudEvent to be queried for a platform delivery error.
        @return:returns true if the provided CloudEvent is marked with having a platform delivery problem.
        """
        return UCloudEvent.get_communication_status(ce) != 0

    @staticmethod
    def add_communication_status(ce: CloudEvent, communication_status) -> CloudEvent:
        """
        Returns a new CloudEvent from the supplied CloudEvent, with the platform communication added.<br><br>
        @param ce:CloudEvent that the platform delivery error will be added.
        @param communication_status:the platform delivery error UCode to add to the CloudEvent.
        @return:Returns a new CloudEvent from the supplied CloudEvent, with the platform communication added.
        """
        if communication_status is None:
            return ce
        ce.__setitem__("commstatus", communication_status)
        return ce

    @staticmethod
    def get_creation_timestamp(ce: CloudEvent) -> int:
        """
        Extract the timestamp from the UUIDV8 CloudEvent Id.<br><br>
        @param ce:The CloudEvent with the timestamp to extract.
        @return:Return the timestamp from the UUIDV8 CloudEvent Id or an empty Optional if timestamp can't be extracted.
        """
        cloud_event_id = UCloudEvent.extract_string_value_from_attributes("id", ce)
        uuid = LongUuidSerializer.instance().deserialize(cloud_event_id)

        return UUIDUtils.getTime(uuid) if uuid is not None else None

    @staticmethod
    def is_expired_by_cloud_event_creation_date(ce: CloudEvent) -> bool:
        """
        Calculate if a CloudEvent configured with a creation time and a ttl attribute is expired. The ttl attribute
        is a configuration of how long this event should live for after it was generated (in milliseconds)<br><br>
        @param ce:The CloudEvent to inspect for being expired.
        @return:Returns true if the CloudEvent was configured with a ttl &gt; 0 and a creation time to compare for
        expiration.
        """
        maybe_ttl = UCloudEvent.get_ttl(ce)
        if not maybe_ttl or maybe_ttl <= 0:
            return False

        cloud_event_creation_time = UCloudEvent.extract_string_value_from_attributes("time", ce)
        if cloud_event_creation_time is None:
            return False

        now = datetime.now()
        creation_time_plus_ttl = cloud_event_creation_time + timedelta(milliseconds=maybe_ttl)

        return now > creation_time_plus_ttl

    @staticmethod
    def is_expired(ce: CloudEvent) -> bool:
        """
        Calculate if a CloudEvent configured with UUIDv8 id and a ttl attribute is expired. The ttl attribute is a
        configuration of how long this event should live for after it was generated (in milliseconds).<br><br>
        @param ce:The CloudEvent to inspect for being expired.
        @return:Returns true if the CloudEvent was configured with a ttl &gt; 0 and UUIDv8 id to compare for expiration.
        """
        maybe_ttl = UCloudEvent.get_ttl(ce)
        if not maybe_ttl or maybe_ttl <= 0:
            return False
        cloud_event_id = UCloudEvent.extract_string_value_from_attributes("id", ce)

        try:
            uuid = LongUuidSerializer.instance().deserialize(cloud_event_id)
            if uuid is None:
                return False
            delta = datetime.utcnow().timestamp() - UUIDUtils.getTime(uuid)
        except ValueError:
            # Invalid UUID, handle accordingly
            delta = 0
        return delta >= maybe_ttl

    @staticmethod
    def is_cloud_event_id(ce: CloudEvent) -> bool:
        """
        Check if a CloudEvent is a valid UUIDv6 or v8 .<br><br>
        @param ce:The CloudEvent with the id to inspect.
        @return: Returns true if the CloudEvent is valid.
        """
        cloud_event_id = UCloudEvent.extract_string_value_from_attributes("id", ce)
        uuid = LongUuidSerializer.instance().deserialize(cloud_event_id)

        return uuid is not None and UUIDUtils.isuuid(uuid)

    @staticmethod
    def get_payload(ce: CloudEvent) -> any_pb2.Any:
        """
        Extract the payload from the CloudEvent as a protobuf Any object. <br>An all or nothing error handling
        strategy is implemented. If anything goes wrong, an Any.getDefaultInstance() will be returned.<br><br>
        @param ce:CloudEvent containing the payload to extract.
        @return:Extracts the payload from a CloudEvent as a Protobuf Any object.
        """
        data = ce.get_data()
        if data is None:
            return any_pb2.Any()
        try:
            return any_pb2.Any().FromString(data)
        except DecodeError:
            return any_pb2.Any()

    @staticmethod
    def unpack(ce: CloudEvent, clazz):
        """
        Extract the payload from the CloudEvent as a protobuf Message of the provided class. The protobuf of this
        message class must be loaded on the client for this to work. <br>  An all or nothing error handling strategy
        is implemented. If anything goes wrong, an empty optional will be returned. <br><br> Example: <br>
        <pre>Optional&lt;SomeMessage&gt; unpacked = UCloudEvent.unpack(cloudEvent, SomeMessage.class);</pre><br><br>
        @param ce:CloudEvent containing the payload to extract.
        @param clazz:The class that extends {@link Message} that the payload is extracted into.
        @return:  Returns a {@link Message} payload of the class type that is provided.
        """
        try:
            any_obj=UCloudEvent.get_payload(ce)
            value = clazz()
            value.ParseFromString(any_obj.value)
            return value
        except DecodeError:
            return None

    @staticmethod
    def to_string(ce: CloudEvent) -> str:
        """
        Function used to pretty print a CloudEvent containing only the id, source, type and maybe a sink. Used mainly
        for logging.<br><br>
        @param ce:The CloudEvent we want to pretty print.
        @return:returns the String representation of the CloudEvent containing only the id, source, type and maybe a
        sink.
        """
        if ce is not None:
            sink_str = UCloudEvent.get_sink(ce)
            sink_str = f", sink='{sink_str}'" if sink_str is not None else ""
            id = UCloudEvent.extract_string_value_from_attributes("id", ce)
            source = UCloudEvent.extract_string_value_from_attributes("source", ce)
            type = UCloudEvent.extract_string_value_from_attributes("type", ce)
            return f"CloudEvent{{id='{id}', source='{source}'{sink_str}, type='{type}'}}"
        else:
            return "null"

    @staticmethod
    def extract_string_value_from_attributes(attr_name, ce: CloudEvent) -> str:
        """
        Utility for extracting the String value of an attribute.<br><br>
        @param attr_name:The name of the CloudEvent attribute.
        @param ce:The CloudEvent containing the data.
        @return:the Optional String value of an attribute matching the attribute name, or an Optional.empty() is the
        value does not exist.
        """

        return ce.get_attributes().get(attr_name)

    @staticmethod
    def extract_integer_value_from_attributes(attr_name, ce: CloudEvent) -> int:
        """

        Utility for extracting the Integer value of an attribute.<br><br>
        @param attr_name:The name of the CloudEvent attribute.
        @param ce:The CloudEvent containing the data.
        @return:returns the Optional Integer value of an attribute matching the attribute name,or an Optional.empty()
        is the value does not exist.
        """
        value = UCloudEvent.extract_string_value_from_attributes(attr_name, ce)
        return int(value) if value is not None else None

    @staticmethod
    def get_event_type(type):
        return {UMessageType.UMESSAGE_TYPE_PUBLISH: "pub.v1", UMessageType.UMESSAGE_TYPE_REQUEST: "req.v1",
            UMessageType.UMESSAGE_TYPE_RESPONSE: "res.v1"}.get(type, "")

    @staticmethod
    def get_message_type(ce_type):
        return {"pub.v1": UMessageType.UMESSAGE_TYPE_PUBLISH, "req.v1": UMessageType.UMESSAGE_TYPE_REQUEST,
            "res.v1": UMessageType.UMESSAGE_TYPE_RESPONSE}.get(ce_type, UMessageType.UMESSAGE_TYPE_UNSPECIFIED)
