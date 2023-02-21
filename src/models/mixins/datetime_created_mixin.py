from datetime import datetime
from typing import Any

import src.models.user_settings.user_settings as user_settings


class DatetimeCreatedMixin:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._datetime_created = datetime.now(user_settings.settings.time_zone)

    @property
    def datetime_created(self) -> datetime:
        return self._datetime_created
