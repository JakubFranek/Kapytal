from decimal import Decimal
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:  # pragma: no cover
    from src.models.accounts.account import Account

from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin
from src.models.mixins.name_mixin import NameMixin


class AccountGroup(NameMixin, DatetimeCreatedMixin):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._parent: Self | None = None
        self._children: list[Self | "Account"] = []
        self._balance = Decimal(0)

    @property
    def parent(self) -> Self | None:
        return self._parent

    @parent.setter
    def parent(self, new_parent: Self | None) -> None:
        if new_parent is not None and not isinstance(new_parent, AccountGroup):
            raise TypeError(
                "AccountGroup parent can only be an AccountGroup or a None."
            )

        if self._parent is not None:
            self._parent._children.remove(self)

        if new_parent is not None:
            new_parent._children.append(self)

        self._parent = new_parent

    @property
    def children(self) -> tuple["Account"] | None:
        return tuple(self._children)
