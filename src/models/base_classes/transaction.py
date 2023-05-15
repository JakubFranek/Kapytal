from abc import ABC, abstractmethod
from collections.abc import Collection
from datetime import datetime
from typing import TYPE_CHECKING

from src.models.mixins.copyable_mixin import CopyableMixin

if TYPE_CHECKING:
    from src.models.base_classes.account import Account

from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin
from src.models.mixins.json_serializable_mixin import JSONSerializableMixin
from src.models.mixins.uuid_mixin import UUIDMixin
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    InvalidAttributeError,
)


# IDEA: think about slots
class Transaction(
    CopyableMixin, DatetimeCreatedMixin, UUIDMixin, JSONSerializableMixin, ABC
):
    DESCRIPTION_MIN_LENGTH = 0
    DESCRIPTION_MAX_LENGTH = 256

    def __init__(self) -> None:
        super().__init__()
        self._tags = []

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

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def tags(self) -> tuple[Attribute, ...]:
        return tuple(self._tags)

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
        if isinstance(datetime_, datetime):
            self._timestamp = datetime_.timestamp()
        else:
            self._timestamp = float(0)

    def add_tags(self, tags: Collection[Attribute]) -> None:
        self._validate_tags(tags)
        for tag in tags:
            if tag not in self._tags:
                self._tags.append(tag)

    def remove_tags(self, tags: Collection[Attribute]) -> None:
        self._validate_tags(tags)
        for tag in tags:
            if tag in self._tags:
                self._tags.remove(tag)

    def clear_tags(self) -> None:
        self._tags.clear()

    def _validate_tags(self, tags: Collection[Attribute]) -> None:
        if not isinstance(tags, Collection):
            raise TypeError("Parameter 'tags' must be a Collection.")
        if not all(isinstance(tag, Attribute) for tag in tags):
            raise TypeError("Parameter 'tags' must be a Collection of Attributes.")
        if not all(tag.type_ == AttributeType.TAG for tag in tags):
            raise InvalidAttributeError(
                "Parameter 'tags' must contain only Attributes with type_=TAG."
            )

    @abstractmethod
    def is_account_related(self, account: "Account") -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_accounts_related(self, accounts: Collection["Account"]) -> bool:
        raise NotImplementedError

    @abstractmethod
    def prepare_for_deletion(self) -> None:
        raise NotImplementedError
