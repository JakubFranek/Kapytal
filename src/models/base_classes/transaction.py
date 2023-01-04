from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.base_classes.account import Account

from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin
from src.models.mixins.uuid_mixin import UUIDMixin


class Transaction(DatetimeCreatedMixin, UUIDMixin, ABC):
    DESCRIPTION_MIN_LENGTH = 0
    DESCRIPTION_MAX_LENGTH = 256

    def __init__(self, description: str, datetime_: datetime) -> None:
        super().__init__()
        self.description = description
        self.datetime_ = datetime_

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{self.__class__.__name__}.description must be a string.")

        if (
            len(value) < Transaction.DESCRIPTION_MIN_LENGTH
            or len(value) > Transaction.DESCRIPTION_MAX_LENGTH
        ):
            raise ValueError(
                f"{self.__class__.__name__}.description length must be between "
                f"{Transaction.DESCRIPTION_MIN_LENGTH} and "
                f"{Transaction.DESCRIPTION_MAX_LENGTH} characters."
            )

        self._description = value

    @property
    def datetime_(self) -> datetime:
        return self._datetime

    @datetime_.setter
    def datetime_(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise TypeError(f"{self.__class__.__name__}.datetime_ must be a datetime.")

        self._datetime = value

    @abstractmethod
    def is_account_related(self, account: "Account") -> bool:
        raise NotImplementedError("Not implemented")
