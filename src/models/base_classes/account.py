from abc import ABC, abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING

from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin
from src.models.mixins.name_mixin import NameMixin
from src.models.mixins.uuid_mixin import UUIDMixin
from src.models.model_objects.account_group import AccountGroup

if TYPE_CHECKING:  # pragma: no cover
    from src.models.base_classes.transaction import Transaction


class UnrelatedAccountError(ValueError):
    """Raised when an Account tries to access a Transaction which does
    not relate to it."""


class Account(NameMixin, DatetimeCreatedMixin, UUIDMixin, ABC):
    def __init__(self, name: str, parent: AccountGroup | None = None) -> None:
        super().__init__(name=name)
        self.parent: AccountGroup | None = parent

    @property
    def parent(self) -> AccountGroup | None:
        return self._parent

    @parent.setter
    def parent(self, new_parent: AccountGroup | None) -> None:
        if new_parent is not None and not isinstance(new_parent, AccountGroup):
            raise TypeError(
                f"{self.__class__.__name__}.parent must be an AccountGroup or a None."
            )

        if hasattr(self, "_parent") and self._parent is not None:
            self._parent._children.remove(self)

        if new_parent is not None:
            new_parent._children.append(self)

        self._parent = new_parent

    @property
    @abstractmethod
    def balance(self) -> Decimal:
        raise NotImplementedError("Not implemented")

    @property
    @abstractmethod
    def transactions(self) -> tuple["Transaction", ...]:
        raise NotImplementedError("Not implemented.")

    @property
    def path(self) -> str:
        if self.parent is None:
            return self.name
        return self.parent.path + "/" + self.name
