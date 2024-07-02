"""
SPDX-FileCopyrightText: 2023 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

from uprotocol.v1.uri_pb2 import UUri


class UriValidator:
    """
    Class for validating Uris.
    """

    # The minimum publish/notification topic id for a URI.
    MIN_TOPIC_ID = 0x8000

    # The Default resource id.
    DEFAULT_RESOURCE_ID = 0

    # The major version wildcard.
    MAJOR_VERSION_WILDCARD = 0xFF

    @staticmethod
    def is_empty(uri: UUri) -> bool:
        """
        Indicates that this  URI is an empty as it does not contain
        authority, entity, and resource.
        @param uri UUri to check if it is empty
        @return Returns true if this  URI is an empty container and has
        no valuable information in building uProtocol sinks or sources.
        """
        return uri is None or uri == UUri()

    @staticmethod
    def is_rpc_method(uri: Optional[UUri]) -> bool:
        """
        Returns true if URI is of type RPC. A UUri is of type RPC if it
        contains the word rpc in the resource name
        and has an instance name and/or the id is less than MIN_TOPIC_ID.
        @param uri: UUri to check if it is of type RPC
        @return: Returns true if this resource specifies an RPC method
        call or RPC response.
        """
        return (
            uri is not None
            and uri.resource_id != UriValidator.DEFAULT_RESOURCE_ID
            and uri.resource_id < UriValidator.MIN_TOPIC_ID
        )

    @staticmethod
    def is_rpc_response(uri: UUri) -> bool:
        """
        @return Returns true if URI is of type RPC response.
        """
        return UriValidator.is_default_resource_id(uri)

    @staticmethod
    def is_default_resource_id(uri: UUri) -> bool:
        """
        Returns true if URI is of type RPC response.
        """
        return not UriValidator.is_empty(uri) and uri.resource_id == UriValidator.DEFAULT_RESOURCE_ID

    @staticmethod
    def is_topic(uri: UUri) -> bool:
        """
        Returns true if URI is of type Topic used for publish and notifications.

        @param uri {@link UUri} to check if it is of type Topic
        @return Returns true if URI is of type Topic.
        """
        return not UriValidator.is_empty(uri) and uri.resource_id >= UriValidator.MIN_TOPIC_ID
