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

from datetime import datetime, timedelta

from cloudevents.http import CloudEvent
from google.protobuf import any_pb2
from google.protobuf.message import DecodeError
from google.rpc.code_pb2 import Code

from org_eclipse_uprotocol.uuid.factory.uuidutils import UUIDUtils


class UCloudEvent:
    @staticmethod
    def get_source(ce: CloudEvent) -> str:
        return UCloudEvent.extract_string_value_from_attributes("source", ce)

    @staticmethod
    def get_sink(ce: CloudEvent) -> str:
        return UCloudEvent.extract_string_value_from_attributes("sink", ce)

    @staticmethod
    def get_request_id(ce: CloudEvent) -> str:
        return UCloudEvent.extract_string_value_from_attributes("reqid", ce)

    @staticmethod
    def get_hash(ce: CloudEvent) -> str:
        return UCloudEvent.extract_string_value_from_attributes("hash", ce)

    @staticmethod
    def get_priority(ce: CloudEvent) -> str:
        return UCloudEvent.extract_string_value_from_attributes("priority", ce)

    @staticmethod
    def get_ttl(ce: CloudEvent) -> int:
        ttl_str = UCloudEvent.extract_string_value_from_attributes("ttl", ce)
        return int(ttl_str) if ttl_str is not None else None

    @staticmethod
    def get_token(ce: CloudEvent) -> str:
        return UCloudEvent.extract_string_value_from_attributes("token", ce)

    @staticmethod
    def get_communication_status(ce: CloudEvent) -> int:
        comm_status = UCloudEvent.extract_string_value_from_attributes("commstatus", ce)
        return int(comm_status) if comm_status is not None else Code.OK

    @staticmethod
    def has_communication_status_problem(ce: CloudEvent) -> bool:
        return UCloudEvent.get_communication_status(ce) != 0

    @staticmethod
    def add_communication_status(ce: CloudEvent, communication_status) -> CloudEvent:
        if communication_status is None:
            return ce
        ce.__setitem__("commstatus", communication_status)
        return ce

    @staticmethod
    def get_creation_timestamp(ce: CloudEvent) -> int:
        cloud_event_id = UCloudEvent.extract_string_value_from_attributes("id", ce)
        uuid = UUIDUtils.fromString(cloud_event_id)

        return UUIDUtils.getTime(uuid) if uuid is not None else None

    @staticmethod
    def is_expired_by_cloud_event_creation_date(ce: CloudEvent) -> bool:
        maybe_ttl = UCloudEvent.get_ttl(ce)
        if maybe_ttl is None or maybe_ttl <= 0:
            return False

        cloud_event_creation_time = UCloudEvent.extract_string_value_from_attributes("time", ce)
        if cloud_event_creation_time is None:
            return False

        now = datetime.now()
        creation_time_plus_ttl = cloud_event_creation_time + timedelta(milliseconds=maybe_ttl)

        return now > creation_time_plus_ttl

    @staticmethod
    def is_expired(ce: CloudEvent) -> bool:
        maybe_ttl = UCloudEvent.get_ttl(ce)
        if maybe_ttl is None or maybe_ttl <= 0:
            return False
        cloud_event_id = UCloudEvent.extract_string_value_from_attributes("id", ce)

        try:
            uuid = UUIDUtils.fromString(cloud_event_id)
            if uuid is None:
                return False
            delta = datetime.utcnow().timestamp() - UUIDUtils.getTime(uuid).timestamp()
        except ValueError:
            # Invalid UUID, handle accordingly
            delta = 0
        return delta >= maybe_ttl

    # Check if a CloudEvent is a valid UUIDv6 or v8 .
    @staticmethod
    def is_cloud_event_id(ce: CloudEvent) -> bool:
        cloud_event_id = UCloudEvent.extract_string_value_from_attributes("id", ce)
        uuid = UUIDUtils.fromString(cloud_event_id)

        return uuid is not None and UUIDUtils.isuuid(uuid)

    @staticmethod
    def get_payload(ce: CloudEvent) -> any_pb2.Any:
        data = ce.get_data()
        if data is None:
            return any_pb2.Any()
        try:
            return any_pb2.Any().FromString(data)
        except DecodeError:
            return any_pb2.Any()

    @staticmethod
    def unpack(ce: CloudEvent, clazz):
        try:
            return UCloudEvent.get_payload(ce).Unpack(clazz)
        except DecodeError:
            return None

    @staticmethod
    def to_string(ce: CloudEvent) -> str:
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
        return ce.get_attributes().get(attr_name)

    @staticmethod
    def extract_integer_value_from_attributes(attr_name, ce: CloudEvent) -> int:
        value = UCloudEvent.extract_string_value_from_attributes(attr_name, ce)
        return int(value) if value is not None else None
