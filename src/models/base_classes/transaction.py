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

    def __init__(self) -> None:
        super().__init__()

    @property
    def description(self) -> str:
        return self._description

    def _validate_description(self, value: str) -> None:
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

    @property
    def datetime_(self) -> datetime:
        return self._datetime

    def _validate_datetime(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise TypeError(f"{self.__class__.__name__}.datetime_ must be a datetime.")

    def set_attributes(
        self, description: str | None = None, datetime_: datetime | None = None
    ) -> None:
        """Validates and sets provided attributes if they are all valid.
        Parameters set to None keep their value."""

        if description is None:
            description = self._description
        if datetime_ is None:
            datetime_ = self._datetime
        self._validate_description(description)
        self._validate_datetime(datetime_)
        self._description = description
        self._datetime = datetime_

    @abstractmethod
    def is_account_related(self, account: "Account") -> bool:
        raise NotImplementedError
