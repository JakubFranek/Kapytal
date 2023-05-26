import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from src.models.mixins.copyable_mixin import CopyableMixin
from src.models.mixins.get_balance_mixin import BalanceMixin
from src.models.mixins.json_serializable_mixin import JSONSerializableMixin
from src.models.mixins.name_mixin import NameMixin
from src.models.mixins.uuid_mixin import UUIDMixin
from src.models.model_objects.account_group import AccountGroup

if TYPE_CHECKING:
    from src.models.base_classes.transaction import Transaction


class UnrelatedAccountError(ValueError):
    """Raised when an Account tries to access a Transaction which does
    not relate to it."""


# TODO: add ancestors/descendents properties (also to AG)


# IDEA: create base for Account and AccountGroup (AccountTreeItem)
# getbalance, parent, transactions
class Account(
    CopyableMixin, NameMixin, UUIDMixin, BalanceMixin, JSONSerializableMixin, ABC
):
    def __init__(self, name: str, parent: AccountGroup | None = None) -> None:
        super().__init__(name=name, allow_slash=False)
        self.parent = parent

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.path}')"

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

        if hasattr(self, "_parent"):
            logging.info(f"Changing parent from {self._parent} to {parent}")
        else:
            logging.info(f"Setting {parent=}")
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
