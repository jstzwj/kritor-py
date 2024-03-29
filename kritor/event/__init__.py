from graia.broadcast import Dispatchable

from ..dispatcher import BaseDispatcher
from ..models import KritorBaseModel


class KritorEvent(Dispatchable, KritorBaseModel):
    """事件基类"""

    type: str


from . import lifecycle as lifecycle  # noqa: F401, E402
from . import message as message  # noqa: F401, E402
from . import mirai as mirai  # noqa: F401, E402