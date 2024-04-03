import unittest
from uprotocol.uri.serializer.shorturiserializer import ShortUriSerializer
from uprotocol.uri.factory.uresource_builder import UResourceBuilder
from uprotocol.proto.uri_pb2 import UAuthority, UEntity, UResource, UUri
from socket import inet_aton


class ShortUriSerializerTest(unittest.TestCase):

    def test_serialize_with_null_uri(self):
        str_uri = ShortUriSerializer().serialize(None)
        self.assertEqual("", str_uri)

    def test_serialize_with_empty_uri(self):
        str_uri = ShortUriSerializer().serialize(UUri())
        self.assertEqual("", str_uri)

    def test_creating_short_uri_serializer(self):
        uri = UUri(
            entity=UEntity(id=1, version_major=1),
            resource=UResourceBuilder.for_rpc_response(),
        )
        str_uri = ShortUriSerializer().serialize(uri)
        self.assertEqual("/1/1/0", str_uri)
        uri2 = ShortUriSerializer().deserialize(str_uri)
        self.assertEqual(uri, uri2)

    def test_creating_short_uri_serializer_with_method(self):
        uri = UUri(
            entity=UEntity(id=1, version_major=1),
            resource=UResourceBuilder.for_rpc_request(10),
        )
        str_uri = ShortUriSerializer().serialize(uri)
        self.assertEqual("/1/1/10", str_uri)
        uri2 = ShortUriSerializer().deserialize(str_uri)
        self.assertEqual(uri, uri2)

    def test_creating_short_uri_serializer_with_topic(self):
        uri = UUri(
            entity=UEntity(id=1, version_major=1),
            resource=UResourceBuilder.from_id(20000),
        )
        str_uri = ShortUriSerializer().serialize(uri)
        self.assertEqual("/1/1/20000", str_uri)
        uri2 = ShortUriSerializer().deserialize(str_uri)
        self.assertEqual(uri, uri2)

    def test_creating_short_uri_serializer_with_authority(self):
        uri = UUri(
            entity=UEntity(id=1, version_major=1),
            authority=UAuthority(id=b"19UYA31581L000000"),
            resource=UResourceBuilder.from_id(20000),
        )
        str_uri = ShortUriSerializer().serialize(uri)
        self.assertEqual("//19UYA31581L000000/1/1/20000", str_uri)
        uri2 = ShortUriSerializer().deserialize(str_uri)
        self.assertEqual(uri, uri2)

    def test_creating_short_uri_serializer_with_ip_authority(self):
        ip_bytes = inet_aton("192.168.1.100")
        uri = UUri(
            entity=UEntity(id=1, version_major=1),
            authority=UAuthority(ip=ip_bytes),
            resource=UResourceBuilder.from_id(20000),
        )
        str_uri = ShortUriSerializer().serialize(uri)
        self.assertEqual("//192.168.1.100/1/1/20000", str_uri)
        uri2 = ShortUriSerializer().deserialize(str_uri)
        self.assertEqual(uri, uri2)

    def test_short_serializing_uri_without_resource(self):
        uri = UUri(entity=UEntity(id=1, version_major=1))
        str_uri = ShortUriSerializer().serialize(uri)
        self.assertEqual(str_uri, "/1/1")

    def test_short_serializing_uri_with_negative_version_major(self):
        with self.assertRaises(ValueError) as context:
            UUri(
                entity=UEntity(id=1, version_major=-1),
                resource=UResourceBuilder.from_id(20000),
            )
        self.assertTrue("Value out of range: -1" in str(context.exception))

    def test_short_deserialize_null_uri(self):
        uri = ShortUriSerializer().deserialize(None)
        self.assertEqual(uri, UUri())

    def test_short_deserialize_empty_uri(self):
        uri = ShortUriSerializer().deserialize("")
        self.assertEqual(uri, UUri())

    def test_short_deserialize_uri_with_scheme_and_authority(self):
        uri = ShortUriSerializer().deserialize("up://mypc/1/1/1")
        self.assertTrue(uri.authority is not None)
        self.assertEqual(uri.authority.id, b"mypc")
        self.assertFalse(uri.authority.HasField("name"))
        self.assertFalse(uri.authority.HasField("ip"))
        self.assertTrue(uri.HasField("entity"))
        self.assertEqual(uri.entity.id, 1)
        self.assertEqual(uri.entity.version_major, 1)
        self.assertTrue(uri.HasField("resource"))
        self.assertEqual(uri.resource.id, 1)

    def test_short_deserialize_uri_without_scheme(self):
        uri = ShortUriSerializer().deserialize("//mypc/1/1/1")
        self.assertTrue(uri.HasField("authority"))
        self.assertEqual(uri.authority.id, bytes("mypc", "utf-8"))
        self.assertFalse(uri.authority.HasField("name"))
        self.assertFalse(uri.authority.HasField("ip"))
        self.assertTrue(uri.HasField("entity"))
        self.assertEqual(uri.entity.id, 1)
        self.assertEqual(uri.entity.version_major, 1)
        self.assertTrue(uri.HasField("resource"))
        self.assertEqual(uri.resource.id, 1)

    def test_short_deserialize_uri_with_only_authority(self):
        uri = ShortUriSerializer().deserialize("//")
        self.assertEqual(uri, UUri())

    def test_short_deserialize_uri_with_scheme_and_only_authority(self):
        uri = ShortUriSerializer().deserialize("up://")
        self.assertEqual(uri, UUri())

    def test_short_serialize_with_invalid_ip_address(self):
        uri = UUri(
            entity=UEntity(id=1, version_major=1),
            authority=UAuthority(ip=b"34823748273"),
        )
        uri_string = ShortUriSerializer().serialize(uri)
        self.assertEqual(uri_string, "")

    def test_short_serialize_with_authority_only_name(self):
        uri = UUri(
            entity=UEntity(id=1, version_major=1),
            authority=UAuthority(name="mypc"),
        )
        uri_string = ShortUriSerializer().serialize(uri)
        self.assertEqual(uri_string, "")

    def test_short_deserialize_local_uri_with_too_many_parts(self):
        uri = ShortUriSerializer().deserialize("/1/1/1/1")
        self.assertEqual(uri, UUri())

    def test_short_deserialize_local_uri_with_only_two_parts(self):
        uri = ShortUriSerializer().deserialize("/1/1")
        self.assertTrue(uri.HasField("entity"))
        self.assertEqual(uri.entity.id, 1)
        self.assertEqual(uri.entity.version_major, 1)

    def test_short_deserialize_local_uri_with_three_parts(self):
        uri = ShortUriSerializer().deserialize("/1")
        self.assertTrue(uri.HasField("entity"))
        self.assertEqual(uri.entity.id, 1)
        self.assertFalse(uri.HasField("resource"))

    def test_short_deserialize_with_blank_authority(self):
        uri = ShortUriSerializer().deserialize("///1/1/1")
        self.assertEqual(uri, UUri())

    def test_short_deserialize_with_remote_authority_ip_and_too_many_parts(
        self,
    ):
        uri = ShortUriSerializer().deserialize("//192.168.1.100/1/1/1/1")
        self.assertEqual(uri, UUri())

    def test_short_deserialize_with_remote_authority_ip_and_right_number_of_parts(
        self,
    ):
        uri = ShortUriSerializer().deserialize("//192.168.1.100/1/1/1")
        self.assertTrue(uri.authority is not None)
        self.assertTrue(uri.authority.HasField("ip"))
        self.assertEqual(uri.authority.ip, inet_aton("192.168.1.100"))
        self.assertTrue(uri.entity is not None)
        self.assertEqual(uri.entity.id, 1)
        self.assertEqual(uri.entity.version_major, 1)
        self.assertTrue(uri.resource is not None)
        self.assertEqual(uri.resource.id, 1)

    def test_short_deserialize_with_remote_authority_ip_address_missing_resource(
        self,
    ):
        uri = ShortUriSerializer().deserialize("//192.168.1.100/1/1")
        self.assertTrue(uri.HasField("authority"))
        self.assertTrue(uri.authority.HasField("ip"))
        self.assertEqual(uri.authority.ip, inet_aton("192.168.1.100"))
        self.assertTrue(uri.HasField("entity"))
        self.assertEqual(uri.entity.id, 1)
        self.assertEqual(uri.entity.version_major, 1)
        self.assertFalse(uri.HasField("resource"))

    def test_short_deserialize_with_remote_authority_ip_address_missing_resource_and_version_major(
        self,
    ):
        uri = ShortUriSerializer().deserialize("//192.168.1.100/1")
        self.assertTrue(uri.HasField("authority"))
        self.assertTrue(uri.authority.HasField("ip"))
        self.assertEqual(uri.authority.ip, inet_aton("192.168.1.100"))
        self.assertTrue(uri.HasField("entity"))
        self.assertEqual(uri.entity.id, 1)
        self.assertFalse(uri.entity.HasField("version_major"))

    def test_short_deserialize_with_remote_authority_ip_address_missing_resource_and_version_major_and_ueid(
        self,
    ):
        uri = ShortUriSerializer().deserialize("//192.168.1.100//")
        self.assertTrue(uri.HasField("authority"))
        self.assertTrue(uri.authority.HasField("ip"))
        self.assertEqual(uri.authority.ip, inet_aton("192.168.1.100"))
        self.assertFalse(uri.HasField("entity"))

    def test_short_deserialize_with_remote_authority_and_blank_ueversion_and_ueid(
        self,
    ):
        uri = ShortUriSerializer().deserialize("//mypc//1/")
        self.assertTrue(uri.HasField("authority"))
        self.assertTrue(uri.authority.HasField("id"))
        self.assertEqual(uri.authority.id, b"mypc")
        self.assertTrue(uri.HasField("entity"))

    def test_short_deserialize_with_remote_authority_and_missing_parts(self):
        uri = ShortUriSerializer().deserialize("//mypc")
        self.assertTrue(uri.HasField("authority"))
        self.assertTrue(uri.authority.HasField("id"))
        self.assertEqual(uri.authority.id, b"mypc")

    def test_short_deserialize_with_remote_authority_and_invalid_characters_for_entity_id_and_version(
        self,
    ):
        uri = ShortUriSerializer().deserialize("//mypc/abc/def")
        self.assertEqual(uri, UUri())

    def test_short_deserialize_with_remote_authority_and_invalid_characters_for_resource_id(
        self,
    ):
        uri = ShortUriSerializer().deserialize("//mypc/1/1/abc")
        self.assertEqual(uri.resource, UResource())


if __name__ == "__main__":
    unittest.main()
