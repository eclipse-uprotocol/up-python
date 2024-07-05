"""
SPDX-FileCopyrightText: 2023 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import re
from typing import Optional

from uprotocol.uri.factory.uri_factory import UriFactory
from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.v1.uri_pb2 import UUri


class UriSerializer:
    """
    UUris are used in transport layers and hence need to be serialized.<br>
    Each transport supports different
    serialization formats.
    """

    @staticmethod
    def serialize(uri: Optional[UUri]) -> str:
        """
        Support for serializing UUri objects into their String format.
        @param uri: UUri object to be serialized to the String format.
        @return:Returns the String format of the supplied UUri that can be
        used as a sink or a source in a
        uProtocol publish communication.
        """
        if uri is None or UriValidator.is_empty(uri):
            return ""

        sb = []

        if uri.authority_name.strip() != "":
            sb.append("//")
            sb.append(uri.authority_name)

        sb.append("/")
        sb.append(hex(uri.ue_id)[2:].upper())
        sb.append("/")
        sb.append(hex(uri.ue_version_major)[2:].upper())
        sb.append("/")
        sb.append(hex(uri.resource_id)[2:].upper())
        return re.sub("/+$", "", "".join(sb))

    @staticmethod
    def _build_local_uri(uri_parts, number_of_parts_in_uri):
        ue_version = None
        ur_id = None
        ue_id = int(uri_parts[1], 16)
        if number_of_parts_in_uri > 2:
            ue_version = int(uri_parts[2], 16)
            if number_of_parts_in_uri > 3:
                ur_id = int(uri_parts[3], 16)

        return ue_id, ue_version, ur_id

    @staticmethod
    def _build_remote_uri(uri_parts, number_of_parts_in_uri):
        ue_id = None
        ue_version = None
        ur_id = None
        auth_name = uri_parts[2]
        if len(uri_parts) > 3:
            ue_id = int(uri_parts[3], 16)
            if number_of_parts_in_uri > 4:
                ue_version = int(uri_parts[4], 16)
                if number_of_parts_in_uri > 5:
                    ur_id = int(uri_parts[5], 16)

        return auth_name, ue_id, ue_version, ur_id

    @staticmethod
    def _build_uri(is_local, uri_parts, number_of_parts_in_uri):
        auth_name = None

        if is_local:
            ue_id, ue_version, ur_id = UriSerializer._build_local_uri(uri_parts, number_of_parts_in_uri)
        else:
            if uri_parts[2].strip() == "":
                return UUri()
            auth_name, ue_id, ue_version, ur_id = UriSerializer._build_remote_uri(uri_parts, number_of_parts_in_uri)

        return UUri(
            authority_name=auth_name,
            ue_id=ue_id,
            ue_version_major=ue_version,
            resource_id=ur_id,
        )

    @staticmethod
    def deserialize(uri: Optional[str]) -> UUri:
        """
        Deserialize from the format to a UUri.
        @param uri:serialized UUri.
        @return:Returns a UUri object from the serialized format from the wire.
        """
        if uri is None or uri.strip() == "":
            return UUri()
        uri = uri[uri.index(":") + 1 :] if ":" in uri else uri.replace("\\", "/")

        is_local = not uri.startswith("//")
        uri_parts = uri.split("/")
        number_of_parts_in_uri = len(uri_parts)

        if number_of_parts_in_uri in [0, 1]:
            return UUri()

        try:
            new_uri = UriSerializer._build_uri(is_local, uri_parts, number_of_parts_in_uri)

        except ValueError:
            return UUri()

        # Ensure that the major version is less than the wildcard
        if new_uri.ue_version_major > UriFactory.WILDCARD_ENTITY_VERSION:
            return UUri()

        # Ensure that the resource id is less than the wildcard
        if new_uri.resource_id > UriFactory.WILDCARD_ENTITY_ID:
            return UUri()

        return new_uri
