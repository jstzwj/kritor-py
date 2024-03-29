from typing import Literal, TypedDict
from typing_extensions import NotRequired

class KritorOptions(TypedDict):
    installed_log: NotRequired[Literal[True]]
    inject_bypass_listener: NotRequired[Literal[True]]
    default_account: NotRequired[int]