from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Literal, Union
from typing_extensions import NotRequired, TypedDict, TypeAlias

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from kritor.utils.string import snake_to_camel

IncEx: TypeAlias = 'set[int] | set[str] | dict[int, Any] | dict[str, Any] | None'

class KritorBaseModel(BaseModel):
    model_config = SettingsConfigDict(
        extra = 'allow',
        arbitrary_types_allowed = True,
        json_encoders = {
            datetime: lambda dt: int(dt.timestamp()),
        }
    )

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

    def model_dump(
        self,
        *,
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        skip_defaults: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        to_camel: bool = False,
    ) -> Dict[str, Any]:
        _, *_ = by_alias, exclude_none, skip_defaults
        data = super().model_dump(
            include=include,  # type: ignore
            exclude=exclude,  # type: ignore
            by_alias=True,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=True,
        )
        if to_camel:
            data = {snake_to_camel(k): v for k, v in data.items()}
        return data
