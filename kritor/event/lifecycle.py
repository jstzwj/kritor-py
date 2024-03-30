"""生命周期相关事件"""
import typing

from kritor.broadcast.entities.event import Dispatchable
from kritor.broadcast.interfaces.dispatcher import DispatcherInterface

from ..dispatcher import BaseDispatcher
from ..typing import generic_issubclass

if typing.TYPE_CHECKING:
    from ..app import KritorApp


class ApplicationLifecycleEvent(Dispatchable):
    """指示有关应用的事件."""

    app: "KritorApp"

    def __init__(self, app: "KritorApp") -> None:
        self.app = app

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            from ..app import KritorApp

            if isinstance(interface.event, ApplicationLifecycleEvent) and generic_issubclass(
                KritorApp, interface.annotation
            ):
                return interface.event.app


class ApplicationLaunch(ApplicationLifecycleEvent):
    """启动"""


class ApplicationShutdown(ApplicationLifecycleEvent):
    """关闭"""


ApplicationLaunched = ApplicationLaunch
ApplicationShutdowned = ApplicationShutdown


class AccountLaunch(ApplicationLifecycleEvent):
    """指示账号的链接已启动."""


class AccountShutdown(ApplicationLifecycleEvent):
    """指示账号的链接关闭."""


class AccountConnectionFail(ApplicationLifecycleEvent):
    """和 mirai-api-http 的链接断开，不论是因为连接失败还是配置失败"""
