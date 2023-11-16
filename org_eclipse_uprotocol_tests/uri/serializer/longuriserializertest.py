import unittest

from org_eclipse_uprotocol.uri.builder.uresource_builder import UResourceBuilder
from org_eclipse_uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from org_eclipse_uprotocol.proto.uri_pb2 import UEntity, UUri, UAuthority, UResource
from org_eclipse_uprotocol.uri.validator.urivalidator import UriValidator


class LongUriSerializerTest(unittest.TestCase):

    def test_using_the_serializers(self):
        uri = UUri(entity=UEntity(name="hartley"), resource=UResourceBuilder.for_rpc_request("raise"))

        str_uri = LongUriSerializer().serialize(uri)
        self.assertEqual("/hartley//rpc.raise", str_uri)
        uri2 = LongUriSerializer().deserialize(str_uri)
        self.assertEqual(uri, uri2)

    def test_parse_protocol_uri_when_is_null(self):
        uri = LongUriSerializer().deserialize(None)
        self.assertTrue(UriValidator.is_empty(uri))
        self.assertFalse(UriValidator.is_resolved(uri))
        self.assertFalse(UriValidator.is_long_form(uri))

    def test_parse_protocol_uri_when_is_empty_string(self):
        uri = ''
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_empty(uuri))
        uri2 = LongUriSerializer().serialize(None)
        self.assertTrue(len(uri2) == 0)

    def test_parse_protocol_uri_with_schema_and_slash(self):
        uri = "/"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(uuri.HasField('authority'))
        self.assertTrue(UriValidator.is_empty(uuri))
        self.assertFalse(uuri.HasField('resource'))
        self.assertFalse(uuri.HasField('entity'))
        uri2 = LongUriSerializer().serialize(UUri())
        self.assertTrue(len(uri2) == 0)

    def test_parse_protocol_uri_with_schema_and_double_slash(self):
        uri = "//"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(uuri.HasField('authority'))
        self.assertFalse(uuri.HasField('resource'))
        self.assertFalse(uuri.HasField('entity'))
        self.assertTrue(UriValidator.is_empty(uuri))

    def test_parse_protocol_uri_with_schema_and_3_slash_and_something(self):
        uri = "///body.access"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(uuri.HasField('authority'))
        self.assertFalse(uuri.HasField('resource'))
        self.assertFalse(uuri.HasField('entity'))
        self.assertTrue(UriValidator.is_empty(uuri))
        self.assertNotEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)

    def test_parse_protocol_uri_with_schema_and_4_slash_and_something(self):
        uri = "////body.access"
        uuri = LongUriSerializer().deserialize(uri)

        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertFalse(uuri.HasField('resource'))
        self.assertFalse(uuri.HasField('entity'))
        self.assertTrue(len(uuri.entity.name) == 0)
        self.assertEqual(0, uuri.entity.version_major)

    def test_parse_protocol_uri_with_schema_and_5_slash_and_something(self):
        uri = "/////body.access"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertFalse(uuri.HasField('resource'))
        self.assertFalse(uuri.HasField('entity'))
        self.assertTrue(UriValidator.is_empty(uuri))

    def test_parse_protocol_uri_with_schema_and_6_slash_and_something(self):
        uri = "//////body.access"
        uuri = LongUriSerializer().deserialize(uri)

        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertTrue(UriValidator.is_empty(uuri))

    def test_parse_protocol_uri_with_local_service_no_version(self):
        uri = "/body.access"
        uuri = LongUriSerializer().deserialize(uri)

        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual(0, uuri.entity.version_minor)
        self.assertFalse(uuri.HasField('resource'))

    def test_parse_protocol_uri_with_local_service_with_version(self):
        uri = "/body.access/1"
        uuri = LongUriSerializer().deserialize(uri)

        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertFalse(uuri.HasField('resource'))

    def test_parse_protocol_uri_with_local_service_no_version_with_resource_name_only(self):
        uri = "/body.access//door"
        uuri = LongUriSerializer().deserialize(uri)

        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual(0, uuri.entity.version_minor)
        self.assertEqual("door", uuri.resource.name)
        self.assertTrue(len(uuri.resource.instance) == 0)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_local_service_with_version_with_resource_name_only(self):
        uri = "/body.access/1/door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertTrue(len(uuri.resource.instance) == 0)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_local_service_no_version_with_resource_with_instance(self):
        uri = "/body.access//door.front_left"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_local_service_with_version_with_resource_with_getMessage(self):
        uri = "/body.access/1/door.front_left"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_local_service_no_version_with_resource_with_instance_and_getMessage(self):
        uri = "/body.access//door.front_left#Door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertFalse(len(uuri.resource.message) == 0)
        self.assertEqual("Door", uuri.resource.message)

    def test_parse_protocol_uri_with_local_service_with_version_with_resource_with_instance_and_getMessage(self):
        uri = "/body.access/1/door.front_left#Door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertFalse(len(uuri.resource.message) == 0)
        self.assertEqual("Door", uuri.resource.message)

    def test_parse_protocol_rpc_uri_with_local_service_no_version(self):
        uri = "/petapp//rpc.response"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("petapp", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("rpc", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("response", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_rpc_uri_with_local_service_with_version(self):
        uri = "/petapp/1/rpc.response"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertFalse(UriValidator.is_remote(uuri.authority))
        self.assertEqual("petapp", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("rpc", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("response", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_remote_service_only_device_and_domain(self):
        uri = "//VCU.MY_CAR_VIN"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)

    def test_parse_protocol_uri_with_remote_service_only_device_and_cloud_domain(self):
        uri = "//cloud.uprotocol.example.com"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("cloud.uprotocol.example.com", uuri.authority.name)
        self.assertFalse(uuri.HasField('entity'))
        self.assertFalse(uuri.HasField('resource'))

    def test_parse_protocol_uri_with_remote_service_no_version(self):
        uri = "//VCU.MY_CAR_VIN/body.access"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertFalse(uuri.HasField('resource'))

    def test_parse_protocol_uri_with_remote_cloud_service_no_version(self):
        uri = "//cloud.uprotocol.example.com/body.access"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("cloud.uprotocol.example.com", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertFalse(uuri.HasField('resource'))

    def test_parse_protocol_uri_with_remote_service_with_version(self):
        uri = "//VCU.MY_CAR_VIN/body.access/1"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertFalse(uuri.HasField('resource'))

    def test_parse_protocol_uri_with_remote_cloud_service_with_version(self):
        uri = "//cloud.uprotocol.example.com/body.access/1"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("cloud.uprotocol.example.com", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertFalse(uuri.HasField('resource'))

    def test_parse_protocol_uri_with_remote_service_no_version_with_resource_name_only(self):
        uri = "//VCU.MY_CAR_VIN/body.access//door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertTrue(len(uuri.resource.instance) == 0)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_remote_cloud_service_no_version_with_resource_name_only(self):
        uri = "//cloud.uprotocol.example.com/body.access//door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("cloud.uprotocol.example.com", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertTrue(len(uuri.resource.instance) == 0)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_remote_service_with_version_with_resource_name_only(self):
        uri = "//VCU.MY_CAR_VIN/body.access/1/door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertTrue(len(uuri.resource.instance) == 0)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_remote_service_cloud_with_version_with_resource_name_only(self):
        uri = "//cloud.uprotocol.example.com/body.access/1/door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("cloud.uprotocol.example.com", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertTrue(len(uuri.resource.instance) == 0)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_remote_service_no_version_with_resource_and_instance_no_getMessage(self):
        uri = "//VCU.MY_CAR_VIN/body.access//door.front_left"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_remote_service_with_version_with_resource_and_instance_no_getMessage(self):
        uri = "//VCU.MY_CAR_VIN/body.access/1/door.front_left"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_uri_with_remote_service_no_version_with_resource_and_instance_and_getMessage(self):
        uri = "//VCU.MY_CAR_VIN/body.access//door.front_left#Door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertFalse(len(uuri.resource.message) == 0)
        self.assertEqual("Door", uuri.resource.message)

    def test_parse_protocol_uri_with_remote_cloud_service_no_version_with_resource_and_instance_and_getMessage(self):
        uri = "//cloud.uprotocol.example.com/body.access//door.front_left#Door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("cloud.uprotocol.example.com", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertFalse(len(uuri.resource.message) == 0)
        self.assertEqual("Door", uuri.resource.message)

    def test_parse_protocol_uri_with_remote_service_with_version_with_resource_and_instance_and_getMessage(self):
        uri = "//VCU.MY_CAR_VIN/body.access/1/door.front_left#Door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU.MY_CAR_VIN", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertFalse(len(uuri.resource.message) == 0)
        self.assertEqual("Door", uuri.resource.message)

    def test_parse_protocol_uri_with_remote_cloud_service_with_version_with_resource_and_instance_and_getMessage(self):
        uri = "//cloud.uprotocol.example.com/body.access/1/door.front_left#Door"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("cloud.uprotocol.example.com", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertFalse(len(uuri.resource.message) == 0)
        self.assertEqual("Door", uuri.resource.message)

    def test_parse_protocol_uri_with_remote_service_with_version_with_resource_with_message_device_no_domain(self):
        uri = "//VCU/body.access/1/door.front_left"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("VCU", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("body.access", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("door", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("front_left", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_rpc_uri_with_remote_service_no_version(self):
        uri = "//bo.cloud/petapp//rpc.response"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("bo.cloud", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("petapp", uuri.entity.name)
        self.assertEqual(0, uuri.entity.version_major)
        self.assertEqual("rpc", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("response", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_parse_protocol_rpc_uri_with_remote_service_with_version(self):
        uri = "//bo.cloud/petapp/1/rpc.response"
        uuri = LongUriSerializer().deserialize(uri)
        self.assertTrue(UriValidator.is_remote(uuri.authority))
        self.assertFalse(len(uuri.authority.name) == 0)
        self.assertEqual("bo.cloud", uuri.authority.name)
        self.assertFalse(len(uuri.entity.name) == 0)
        self.assertEqual("petapp", uuri.entity.name)
        self.assertNotEqual(0, uuri.entity.version_major)
        self.assertEqual(1, uuri.entity.version_major)
        self.assertEqual("rpc", uuri.resource.name)
        self.assertFalse(len(uuri.resource.instance) == 0)
        self.assertEqual("response", uuri.resource.instance)
        self.assertTrue(len(uuri.resource.message) == 0)

    def test_build_protocol_uri_from__uri_when__uri_isnull(self):
        uprotocoluri = LongUriSerializer().serialize(None)
        self.assertEqual('', uprotocoluri)

    def test_build_protocol_uri_from__uri_when__uri_isEmpty(self):
        uuri = UUri()
        uprotocoluri = LongUriSerializer().serialize(uuri)
        self.assertEqual('', uprotocoluri)

    def test_build_protocol_uri_from__uri_when__uri_has_empty_use(self):
        use = UEntity()
        uuri = UUri(authority=UAuthority(), entity=use, resource=UResource(name="door"))
        uprotocoluri = LongUriSerializer().serialize(uuri)
        self.assertEqual("/////door", uprotocoluri)

    def test_build_protocol_uri_from__uri_when__uri_has_local_authority_service_no_version(self):
        uuri = UUri(entity=UEntity(name="body.access"))
        uprotocoluri = LongUriSerializer().serialize(uuri)
        self.assertEqual("/body.access", uprotocoluri)

    def test_build_protocol_uri_from__uri_when__uri_has_local_authority_service_and_version(self):
        use = UEntity(name="body.access", version_major=1)
        uuri = UUri(entity=use, resource=UResource())
        uprotocoluri = LongUriSerializer().serialize(uuri)
        self.assertEqual("/body.access/1", uprotocoluri)

    def test_build_protocol_uri_from__uri_when__uri_has_local_authority_service_no_version_with_resource(self):
        use = UEntity(name="body.access")
        uuri = UUri(entity=use, resource=UResource(name="door"))
        uprotocoluri = LongUriSerializer().serialize(uuri)
        self.assertEqual("/body.access//door", uprotocoluri)

    def test_build_protocol_uri_from__uri_when__uri_has_local_authority_service_and_version_with_resource(self):
        use = UEntity(name="body.access", version_major=1)
        uuri = UUri(entity=use, resource=UResource(name="door"))
        uprotocoluri = LongUriSerializer().serialize(uuri)
        self.assertEqual("/body.access/1/door", uprotocoluri)


if __name__ == '__main__':
    unittest.main()
