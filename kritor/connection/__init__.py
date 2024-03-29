from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, ClassVar, Generic
from typing_extensions import Self

from statv import Stats

from ..event import KritorEvent
from ..utils.string import camel_to_snake
from ._info import T_Info, U_Info, GrpcClientInfo, GrpcServerInfo

if TYPE_CHECKING:
    from ..service import ElizabethService

