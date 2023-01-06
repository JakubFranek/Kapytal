from datetime import datetime
from typing import Any

from src.models.constants import tzinfo


class DatetimeCreatedMixin:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._datetime_created = datetime.now(tzinfo)

    @property
    def datetime_created(self) -> datetime:
        return self._datetime_created
