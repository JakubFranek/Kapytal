from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin
from src.models.mixins.name_mixin import NameMixin


class Attribute(NameMixin, DatetimeCreatedMixin):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)
