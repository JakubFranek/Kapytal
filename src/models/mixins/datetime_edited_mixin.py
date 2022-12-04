from datetime import datetime


class DatetimeEditedMixin:
    def __init__(self) -> None:
        super().__init__()
        self._datetime_edited = None

    @property
    def datetime_edited(self) -> datetime:
        return self._datetime_edited
