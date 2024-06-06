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

from google.protobuf.descriptor import ServiceDescriptor
from google.protobuf.descriptor_pb2 import ServiceOptions

from uprotocol.proto.uprotocol_options_pb2 import (
    id,
    name,
    version_major,
    version_minor,
)
from uprotocol.proto.uri_pb2 import UEntity


class UEntityFactory:
    """
    Factory for creating UEntity objects.
    """

    @staticmethod
    def from_proto(service_descriptor: ServiceDescriptor):
        if service_descriptor is None:
            return UEntity()

        options: ServiceOptions = service_descriptor.GetOptions()

        name_ext: str = options.Extensions[name]
        v_major: int = options.Extensions[version_major]
        v_minor: int = options.Extensions[version_minor]
        id_ext: int = options.Extensions[id]

        uentity = UEntity()
        if name_ext is not None:
            uentity.name = name_ext
        if v_major is not None:
            uentity.version_major = v_major
        if v_minor is not None:
            uentity.version_minor = v_minor
        if id_ext is not None:
            uentity.id = id_ext

        return uentity
