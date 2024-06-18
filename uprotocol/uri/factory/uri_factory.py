"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

from google.protobuf.descriptor import ServiceDescriptor
from google.protobuf.descriptor_pb2 import ServiceOptions

from uprotocol.uoptions_pb2 import service_id, service_version_major
from uprotocol.v1.uri_pb2 import UUri


class UriFactory:
    """
    URI Factory that builds URIs from protos
    """

    @staticmethod
    def from_proto(
        service_descriptor: Optional[ServiceDescriptor], resource_id: int, authority_name: Optional[str]
    ) -> UUri:
        """
        Builds a URI for a protobuf generated code Service Descriptor.
        @param service_descriptor TThe protobuf generated code Service Descriptor.
        @param resource_id The resource id.
        @param authority_name The authority name.
        @return Returns a URI for a protobuf generated code

        Service Descriptor.
        """
        if service_descriptor is None:
            return UUri()

        options: ServiceOptions = service_descriptor.GetOptions()

        version_major: int = options.Extensions[service_version_major]
        id_val: int = options.Extensions[service_id]


        uuri = UUri()
        if version_major is not None:
            uuri.ue_version_major = version_major
        if resource_id is not None:
            uuri.resource_id = resource_id
        if id_val is not None:
            uuri.ue_id = id_val

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
