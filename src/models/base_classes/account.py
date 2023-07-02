from abc import ABC, abstractmethod
from datetime import date
from typing import TYPE_CHECKING

from src.models.mixins.copyable_mixin import CopyableMixin
from src.models.mixins.get_balance_mixin import BalanceMixin
from src.models.mixins.json_serializable_mixin import JSONSerializableMixin
from src.models.mixins.name_mixin import NameMixin
from src.models.mixins.uuid_mixin import UUIDMixin
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.currency_objects import CashAmount, Currency

if TYPE_CHECKING:
    from src.models.base_classes.transaction import Transaction


class UnrelatedAccountError(ValueError):
    """Raised when an Account tries to access a Transaction which does
    not relate to it."""


class Account(
    CopyableMixin, NameMixin, UUIDMixin, BalanceMixin, JSONSerializableMixin, ABC
):
    __slots__ = ()

    def __init__(self, name: str, parent: AccountGroup | None = None) -> None:
        super().__init__(name=name, allow_slash=False)
        self.parent = parent

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.path})"

    @property
    def parent(self) -> AccountGroup | None:
        return self._parent

    @parent.setter
    def parent(self, parent: AccountGroup | None) -> None:
        if parent is not None and not isinstance(parent, AccountGroup):
            raise TypeError(
                f"{self.__class__.__name__}.parent must be an AccountGroup or a None."
            )

        if hasattr(self, "_parent"):
            if self._parent == parent:
                return
            if self._parent is not None:
                self._parent._remove_child(self)  # noqa: SLF001

        if parent is not None:
            parent._add_child(self)  # noqa: SLF001

        self._parent = parent

    @property
    def path(self) -> str:
        if self._parent is None:
            return self._name
        return self._parent.path + "/" + self._name

    @property
    @abstractmethod
    def transactions(self) -> tuple["Transaction", ...]:
        raise NotImplementedError

    @abstractmethod
    def get_balance(self, currency: Currency, date_: date | None = None) -> CashAmount:
        """Returns latest balance, or the latest balance for the specified date."""
        # TODO: None date should be initialized to today, which is not necessarily the latest!
        raise NotImplementedError
