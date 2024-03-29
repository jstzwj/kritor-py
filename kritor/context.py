from contextlib import contextmanager, suppress
from contextvars import ContextVar
from typing import TYPE_CHECKING

from kritor.app import KritorApp

if TYPE_CHECKING:
    from asyncio.events import AbstractEventLoop
    from .app import KritorApp


kritor_ctx: ContextVar[KritorApp] = ContextVar("kritor")


context_map: dict[str, ContextVar] = {
    "Kritor": kritor_ctx,
    "Dispatchable": event_ctx,
    "AbstractEventLoop": event_loop_ctx,
}
