from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from src.models.base_classes.account import Account

from src.models.constants import tzinfo
from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin
from src.models.mixins.datetime_edited_mixin import DatetimeEditedMixin


class Transaction(DatetimeCreatedMixin, DatetimeEditedMixin, ABC):
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
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def datetime_(self) -> datetime:
        return self._datetime

    @datetime_.setter
    def datetime_(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise TypeError(f"{self.__class__.__name__}.datetime_ must be a datetime.")

        self._datetime = value
        self._datetime_edited = datetime.now(tzinfo)

    @abstractmethod
    def is_account_related(self, account: "Account") -> bool:
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def get_amount_for_account(self, account: "Account") -> Decimal:
        raise NotImplementedError("Not implemented")
