"""本模块提供 Ariadne 消息相关部件."""
from datetime import datetime
from typing import TYPE_CHECKING, Literal

from pydantic import Field, validator

from ..models.base import KritorBaseModel
from ..utils import internal_cls

if TYPE_CHECKING:
    from .chain import MessageChain


class Source(KritorBaseModel):
    """表示消息在一个特定聊天区域内的唯一标识"""

    type: str = "Source"

    id: int
    """消息 ID"""

    time: datetime
    """发送时间"""

    def __int__(self):
        return self.id

    async def fetch_original(self) -> "MessageChain":
        """尝试从本标记恢复原本的消息链, 有可能失败.

        Returns:
            MessageChain: 原来的消息链.
        """
        from ..app import Ariadne

        return (await Ariadne.current().get_message_from_id(self.id)).message_chain

class Quote(KritorBaseModel):
    """表示消息中回复其他消息/用户的部分"""

    type: str = "Quote"

    id: int
    """引用的消息 ID"""

    def as_persistent_string(self) -> str:
        return ""
