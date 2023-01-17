from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from src.models.base_classes.account import Account

from src.models.mixins.get_balance_mixin import GetBalanceMixin
from src.models.mixins.name_mixin import NameMixin
from src.models.model_objects.currency import CashAmount, Currency


class AccountGroup(NameMixin, GetBalanceMixin):
    def __init__(self, name: str, parent: Self | None = None) -> None:
        super().__init__(name)
        self.parent = parent
        self._children: list[Self | Account] = []

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

    def __repr__(self) -> str:
        return f"AccountGroup('{self.name}', parent='{self.parent}')"

    @property
    def path(self) -> str:
        if self.parent is None:
            return self.name
        return self.parent.path + "/" + self.name

    def get_balance(self, currency: Currency) -> CashAmount:
        return sum(
            (child.get_balance(currency) for child in self._children),
            start=CashAmount(0, currency),
        )
