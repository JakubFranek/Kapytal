from typing import TYPE_CHECKING, Any, Self

from src.models.custom_exceptions import NotFoundError

if TYPE_CHECKING:
    from src.models.base_classes.account import Account

from src.models.mixins.get_balance_mixin import GetBalanceMixin
from src.models.mixins.json_serializable_mixin import JSONSerializableMixin
from src.models.mixins.name_mixin import NameMixin
from src.models.model_objects.currency_objects import CashAmount, Currency
from src.models.utilities.find_helpers import find_account_group_by_path


class AccountGroup(NameMixin, GetBalanceMixin, JSONSerializableMixin):
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
        return f"AccountGroup(path='{self.path}')"

    @property
    def path(self) -> str:
        if self.parent is None:
            return self.name
        return self.parent.path + "/" + self.name

    def set_child_index(self, child: "Account" | Self, index: int) -> None:
        if child not in self._children:
            raise NotFoundError(
                "Parameter 'child' not in this AccountGroup's children."
            )
        self._children.remove(child)
        self._children.insert(index, child)

    def get_balance(self, currency: Currency) -> CashAmount:
        return sum(
            (child.get_balance(currency) for child in self._children),
            start=CashAmount(0, currency),
        )

    def serialize(self) -> dict[str, Any]:
        return {
            "datatype": "AccountGroup",
            "path": self.path,
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any], account_groups: list["AccountGroup"]
    ) -> "AccountGroup":
        path: str = data["path"]
        parent_path, _, name = path.rpartition("/")
        obj = AccountGroup(name)
        if parent_path != "":
            obj.parent = find_account_group_by_path(parent_path, account_groups)
        return obj
