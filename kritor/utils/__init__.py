import functools
import inspect
import sys
import traceback
import types
import typing
import warnings
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Callable,
    Generator,
    Iterable,
    List,
    MutableSet,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from typing import TYPE_CHECKING
from ..typing import ExceptionHook, P, R, T, Wrapper

def gen_subclass(cls: Type[T]) -> Generator[Type[T], None, None]:
    """生成某个类的所有子类 (包括其自身)

    Args:
        cls (Type[T]): 类

    Yields:
        Type[T]: 子类
    """
    yield cls
    for sub_cls in cls.__subclasses__():
        if TYPE_CHECKING:
            assert issubclass(sub_cls, cls)
        yield from gen_subclass(sub_cls)

_T_cls = TypeVar("_T_cls", bound=type)
__SAFE_MODULES__: List[str] = ["graia", "launart", "statv", "pydantic", "aiohttp", "avilla"]
def internal_cls(alt: Optional[Callable] = None) -> Callable[[_T_cls], _T_cls]:
    """将一个类型包装为内部类, 可通过 __SAFE_MODULES__ 定制."""
    if alt:
        hint = f"Use {alt.__module__}.{alt.__qualname__}!"
    else:
        hint = "Only modules start with {module} can initialize it!"

    SAFE_MODULES = tuple(__SAFE_MODULES__)

    def deco(cls: _T_cls) -> _T_cls:
        origin_init = cls.__init__

        @functools.wraps(origin_init)
        def _wrapped_init_(self: object, *args, **kwargs):
            frame = inspect.stack()[1].frame  # outer frame
            module_name: str = frame.f_globals["__name__"]
            if not module_name.startswith(SAFE_MODULES):
                raise NameError(
                    f"{self.__class__.__module__}.{self.__class__.__qualname__} is an internal class!",
                    hint.format(module=self.__class__.__module__),
                )
            return origin_init(self, *args, **kwargs)

        cls.__init__ = _wrapped_init_
        return cls

    return deco
