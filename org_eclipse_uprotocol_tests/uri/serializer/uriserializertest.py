import unittest

from org_eclipse_uprotocol.proto.uri_pb2 import UAuthority, UEntity, UResource, UUri
from org_eclipse_uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from org_eclipse_uprotocol.uri.serializer.microuriserializer import MicroUriSerializer
from org_eclipse_uprotocol.uri.validator.urivalidator import UriValidator


class UriSerializerTest(unittest.TestCase):

    def test_build_resolved_valid_long_micro_uri(self):
        long_uuri = UUri(authority=UAuthority(name="testauth"), entity=UEntity(name="neelam"),
                        resource=UResource(name="rpc", instance="response"))
        micro_uuri = UUri(entity=UEntity(id=29999, version_major=254), resource=UResource(id=39999))
        microuri = MicroUriSerializer().serialize(micro_uuri)
        longuri = LongUriSerializer().serialize(long_uuri)
        resolved_uuri = LongUriSerializer().build_resolved(longuri, microuri)
        self.assertTrue(resolved_uuri)
        self.assertFalse(UriValidator.is_empty(resolved_uuri))
        self.assertEqual("testauth", resolved_uuri.authority.name)
        self.assertEqual("neelam", resolved_uuri.entity.name)
        self.assertEqual(29999, resolved_uuri.entity.id)
        self.assertEqual(254, resolved_uuri.entity.version_major)
        self.assertEqual("rpc", resolved_uuri.resource.name)
        self.assertEqual("response", resolved_uuri.resource.instance)
        self.assertEqual(39999, resolved_uuri.resource.id)

    def test_build_resolved_null_long_null_micro_uri(self):
        result = MicroUriSerializer().build_resolved(None, None)
        self.assertTrue(result)
        self.assertTrue(UriValidator.is_empty(result))

    def test_build_resolved_null_long_micro_uri(self):
        result = MicroUriSerializer().build_resolved(None, bytes())
        self.assertTrue(result)
        self.assertTrue(UriValidator.is_empty(result))

    def test_build_resolved_valid_long_null_micro_uri(self):
        result = MicroUriSerializer().build_resolved("", bytes())
        self.assertTrue(result)
        self.assertTrue(UriValidator.is_empty(result))

#
# if __name__ == '__main__':
#     unittest.main()
