from typing import Union
from google.protobuf.any_pb2 import Any
from google.protobuf.message import Message
from uprotocol.proto.uprotocol.v1.uattributes_pb2 import UPayloadFormat
from uprotocol.proto.uprotocol.v1.umessage_pb2 import UMessage
from google.protobuf.wrappers_pb2 import BoolValue
from multimethod import multimethod
from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper
print(type(UPayloadFormat))
class A:
    
    @multimethod
    def build(self, message: Message):
        print("Message")
        pass
    
    @multimethod
    def build(self, message: Any):
        print("Any")
        pass
    
    @multimethod
    def build(self, format: int, payload: bytearray):
        print("format payload")
        pass
    
    @multimethod
    def build(self):
        print("build")
        pass
    
    def test(self) -> "A":
        print("test")
        pass

boolean: Message = BoolValue(value=True)
A().build(boolean)

any: Any = Any()
A().build(any)

A().build(UPayloadFormat.UPAYLOAD_FORMAT_UNSPECIFIED, bytearray([1, 2, 3]))

A().build()

A().test()


from uprotocol.proto.uprotocol.v1.uattributes_pb2 import (
    UAttributes,
    UMessageType,
    UPriority,
)

print(UPriority.UPRIORITY_CS4 >= UPriority.UPRIORITY_CS0)
print(0x8000)