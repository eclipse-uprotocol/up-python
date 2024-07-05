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

from uprotocol.uri.factory.uri_factory import UriFactory
from uprotocol.v1.uri_pb2 import UUri


class UriValidator:
    """
    Class for validating Uris.
    """

    RESOURCE_ID_RESPONSE = 0
    RESOURCE_ID_MIN_EVENT = 0x8000  # The minimum event id for a URI.

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
        Returns true if URI is of type RPC. A UUri is of type RPC if its
        resource id is less than RESOURCE_ID_MIN_EVENT and greater than RESOURCE_ID_RESPONSE.
        @param uri: UUri to check if it is of type RPC
        @return: Returns true if this resource specifies an RPC method
        call.
        """
        return (
            uri is not None and UriValidator.RESOURCE_ID_RESPONSE < uri.resource_id < UriValidator.RESOURCE_ID_MIN_EVENT
        )

    @staticmethod
    def is_rpc_response(uri: UUri) -> bool:
        """
        @return Returns true if URI is of type RPC response.
        """
        return UriValidator.is_default_resource_id(uri)

    @staticmethod
    def is_notification_destination(uri: UUri) -> bool:
        """
        @return Returns true if URI is of type RPC response.
        """
        return UriValidator.is_default_resource_id(uri)

    @staticmethod
    def is_default_resource_id(uri: UUri) -> bool:
        """
        Returns true if URI is of type RPC response.
        """
        return not UriValidator.is_empty(uri) and uri.resource_id == UriValidator.RESOURCE_ID_RESPONSE

    @staticmethod
    def is_topic(uri: UUri) -> bool:
        """
        Returns true if URI is of type Topic used for publish and notifications.

        @param uri {@link UUri} to check if it is of type Topic
        @return Returns true if URI is of type Topic.
        """
        return not UriValidator.is_empty(uri) and uri.resource_id >= UriValidator.RESOURCE_ID_MIN_EVENT

    @staticmethod
    def matches_authority(uri_to_match: UUri, candidate_uri: UUri) -> bool:
        """
        Checks if the authority of the uri_to_match matches the candidate_uri.
        A match occurs if the authority name in uri_to_match is a wildcard
        or if both URIs have the same authority name.

        :param uri_to_match: The URI to match.
        :param candidate_uri: The candidate URI to match against.
        :return: True if the authority names match, False otherwise.
        """
        return (
            uri_to_match.authority_name == UriFactory.WILDCARD_AUTHORITY
            or uri_to_match.authority_name == candidate_uri.authority_name
        )

    @staticmethod
    def matches_entity_id(uri_to_match: UUri, candidate_uri: UUri) -> bool:
        """
        Checks if the entity ID of the uri_to_match matches the candidate_uri.
        A match occurs if the entity ID in uri_to_match is a wildcard (0xFFFF)
        or if the masked entity IDs of both URIs are equal.

        The entity ID masking is performed using a bitwise AND operation with
        0xFFFF. If the result of the bitwise AND operation between the
        uri_to_match's entity ID and 0xFFFF is 0xFFFF, it indicates that the
        uri_to_match's entity ID is a wildcard and can match any entity ID.
        Otherwise, the function checks if the masked entity IDs of both URIs
        are equal, meaning that the relevant parts of their entity IDs match.

        :param uri_to_match: The URI to match.
        :param candidate_uri: The candidate URI to match against.
        :return: True if the entity IDs match, False otherwise.
        """
        return (uri_to_match.ue_id & UriFactory.WILDCARD_ENTITY_ID) == UriFactory.WILDCARD_ENTITY_ID or (
            uri_to_match.ue_id & UriFactory.WILDCARD_ENTITY_ID
        ) == (candidate_uri.ue_id & UriFactory.WILDCARD_ENTITY_ID)

    @staticmethod
    def matches_entity_instance(uri_to_match: UUri, candidate_uri: UUri) -> bool:
        """
        Checks if the entity instance of the uri_to_match matches the candidate_uri.
        A match occurs if the upper 16 bits of the entity ID in uri_to_match are zero
        or if the upper 16 bits of the entity IDs of both URIs are equal.

        :param uri_to_match: The URI to match.
        :param candidate_uri: The candidate URI to match against.
        :return: True if the entity instances match, False otherwise.
        """
        return (uri_to_match.ue_id & 0xFFFF_0000) == 0x0000_0000 or (uri_to_match.ue_id & 0xFFFF_0000) == (
            candidate_uri.ue_id & 0xFFFF_0000
        )

    @staticmethod
    def matches_entity_version(uri_to_match: UUri, candidate_uri: UUri) -> bool:
        """
        Checks if the entity version of the uri_to_match matches the candidate_uri.
        A match occurs if the entity version in uri_to_match is a wildcard
        or if both URIs have the same entity version.

        :param uri_to_match: The URI to match.
        :param candidate_uri: The candidate URI to match against.
        :return: True if the entity versions match, False otherwise.
        """
        return (
            uri_to_match.ue_version_major == UriFactory.WILDCARD_ENTITY_VERSION
            or uri_to_match.ue_version_major == candidate_uri.ue_version_major
        )

    @staticmethod
    def matches_entity(uri_to_match: UUri, candidate_uri: UUri) -> bool:
        """
        Checks if the entity of the uri_to_match matches the candidate_uri.
        A match occurs if the entity ID, entity instance, and entity version
        of both URIs match according to their respective rules.

        :param uri_to_match: The URI to match.
        :param candidate_uri: The candidate URI to match against.
        :return: True if the entities match, False otherwise.
        """
        return (
            UriValidator.matches_entity_id(uri_to_match, candidate_uri)
            and UriValidator.matches_entity_instance(uri_to_match, candidate_uri)
            and UriValidator.matches_entity_version(uri_to_match, candidate_uri)
        )

    @staticmethod
    def matches_resource(uri_to_match: UUri, candidate_uri: UUri) -> bool:
        """
        Checks if the resource of the uri_to_match matches the candidate_uri.
        A match occurs if the resource ID in uri_to_match is a wildcard
        or if both URIs have the same resource ID.

        :param uri_to_match: The URI to match.
        :param candidate_uri: The candidate URI to match against.
        :return: True if the resource IDs match, False otherwise.
        """
        return (
            uri_to_match.resource_id == UriFactory.WILDCARD_RESOURCE_ID
            or uri_to_match.resource_id == candidate_uri.resource_id
        )

    @staticmethod
    def matches(uri_to_match: UUri, candidate_uri: UUri) -> bool:
        """
        Checks if the entire URI (authority, entity, and resource) of the uri_to_match
        matches the candidate_uri. A match occurs if the authority, entity, and resource
        of both URIs match according to their respective rules.

        :param uri_to_match: The URI to match.
        :param candidate_uri: The candidate URI to match against.
        :return: True if the entire URIs match, False otherwise.
        """
        return (
            UriValidator.matches_authority(uri_to_match, candidate_uri)
            and UriValidator.matches_entity(uri_to_match, candidate_uri)
            and UriValidator.matches_resource(uri_to_match, candidate_uri)
        )
