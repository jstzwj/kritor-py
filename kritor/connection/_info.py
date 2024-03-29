from typing import Dict, NamedTuple, TypeVar, Union

from yarl import URL


class GrpcClientInfo(NamedTuple):
    account: int
    ticket: str
    host: str
    port: int

    @property
    def endpoint(self) -> str:
        return f"{self.host}:{self.port}"

class GrpcServerInfo(NamedTuple):
    host: str
    port: int


U_Info = Union[GrpcClientInfo, GrpcServerInfo]

T_Info = TypeVar("T_Info", bound=U_Info)
