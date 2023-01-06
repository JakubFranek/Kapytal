from datetime import datetime

from src.models.constants import tzinfo


# TODO: mixin ABC?
# TODO: mixin supers?
class DatetimeCreatedMixin:
    def __init__(self) -> None:
        super().__init__()
        self._datetime_created = datetime.now(tzinfo)

    @property
    def datetime_created(self) -> datetime:
        return self._datetime_created
