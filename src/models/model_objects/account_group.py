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
        self._children: dict[int, Self | Account] = {}

    @property
    def parent(self) -> Self | None:
        return self._parent

    @parent.setter
    def parent(self, new_parent: Self | None) -> None:
        if new_parent is not None and not isinstance(new_parent, AccountGroup):
            raise TypeError("AccountGroup.parent must be an AccountGroup or a None.")

        if hasattr(self, "_parent"):
            if self._parent == new_parent:
                return
            if self._parent is not None:
                self._parent._remove_child(self)

        if new_parent is not None:
            new_parent._add_child(self)

        self._parent = new_parent

    @property
    def children(self) -> tuple["Account" | Self, ...]:
        return tuple(self._children[key] for key in sorted(self._children.keys()))

    @property
    def path(self) -> str:
        if self.parent is None:
            return self.name
        return self.parent.path + "/" + self.name

    def __repr__(self) -> str:
        return f"AccountGroup(path='{self.path}')"

    def _add_child(self, child: Self | "Account") -> None:
        max_index = max(sorted(self._children.keys()), default=-1)
        self._children[max_index + 1] = child

    def _remove_child(self, child: Self | "Account") -> None:
        index = list(self._children.keys())[list(self._children.values()).index(child)]
        aux_dict: dict[int, AccountGroup | Account] = {}
        for key, value in self._children.items():
            if key >= index:
                aux_dict[key] = self._children.get(key + 1, None)
            else:
                aux_dict[key] = value
        max_index = max(sorted(aux_dict.keys()), default=0)
        del aux_dict[max_index]
        self._children = aux_dict

    def set_child_index(self, child: "Account" | Self, index: int) -> None:
        if index < 0:
            raise ValueError("Parameter 'index' must not be negative.")
        if child not in self.children:
            raise NotFoundError(
                "Parameter 'child' not in this AccountGroup's children."
            )
        self._remove_child(child)
        aux_dict: dict[int, AccountGroup | Account] = {}
        for key, value in self._children.items():
            if key >= index:
                aux_dict[key + 1] = value
            else:
                aux_dict[key] = value
        aux_dict[index] = child
        self._children = aux_dict

    def get_balance(self, currency: Currency) -> CashAmount:
        return sum(
            (child.get_balance(currency) for child in self.children),
            start=CashAmount(0, currency),
        )

    def serialize(self) -> dict[str, Any]:
        index = self.parent.children.index(self) if self.parent is not None else None
        return {
            "datatype": "AccountGroup",
            "path": self.path,
            "index": index,
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any], account_groups: list["AccountGroup"]
    ) -> "AccountGroup":
        path: str = data["path"]
        index: int | None = data["index"]
        parent_path, _, name = path.rpartition("/")
        obj = AccountGroup(name)
        if parent_path != "":
            obj._parent = find_account_group_by_path(parent_path, account_groups)
            obj._parent._children[index] = obj
        return obj
