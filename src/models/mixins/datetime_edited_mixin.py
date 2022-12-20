from datetime import datetime

from src.models.constants import tzinfo


class DatetimeEditedMixin:
    def __init__(self) -> None:
        super().__init__()
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def datetime_edited(self) -> datetime:
        return self._datetime_edited
