from datetime import datetime
from typing import Any

from src.models.user_settings import user_settings


class DatetimeCreatedMixin:
    __slots__ = ()

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs)
        self._datetime_created = datetime.now(user_settings.settings.time_zone).replace(
            microsecond=0
        )

    @property
    def datetime_created(self) -> datetime:
        return self._datetime_created
