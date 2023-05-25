import logging
from typing import TYPE_CHECKING, Any, Self
from uuid import UUID

from src.models.custom_exceptions import NotFoundError

if TYPE_CHECKING:
    from src.models.base_classes.account import Account

from src.models.mixins.get_balance_mixin import BalanceMixin
from src.models.mixins.json_serializable_mixin import JSONSerializableMixin
from src.models.mixins.name_mixin import NameMixin
from src.models.mixins.uuid_mixin import UUIDMixin
from src.models.model_objects.currency_objects import CashAmount, Currency


class AccountGroup(NameMixin, BalanceMixin, JSONSerializableMixin, UUIDMixin):
    def __init__(self, name: str, parent: Self | None = None) -> None:
        super().__init__(name=name, allow_slash=False)
        self.parent = parent
        self._children_dict: dict[int, Self | Account] = {}
        self._children_tuple: tuple[Self | Account, ...] = ()

    @property
    def parent(self) -> Self | None:
        return self._parent

    @parent.setter
    def parent(self, parent: Self | None) -> None:
        if parent is not None and not isinstance(parent, AccountGroup):
            raise TypeError("AccountGroup.parent must be an AccountGroup or a None.")

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
    def children(self) -> tuple["Account" | Self, ...]:
        return self._children_tuple

    @property
    def path(self) -> str:
        if self._parent is None:
            return self._name
        return self._parent.path + "/" + self._name

    def __repr__(self) -> str:
        return f"AccountGroup('{self.path}')"

    def _update_children_tuple(self) -> None:
        self._children_tuple = tuple(
            self._children_dict[key] for key in sorted(self._children_dict.keys())
        )

    def _add_child(self, child: Self | "Account") -> None:
        max_index = max(sorted(self._children_dict.keys()), default=-1)
        self._children_dict[max_index + 1] = child
        self._update_children_tuple()
        child.event_balance_updated.append(self._update_balances)

    def _remove_child(self, child: Self | "Account") -> None:
        index = self.get_child_index(child)
        aux_dict: dict[int, AccountGroup | Account] = {}
        for key, value in self._children_dict.items():
            if key >= index:
                aux_dict[key] = self._children_dict.get(key + 1, None)
            else:
                aux_dict[key] = value
        max_index = max(sorted(aux_dict.keys()), default=0)
        del aux_dict[max_index]
        self._children_dict = aux_dict
        self._update_children_tuple()
        child.event_balance_updated.remove(self._update_balances)

    def set_child_index(self, child: "Account" | Self, index: int) -> None:
        if index < 0:
            raise ValueError("Parameter 'index' must not be negative.")
        if child not in self._children_tuple:
            raise NotFoundError(
                "Parameter 'child' not in this AccountGroup's children."
            )

        current_index = self.get_child_index(child)
        if current_index == index:
            return

        self._remove_child(child)
        aux_dict: dict[int, AccountGroup | Account] = {}
        for key, value in self._children_dict.items():
            if key >= index:
                aux_dict[key + 1] = value
            else:
                aux_dict[key] = value
        aux_dict[index] = child
        self._children_dict = aux_dict
        self._update_children_tuple()
        logging.info(f"Changing index from {current_index} to {index}")

    def get_child_index(self, child: "Account" | Self) -> int:
        return list(self._children_dict.keys())[
            list(self._children_dict.values()).index(child)
        ]

    def get_balance(self, currency: Currency) -> CashAmount:
        total = currency.zero_amount
        for balance in self._balances:
            total += balance.convert(currency)
        return total

    def _update_balances(self) -> None:
        balances: dict[Currency, CashAmount] = {}
        for child in self._children_tuple:
            for balance in child.balances:
                if balance.currency in balances:
                    balances[balance.currency] += balance
                else:
                    balances[balance.currency] = balance
        self._balances = tuple(balances.values())
        self.event_balance_updated()

    def serialize(self) -> dict[str, Any]:
        index = self.parent.get_child_index(self) if self.parent is not None else None
        return {
            "datatype": "AccountGroup",
            "path": self.path,
            "index": index,
            "uuid": str(self.uuid),
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any], account_groups: dict[str, "AccountGroup"]
    ) -> "AccountGroup":
        path: str = data["path"]
        index: int | None = data["index"]
        parent_path, _, name = path.rpartition("/")
        obj = AccountGroup(name)
        obj._uuid = UUID(data["uuid"])  # noqa: SLF001
        if parent_path:
            obj._parent = account_groups[parent_path]  # noqa: SLF001
            obj._parent._children_dict[index] = obj  # noqa: SLF001
            obj._parent._update_children_tuple()  # noqa: SLF001
            obj.event_balance_updated.append(
                obj._parent._update_balances  # noqa: SLF001
            )
        return obj
