from abc import ABC, abstractmethod
from concurrent.futures import Future

from org_eclipse_uprotocol.transport.datamodel.uattributes import UAttributes
from org_eclipse_uprotocol.transport.datamodel.upayload import UPayload
from org_eclipse_uprotocol.uri.datamodel.uuri import UUri


class RpcClient(ABC):
    @abstractmethod
    def invoke_method(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> Future:  # Future of Upayload
        pass
