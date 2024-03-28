

import inspect
from typing import Any, Callable
import uuid


class KritorHandler(object):
    def __init__(self, fn: Callable[[Any], Any]) -> None:
        self.id = uuid.uuid4().hex
        self.fn = fn
        self.is_sync = not inspect.iscoroutinefunction(self.fn)
    
    def call(self, *args: Any, **kwds: Any) -> Any:
        if self.is_sync:
            self.fn(*args, **kwds)
    
    async def acall(self, *args: Any, **kwds: Any) -> Any:
        if self.is_sync:
            self.fn(*args, **kwds)
        else:
            await self.fn(*args, **kwds)
    
    def get_handler_id(self) -> str:
        return self.id