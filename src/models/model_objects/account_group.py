from decimal import Decimal
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:  # pragma: no cover
    from src.models.base_classes.account import Account

from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin
from src.models.mixins.name_mixin import NameMixin


class AccountGroup(NameMixin, DatetimeCreatedMixin):
    def __init__(self, name: str, parent: Self | None = None) -> None:
        super().__init__(name)
        self.parent = parent
        self._children: list[Self | "Account"] = []

    @property
    def parent(self) -> Self | None:
        return self._parent

    @parent.setter
    def parent(self, new_parent: Self | None) -> None:
        if new_parent is not None and not isinstance(new_parent, AccountGroup):
            raise TypeError("AccountGroup.parent must be an AccountGroup or a None.")

        if hasattr(self, "_parent") and self._parent is not None:
            self._parent._children.remove(self)

        if new_parent is not None:
            new_parent._children.append(self)

        self._parent = new_parent

    @property
    def children(self) -> tuple["Account" | Self, ...]:
        return tuple(self._children)

    @property
    def balance(self) -> Decimal:
        return Decimal(sum(child.balance for child in self._children))

    def __repr__(self) -> str:
        return f"AccountGroup('{self.name}', parent='{self.parent}')"

    @property
    def path(self) -> str:
        if self.parent is None:
            return self.name
        return self.parent.path + "/" + self.name
