import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from src.models.mixins.copyable_mixin import CopyableMixin
from src.models.mixins.get_balance_mixin import GetBalanceMixin
from src.models.mixins.json_serializable_mixin import JSONSerializableMixin
from src.models.mixins.name_mixin import NameMixin
from src.models.mixins.uuid_mixin import UUIDMixin
from src.models.model_objects.account_group import AccountGroup

if TYPE_CHECKING:
    from src.models.base_classes.transaction import Transaction


class UnrelatedAccountError(ValueError):
    """Raised when an Account tries to access a Transaction which does
    not relate to it."""


# IDEA: create base for Account and AccountGroup
# getbalance, parent, children, transactions
class Account(
    CopyableMixin, NameMixin, UUIDMixin, GetBalanceMixin, JSONSerializableMixin, ABC
):
    def __init__(self, name: str, parent: AccountGroup | None = None) -> None:
        super().__init__(name=name, allow_slash=False)
        self.parent = parent

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.path}')"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Account):
            return False
        return self.uuid == __o.uuid

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
                self._parent._remove_child(self)

        if parent is not None:
            parent._add_child(self)

        if hasattr(self, "_parent"):
            logging.info(f"Changing parent from {self._parent} to {parent}")
        else:
            logging.info(f"Setting {parent=}")
        self._parent = parent

    @property
    def path(self) -> str:
        if self.parent is None:
            return self.name
        return self.parent.path + "/" + self.name

    @property
    @abstractmethod
    def transactions(self) -> tuple["Transaction", ...]:
        raise NotImplementedError
