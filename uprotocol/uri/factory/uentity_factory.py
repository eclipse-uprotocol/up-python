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

from uprotocol.proto.uri_pb2 import UEntity
from uprotocol.proto.uprotocol_options_pb2 import name as Name
from uprotocol.proto.uprotocol_options_pb2 import (
    version_major as Version_Major,
)
from uprotocol.proto.uprotocol_options_pb2 import (
    version_minor as Version_Minor,
)
from uprotocol.proto.uprotocol_options_pb2 import id as Id


class UEntityFactory:
    """
    Factory for creating UEntity objects.
    """

    @staticmethod
    def from_proto(service_descriptor: ServiceDescriptor):
        if service_descriptor is None:
            return UEntity()

        options: ServiceOptions = service_descriptor.GetOptions()

        name: str = options.Extensions[Name]
        version_major: int = options.Extensions[Version_Major]
        version_minor: int = options.Extensions[Version_Minor]
        id: int = options.Extensions[Id]

        uentity = UEntity()
        if name is not None:
            uentity.name = name
        if version_major is not None:
            uentity.version_major = version_major
        if version_minor is not None:
            uentity.version_minor = version_minor
        if id is not None:
            uentity.id = id

        return uentity
