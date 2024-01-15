from abc import ABC, abstractmethod
from collections.abc import Collection
from datetime import date, datetime
from typing import TYPE_CHECKING

from src.models.custom_exceptions import NotFoundError
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


class Transaction(
    CopyableMixin, DatetimeCreatedMixin, UUIDMixin, JSONSerializableMixin, ABC
):
    __slots__ = ()

    DESCRIPTION_MIN_LENGTH = 0
    DESCRIPTION_MAX_LENGTH = 256

    def __init__(self) -> None:
        super().__init__()
        self._tags: frozenset[Attribute] = frozenset()
        self._datetime: datetime

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
    def date_(self) -> date:
        return self._datetime.date()

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def tags(self) -> frozenset[Attribute]:
        return self._tags

    def _validate_datetime(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise TypeError(f"{self.__class__.__name__}.datetime_ must be a datetime.")

    # TODO: create base _set_attributes version to use for description and datetime set
    def set_attributes(
        self,
        description: str | None = None,
        datetime_: datetime | None = None,
        *,
        block_account_update: bool = False,  # noqa: ARG002
    ) -> None:
        """Validates and sets provided attributes if they are all valid.
        Parameters set to None keep their value."""

        if description is None:
            description = self._description
        if datetime_ is None:
            datetime_ = self._datetime
        self._validate_description(description)
        self._validate_datetime(datetime_)
        self._description = description.strip()
        self._datetime = datetime_
        self._timestamp = datetime_.timestamp()

    def add_tags(self, tags: Collection[Attribute]) -> None:
        self._validate_tags(tags)
        self._tags = self._tags.union(tags)

    def remove_tags(self, tags: Collection[Attribute]) -> None:
        self._validate_tags(tags)
        self._tags = self._tags.difference(tags)

    def replace_tag(self, replaced_tag: Attribute, replacement_tag: Attribute) -> None:
        self._validate_tags((replaced_tag, replacement_tag))
        if replaced_tag not in self._tags:
            raise NotFoundError(
                f"Tag '{replaced_tag.name}' not found in this "
                f"{self.__class__.__name__}'s Tags."
            )
        tags = set(self._tags)
        tags.remove(replaced_tag)
        tags.add(replacement_tag)
        self._tags = frozenset(tags)

    def clear_tags(self) -> None:
        self._tags = frozenset()

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
