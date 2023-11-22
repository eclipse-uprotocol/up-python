import unittest

from org_eclipse_uprotocol.cloudevent.datamodel.ucloudeventattributes import UCloudEventAttributesBuilder, \
    UCloudEventAttributes
from org_eclipse_uprotocol.proto.uattributes_pb2 import UPriority


class UCloudEventAttributesTest(unittest.TestCase):

    # def test_hash_code_equals(self):
    #     # Assuming you have an equivalent of EqualsVerifier in Python
    #     # For example, using the `attrs` library to define data classes
    #     self.fail("Not implemented: Need equivalent of EqualsVerifier in Python")

    def test_to_string(self):
        u_cloud_event_attributes = UCloudEventAttributesBuilder().with_hash("somehash").with_priority(
            UPriority.UPRIORITY_CS1).with_ttl(3).with_token("someOAuthToken").build()

        expected = "UCloudEventAttributes{hash='somehash', priority=UPRIORITY_CS1, ttl=3, token='someOAuthToken'}"
        self.assertEqual(expected, str(u_cloud_event_attributes))

    def test_create_valid(self):
        u_cloud_event_attributes = UCloudEventAttributesBuilder().with_hash("somehash").with_priority(
            UPriority.UPRIORITY_CS6).with_ttl(3).with_token("someOAuthToken").build()

        self.assertEqual("somehash", u_cloud_event_attributes.get_hash())
        self.assertEqual(UPriority.Name(UPriority.UPRIORITY_CS6), u_cloud_event_attributes.get_priority())
        self.assertEqual(3, u_cloud_event_attributes.get_ttl())
        self.assertEqual("someOAuthToken", u_cloud_event_attributes.get_token())

    def test_is_empty_function(self):
        u_cloud_event_attributes = UCloudEventAttributes.empty()
        self.assertTrue(u_cloud_event_attributes.is_empty())
        self.assertTrue(u_cloud_event_attributes.priority is None)
        self.assertTrue(u_cloud_event_attributes.token is None)
        self.assertTrue(u_cloud_event_attributes.ttl is None)

    def test_is_empty_function_when_built_with_blank_strings(self):
        u_cloud_event_attributes = UCloudEventAttributesBuilder().with_hash("  ").with_token("  ").build()
        self.assertTrue(u_cloud_event_attributes.is_empty())
        self.assertTrue(u_cloud_event_attributes.hash.isspace())
        self.assertTrue(u_cloud_event_attributes.priority is None)
        self.assertTrue(u_cloud_event_attributes.token.isspace())
        self.assertTrue(u_cloud_event_attributes.ttl is None)

    def test_is_empty_function_permutations(self):
        u_cloud_event_attributes = UCloudEventAttributesBuilder().with_hash("  ").with_token("  ").build()
        self.assertTrue(u_cloud_event_attributes.is_empty())

        u_cloud_event_attributes2 = UCloudEventAttributesBuilder().with_hash("someHash").with_token("  ").build()
        self.assertFalse(u_cloud_event_attributes2.is_empty())

        u_cloud_event_attributes3 = UCloudEventAttributesBuilder().with_hash(" ").with_token("SomeToken").build()
        self.assertFalse(u_cloud_event_attributes3.is_empty())

        u_cloud_event_attributes4 = UCloudEventAttributesBuilder().with_priority(UPriority.UPRIORITY_CS0).build()
        self.assertFalse(u_cloud_event_attributes4.is_empty())

        u_cloud_event_attributes5 = UCloudEventAttributesBuilder().with_ttl(8).build()
        self.assertFalse(u_cloud_event_attributes5.is_empty())


if __name__ == '__main__':
    unittest.main()
