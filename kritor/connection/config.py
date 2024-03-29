from typing import TYPE_CHECKING, Dict, List, NamedTuple, Sequence, Type, Union, overload
from typing_extensions import NotRequired, Required, TypedDict

from ..typing import DictStrAny
from ._info import GrpcClientInfo, GrpcServerInfo, U_Info

if TYPE_CHECKING:
    from ..app import KritorApp


class GrpcClientConfig(NamedTuple):
    """Grpc 客户端配置"""

    host: str = "localhost"
    port: int = 5700


class GrpcServerConfig(NamedTuple):
    """Grpc 服务器配置"""

    host: str = "localhost"
    port: int = 5090


U_Config = Union[GrpcClientConfig, GrpcServerConfig]

_CFG_INFO_MAP = {
    GrpcClientConfig: GrpcClientInfo,
    GrpcServerConfig: GrpcServerInfo,
}

def config(account: Union[int, str], ticket: str, *configs: Union[Type[U_Config], U_Config]) -> List[U_Info]:
    """生成 Kritor 账号配置
    """
    assert isinstance(account, int) or isinstance(account, str)
    assert isinstance(ticket, str)
    account = str(account)

    configs = configs or (GrpcClientConfig(), )
    infos: List[U_Info] = []
    for cfg in configs:
        if isinstance(cfg, type):
            cfg = cfg()
        infos.append(_CFG_INFO_MAP[type(cfg)](account, ticket, *cfg))
    return infos


class ConfigTypedDict(TypedDict):
    account: Required[int]
    verify_key: Required[str]
    http_client: NotRequired[DictStrAny]
    websocket_client: NotRequired[DictStrAny]
    http_server: NotRequired[DictStrAny]
    websocket_server: NotRequired[DictStrAny]


@overload
def from_obj(obj: Sequence[ConfigTypedDict]) -> List["KritorApp"]:
    ...


@overload
def from_obj(obj: ConfigTypedDict) -> "KritorApp":
    ...


def from_obj(obj: Union[ConfigTypedDict, Sequence[ConfigTypedDict]]) -> Union[List["KritorApp"], "KritorApp"]:
    if isinstance(obj, Sequence):
        return [from_obj(o) for o in obj]
    if isinstance(obj, dict):
        extras: List[U_Config] = []
        if "grpc_client" in obj:
            extras.append(GrpcClientConfig(**obj["grpc_client"]))
        if "grpc_server" in obj:
            extras.append(GrpcServerConfig(**obj["grpc_server"]))

        from ..app import KritorApp

        return KritorApp(config(obj["account"], obj["verify_key"], *extras))
