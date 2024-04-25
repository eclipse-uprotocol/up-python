import socket
import unittest

from uprotocol.proto.uri_pb2 import UEntity, UUri, UAuthority, UResource
from uprotocol.uri.factory.uresource_builder import UResourceBuilder
from uprotocol.uri.serializer.microuriserializer import MicroUriSerializer
from uprotocol.uri.validator.urivalidator import UriValidator


class TestMicroUriSerializer(unittest.TestCase):

    def test_empty(self):
        bytes_uuri = MicroUriSerializer().serialize(UUri())
        self.assertEqual(len(bytes_uuri), 0)
        uri2 = MicroUriSerializer().deserialize(bytes_uuri)
        self.assertTrue(UriValidator.is_empty(uri2))

    def test_null(self):
        bytes_uuri = MicroUriSerializer().serialize(None)
        self.assertEqual(len(bytes_uuri), 0)
        uri2 = MicroUriSerializer().deserialize(None)
        self.assertTrue(UriValidator.is_empty(uri2))

    def test_serialize_uri(self):
        uri = UUri(
            entity=UEntity(id=29999, version_major=254),
            resource=UResourceBuilder.from_id(19999),
        )
        bytes_uuri = MicroUriSerializer().serialize(uri)
        uri2 = MicroUriSerializer().deserialize(bytes_uuri)
        self.assertTrue(UriValidator.is_micro_form(uri))
        self.assertTrue(len(bytes_uuri) > 0)
        self.assertEqual(uri, uri2)

    def test_serialize_remote_uri_without_address(self):
        uri = UUri(
            authority=UAuthority(name="vcu.vin"),
            entity=UEntity(id=29999, version_major=254),
            resource=UResourceBuilder.for_rpc_response(),
        )
        bytes_uuri = MicroUriSerializer().serialize(uri)
        self.assertTrue(len(bytes_uuri) == 0)

    def test_serialize_uri_missing_ids(self):
        uri = UUri(
            entity=UEntity(name="hartley"),
            resource=UResourceBuilder.for_rpc_response(),
        )
        bytes_uuri = MicroUriSerializer().serialize(uri)
        self.assertTrue(len(bytes_uuri) == 0)

    def test_serialize_uri_missing_resource_id(self):
        uri = UUri(entity=UEntity(name="hartley"))
        bytes_uuri = MicroUriSerializer().serialize(uri)
        self.assertTrue(len(bytes_uuri) == 0)

    def test_deserialize_bad_microuri_length(self):
        badMicroUUri = bytes([0x1, 0x0, 0x0, 0x0, 0x0])
        uuri = MicroUriSerializer().deserialize(badMicroUUri)
        self.assertTrue(UriValidator.is_empty(uuri))

        badMicroUUri = bytes(
            [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
        )
        uuri = MicroUriSerializer().deserialize(badMicroUUri)
        self.assertTrue(UriValidator.is_empty(uuri))

    def test_deserialize_bad_microuri_not_version_1(self):
        badMicroUUri = bytes(
            [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
        )
        uuri = MicroUriSerializer().deserialize(badMicroUUri)
        self.assertTrue(UriValidator.is_empty(uuri))

    def test_deserialize_bad_microuri_not_valid_address_type(self):
        badMicroUUri = bytes(
            [0x1, 0x5, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
        )
        uuri = MicroUriSerializer().deserialize(badMicroUUri)
        self.assertTrue(UriValidator.is_empty(uuri))

    def test_deserialize_bad_microuri_valid_address_type_invalid_length(self):
        badMicroUUri = bytes(
            [0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
        )
        uuri = MicroUriSerializer().deserialize(badMicroUUri)
        self.assertTrue(UriValidator.is_empty(uuri))

        badMicroUUri = bytes(
            [0x1, 0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
        )
        uuri = MicroUriSerializer().deserialize(badMicroUUri)
        self.assertTrue(UriValidator.is_empty(uuri))

        badMicroUUri = bytes(
            [0x1, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
        )
        uuri = MicroUriSerializer().deserialize(badMicroUUri)
        self.assertTrue(UriValidator.is_empty(uuri))

    def test_serialize_good_ipv4_based_authority(self):
        uri = UUri(
            authority=UAuthority(
                ip=socket.inet_pton(socket.AF_INET, "10.0.3.3")
            ),
            entity=UEntity(id=29999, version_major=254),
            resource=UResourceBuilder.for_rpc_request(99),
        )
        bytes_uuri = MicroUriSerializer().serialize(uri)
        uri2 = MicroUriSerializer().deserialize(bytes_uuri)
        self.assertTrue(len(bytes_uuri) > 0)
        self.assertTrue(UriValidator.is_micro_form(uri))
        self.assertTrue(UriValidator.is_micro_form(uri2))
        self.assertEqual(str(uri), str(uri2))
        self.assertTrue(uri == uri2)

    def test_serialize_bad_authority(self):
        uri = UUri(
            authority=UAuthority(ip=b"123456789"),
            entity=UEntity(id=29999, version_major=254),
            resource=UResourceBuilder.for_rpc_request(99),
        )
        bytes_uuri = MicroUriSerializer().serialize(uri)
        self.assertEqual(bytes_uuri, bytearray())

    def test_serialize_good_ipv6_based_authority(self):
        uri = UUri(
            authority=UAuthority(
                ip=socket.inet_pton(
                    socket.AF_INET6, "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
                )
            ),
            entity=UEntity(id=29999, version_major=254),
            resource=UResource(id=19999, name="rpc"),
        )
        bytes_uuri = MicroUriSerializer().serialize(uri)
        uri2 = MicroUriSerializer().deserialize(bytes_uuri)
        self.assertTrue(UriValidator.is_micro_form(uri))
        self.assertTrue(len(bytes_uuri) > 0)
        self.assertTrue(uri == uri2)

    def test_serialize_id_based_authority(self):
        size = 13
        byteArray = bytearray(i for i in range(size))
        uri = UUri(
            authority=UAuthority(id=bytes(byteArray)),
            entity=UEntity(id=29999, version_major=254),
            resource=UResource(id=19999, name="rpc"),
        )
        bytes_uuri = MicroUriSerializer().serialize(uri)
        uri2 = MicroUriSerializer().deserialize(bytes_uuri)
        self.assertTrue(UriValidator.is_micro_form(uri))
        self.assertTrue(len(bytes_uuri) > 0)
        self.assertTrue(uri == uri2)

    def test_serialize_bad_length_ip_based_authority(self):
        byteArray = bytes([127, 1, 23, 123, 12, 6])
        uri = UUri(
            authority=UAuthority(ip=byteArray),
            entity=UEntity(id=29999, version_major=254),
            resource=UResource(id=19999),
        )
        bytes_uuri = MicroUriSerializer().serialize(uri)
        self.assertTrue(len(bytes_uuri) == 0)

    def test_serialize_id_size_255_based_authority(self):
        size = 129
        byteArray = bytes(i for i in range(size))
        uri = UUri(
            authority=UAuthority(id=byteArray),
            entity=UEntity(id=29999, version_major=254),
            resource=UResourceBuilder.for_rpc_request(99),
        )
        bytes_uuri = MicroUriSerializer().serialize(uri)
        self.assertEqual(len(bytes_uuri), 9 + size)
        uri2 = MicroUriSerializer().deserialize(bytes_uuri)
        self.assertTrue(UriValidator.is_micro_form(uri))
        self.assertTrue(uri == uri2)

    def test_serialize_id_out_of_range_2(self):
        byteArray = bytearray(258)
        for i in range(256):
            byteArray[i] = i
        byteArray = bytes(byteArray)
        uri = UUri(
            authority=UAuthority(id=byteArray),
            entity=UEntity(id=29999, version_major=254),
            resource=UResourceBuilder.from_id(19999),
        )
        bytes_uuri = MicroUriSerializer().serialize(uri)
        self.assertEqual(len(bytes_uuri), 0)

    def test_serialize_resource_id_out_of_range(self):
        size = 129
        byteArray = bytes(i for i in range(size))
        uri = UUri(
            authority=UAuthority(id=byteArray),
            entity=UEntity(id=29999, version_major=254),
            resource=UResourceBuilder.from_id(65536),
        )
        bytes_uuri = MicroUriSerializer().serialize(uri)
        self.assertEqual(len(bytes_uuri), 0)

    def test_serialize_entity_id_out_of_range(self):
        size = 129
        byteArray = bytes(i for i in range(size))
        uri = UUri(
            authority=UAuthority(id=byteArray),
            entity=UEntity(id=65536, version_major=254),
            resource=UResourceBuilder.from_id(19999),
        )
        bytes_uuri = MicroUriSerializer().serialize(uri)
        self.assertEqual(len(bytes_uuri), 0)

    def test_serialize_authority_ip_invalid(self):
        uri = UUri(
            authority=UAuthority(ip=b"123456789"),
            entity=UEntity(id=29999, version_major=254),
            resource=UResourceBuilder.from_id(19999),
        )
        bytes_uuri = MicroUriSerializer().serialize(uri)
        self.assertEqual(len(bytes_uuri), 0)


if __name__ == "__main__":
    unittest.main()
