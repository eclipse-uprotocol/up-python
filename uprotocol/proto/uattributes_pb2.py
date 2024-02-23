# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: uattributes.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import uprotocol.proto.uri_pb2 as uri__pb2
import uprotocol.proto.uuid_pb2 as uuid__pb2
import uprotocol.proto.uprotocol_options_pb2 as uprotocol__options__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11uattributes.proto\x12\x0cuprotocol.v1\x1a\turi.proto\x1a\nuuid.proto\x1a\x17uprotocol_options.proto\"\xa9\x03\n\x0bUAttributes\x12\x1e\n\x02id\x18\x01 \x01(\x0b\x32\x12.uprotocol.v1.UUID\x12(\n\x04type\x18\x02 \x01(\x0e\x32\x1a.uprotocol.v1.UMessageType\x12\"\n\x06source\x18\x03 \x01(\x0b\x32\x12.uprotocol.v1.UUri\x12 \n\x04sink\x18\x04 \x01(\x0b\x32\x12.uprotocol.v1.UUri\x12)\n\x08priority\x18\x05 \x01(\x0e\x32\x17.uprotocol.v1.UPriority\x12\x10\n\x03ttl\x18\x06 \x01(\x05H\x00\x88\x01\x01\x12\x1d\n\x10permission_level\x18\x07 \x01(\x05H\x01\x88\x01\x01\x12\x17\n\ncommstatus\x18\x08 \x01(\x05H\x02\x88\x01\x01\x12!\n\x05reqid\x18\t \x01(\x0b\x32\x12.uprotocol.v1.UUID\x12\x12\n\x05token\x18\n \x01(\tH\x03\x88\x01\x01\x12\x18\n\x0btraceparent\x18\x0b \x01(\tH\x04\x88\x01\x01\x42\x06\n\x04_ttlB\x13\n\x11_permission_levelB\r\n\x0b_commstatusB\x08\n\x06_tokenB\x0e\n\x0c_traceparent*\xa3\x01\n\x0cUMessageType\x12\x1d\n\x19UMESSAGE_TYPE_UNSPECIFIED\x10\x00\x12%\n\x15UMESSAGE_TYPE_PUBLISH\x10\x01\x1a\n\xaa\xd4\x18\x06pub.v1\x12%\n\x15UMESSAGE_TYPE_REQUEST\x10\x02\x1a\n\xaa\xd4\x18\x06req.v1\x12&\n\x16UMESSAGE_TYPE_RESPONSE\x10\x03\x1a\n\xaa\xd4\x18\x06res.v1*\xea\x01\n\tUPriority\x12\x19\n\x15UPRIORITY_UNSPECIFIED\x10\x00\x12\x1a\n\rUPRIORITY_CS0\x10\x01\x1a\x07\xaa\xd4\x18\x03\x43S0\x12\x1a\n\rUPRIORITY_CS1\x10\x02\x1a\x07\xaa\xd4\x18\x03\x43S1\x12\x1a\n\rUPRIORITY_CS2\x10\x03\x1a\x07\xaa\xd4\x18\x03\x43S2\x12\x1a\n\rUPRIORITY_CS3\x10\x04\x1a\x07\xaa\xd4\x18\x03\x43S3\x12\x1a\n\rUPRIORITY_CS4\x10\x05\x1a\x07\xaa\xd4\x18\x03\x43S4\x12\x1a\n\rUPRIORITY_CS5\x10\x06\x1a\x07\xaa\xd4\x18\x03\x43S5\x12\x1a\n\rUPRIORITY_CS6\x10\x07\x1a\x07\xaa\xd4\x18\x03\x43S6B.\n\x18org.eclipse.uprotocol.v1B\x10UAttributesProtoP\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'uattributes_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\030org.eclipse.uprotocol.v1B\020UAttributesProtoP\001'
  _UMESSAGETYPE.values_by_name["UMESSAGE_TYPE_PUBLISH"]._options = None
  _UMESSAGETYPE.values_by_name["UMESSAGE_TYPE_PUBLISH"]._serialized_options = b'\252\324\030\006pub.v1'
  _UMESSAGETYPE.values_by_name["UMESSAGE_TYPE_REQUEST"]._options = None
  _UMESSAGETYPE.values_by_name["UMESSAGE_TYPE_REQUEST"]._serialized_options = b'\252\324\030\006req.v1'
  _UMESSAGETYPE.values_by_name["UMESSAGE_TYPE_RESPONSE"]._options = None
  _UMESSAGETYPE.values_by_name["UMESSAGE_TYPE_RESPONSE"]._serialized_options = b'\252\324\030\006res.v1'
  _UPRIORITY.values_by_name["UPRIORITY_CS0"]._options = None
  _UPRIORITY.values_by_name["UPRIORITY_CS0"]._serialized_options = b'\252\324\030\003CS0'
  _UPRIORITY.values_by_name["UPRIORITY_CS1"]._options = None
  _UPRIORITY.values_by_name["UPRIORITY_CS1"]._serialized_options = b'\252\324\030\003CS1'
  _UPRIORITY.values_by_name["UPRIORITY_CS2"]._options = None
  _UPRIORITY.values_by_name["UPRIORITY_CS2"]._serialized_options = b'\252\324\030\003CS2'
  _UPRIORITY.values_by_name["UPRIORITY_CS3"]._options = None
  _UPRIORITY.values_by_name["UPRIORITY_CS3"]._serialized_options = b'\252\324\030\003CS3'
  _UPRIORITY.values_by_name["UPRIORITY_CS4"]._options = None
  _UPRIORITY.values_by_name["UPRIORITY_CS4"]._serialized_options = b'\252\324\030\003CS4'
  _UPRIORITY.values_by_name["UPRIORITY_CS5"]._options = None
  _UPRIORITY.values_by_name["UPRIORITY_CS5"]._serialized_options = b'\252\324\030\003CS5'
  _UPRIORITY.values_by_name["UPRIORITY_CS6"]._options = None
  _UPRIORITY.values_by_name["UPRIORITY_CS6"]._serialized_options = b'\252\324\030\003CS6'
  _UMESSAGETYPE._serialized_start=512
  _UMESSAGETYPE._serialized_end=675
  _UPRIORITY._serialized_start=678
  _UPRIORITY._serialized_end=912
  _UATTRIBUTES._serialized_start=84
  _UATTRIBUTES._serialized_end=509
# @@protoc_insertion_point(module_scope)
