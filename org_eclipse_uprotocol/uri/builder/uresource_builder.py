from org_eclipse_uprotocol.proto.uri_pb2 import UResource


class UResourceBuilder:
    MAX_RPC_ID = 1000

    @staticmethod
    def for_rpc_response():
        return UResource(name="rpc", instance="response", id=0)

    @staticmethod
    def for_rpc_request(method, id=None):
        uresource = UResource(name="rpc")
        if method is not None:
            uresource.instance = method
        if id is not None:
            uresource.id = id

        return uresource

    @staticmethod
    def for_rpc_request_with_id(id):
        return UResourceBuilder.for_rpc_request(None, id)

    @staticmethod
    def from_id(id):
        if id is None:
            raise ValueError("id cannot be None")

        return UResourceBuilder.for_rpc_request(id) if id < UResourceBuilder.MAX_RPC_ID else UResource(id=id)

