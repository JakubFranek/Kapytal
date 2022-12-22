from datetime import datetime

from src.models.constants import tzinfo


# TODO: evaluate whether this Mixin is even necessary
# maybe for sorting items based on last edit?
# (logs should cover debugging needs)
class DatetimeEditedMixin:
    def __init__(self) -> None:
        super().__init__()
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def datetime_edited(self) -> datetime:
        return self._datetime_edited
