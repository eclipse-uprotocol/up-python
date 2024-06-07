"""
SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to the
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

from typing import Optional

from google.protobuf.descriptor import ServiceDescriptor
from google.protobuf.descriptor_pb2 import ServiceOptions

from uprotocol.proto.uprotocol.v1.uri_pb2 import UUri
from uprotocol.proto.uprotocol.uoptions_pb2 import (
    service_version_major as Version_Major,
    service_id as Service_Id,
)


class UriFactory:
    """
    URI Factory that builds URIs from protos
    """

    @staticmethod
    def from_proto(
        service_descriptor: Optional[ServiceDescriptor], resource_id: int, authority_name: Optional[str]
    ) -> UUri:
        """
        Builds a URI for an protobuf generated code Service Descriptor.
        @param resourceId The resource id.
        @param authorityName The authority name.
        @return Returns a URI for an protobuf generated code
        Service Descriptor.
        """
        if service_descriptor is None:
            return UUri()

        options: ServiceOptions = service_descriptor.GetOptions()

        version_major: int = options.Extensions[Version_Major]
        service_id: int = options.Extensions[Service_Id]

        uuri = UUri()
        if version_major is not None:
            uuri.ue_version_major = version_major
        if resource_id is not None:
            uuri.resource_id = resource_id
        if service_id is not None:
            uuri.ue_id = service_id
        if authority_name is not None:
            uuri.authority_name = authority_name

        return uuri

    @staticmethod
    def any_func() -> UUri:
        """
        Returns a URI with all fields set to 0.
        @return Returns a URI with all fields set to 0.
        """
        return UUri(
            authority_name="*",
            ue_id=0xFFFF,
            ue_version_major=0xFF,
            resource_id=0xFFFF,
        )
