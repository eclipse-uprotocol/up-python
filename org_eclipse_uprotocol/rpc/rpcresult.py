from abc import ABC, abstractmethod
from typing import Callable, TypeVar, Union

from google.rpc.code_pb2 import Code
from google.rpc.status_pb2 import Status

T = TypeVar('T')


class RpcResult(ABC):

    @abstractmethod
    def isSuccess(self) -> bool:
        pass

    @abstractmethod
    def isFailure(self) -> bool:
        pass

    @abstractmethod
    def getOrElse(self, default_value: T) -> T:
        pass

    @abstractmethod
    def map(self, f: Callable[[T], T]) -> 'RpcResult':
        pass

    @abstractmethod
    def flatMap(self, f: Callable[[T], 'RpcResult']) -> 'RpcResult':
        pass

    @abstractmethod
    def filter(self, f: Callable[[T], bool]) -> 'RpcResult':
        pass

    @abstractmethod
    def failureValue(self) -> Status:
        pass

    @abstractmethod
    def successValue(self) -> T:
        pass

    def success(value: T) -> 'RpcResult':
        return Success(value)

    def failure(value: Union[Status, Exception, None] = None, code: Code = Code.UNKNOWN,
                message: str = '') -> 'RpcResult':
        return Failure(value, code, message)

    def flatten(result: 'RpcResult') -> 'RpcResult':
        return result.flatMap(lambda x: x)


class Success(RpcResult):

    def __init__(self, value: T):
        self.value = value

    def isSuccess(self) -> bool:
        return True

    def isFailure(self) -> bool:
        return False

    def getOrElse(self, default_value: T) -> T:
        return self.successValue()

    def map(self, f: Callable[[T], T]) -> RpcResult:
        try:
            return self.success()
        except Exception as e:
            return self.failure(e)

    def flatMap(self, f: Callable[[T], RpcResult]) -> RpcResult:
        try:
            return f(self.successValue())
        except Exception as e:
            return self.failure(e)

    def filter(self, f: Callable[[T], bool]) -> RpcResult:
        try:
            return self if f(self.successValue()) else self.failure(Code.FAILED_PRECONDITION, "filtered out")
        except Exception as e:
            return self.failure(e)

    def failureValue(self) -> Status:
        raise ValueError("Method failureValue() called on a Success instance")

    def successValue(self) -> T:
        return self.value

    def __str__(self) -> str:
        return f"Success({self.successValue()})"


class Failure(RpcResult):

    def __init__(self, value: Union[Status, Exception, None] = None, code: Code = Code.UNKNOWN, message: str = ''):
        if isinstance(value, Status):
            self.value = value
        elif isinstance(value, Exception):
            self.value = Status(code=code, message=str(value))
        else:
            self.value = Status(code=code, message=message)

    def isSuccess(self) -> bool:
        return False

    def isFailure(self) -> bool:
        return True

    def getOrElse(self, default_value: T) -> T:
        return default_value

    def map(self, f: Callable[[T], T]) -> RpcResult:
        return self.failure(self)

    def flatMap(self, f: Callable[[T], RpcResult]) -> RpcResult:
        return self.failure(self.failureValue())

    def filter(self, f: Callable[[T], bool]) -> RpcResult:
        return self.failure(self)

    def failureValue(self) -> Status:
        return self.value

    def successValue(self) -> T:
        raise ValueError("Method successValue() called on a Failure instance")

    def __str__(self) -> str:
        return f"Failure({self.value})"
