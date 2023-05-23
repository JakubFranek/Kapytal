import logging
from enum import Enum, auto
from typing import Any, Self

from src.models.custom_exceptions import NotFoundError
from src.models.mixins.json_serializable_mixin import JSONSerializableMixin
from src.models.mixins.name_mixin import NameMixin


class InvalidAttributeError(ValueError):
    """Raised when invalid Attribute is supplied."""


class InvalidCategoryError(ValueError):
    """Raised when invalid Category is supplied."""


class InvalidCategoryTypeError(ValueError):
    """Raised when Category.type_ is incompatible with given CashTransaction.type_."""


class AttributeType(Enum):
    TAG = auto()
    PAYEE = auto()


class CategoryType(Enum):
    INCOME = "Income"
    EXPENSE = "Expense"
    INCOME_AND_EXPENSE = "Income and Expense"


class Attribute(NameMixin, JSONSerializableMixin):
    def __init__(self, name: str, type_: AttributeType) -> None:
        super().__init__(name=name, allow_slash=True)

        if not isinstance(type_, AttributeType):
            raise TypeError("Attribute.type_ must be an AttributeType.")
        logging.info(f"Setting type_ to {type_.name}")
        self._type = type_

    @property
    def type_(self) -> AttributeType:
        return self._type

    def __repr__(self) -> str:
        return f"Attribute('{self._name}', {self._type.name})"

    def __str__(self) -> str:
        return self._name

    def serialize(self) -> dict[str, Any]:
        return {"datatype": "Attribute", "name": self._name, "type": self._type.name}

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Self:
        name = data["name"]
        type_ = AttributeType[data["type"]]
        return Attribute(name, type_)


class Category(NameMixin, JSONSerializableMixin):
    def __init__(
        self, name: str, type_: CategoryType, parent: Self | None = None
    ) -> None:
        super().__init__(name, allow_slash=False)

        if not isinstance(type_, CategoryType):
            raise TypeError("Category.type_ must be a CategoryType.")
        logging.info(f"Setting type_ to {type_.name}")
        self._type = type_

        self.parent = parent
        self._children_dict: dict[int, Self] = {}
        self._children_tuple: tuple[Self, ...] = ()

    @property
    def parent(self) -> Self | None:
        return self._parent

    @parent.setter
    def parent(self, parent: Self | None) -> None:
        if parent is not None:
            if not isinstance(parent, Category):
                raise TypeError("Category.parent must be a Category or a None.")
            if parent.type_ != self.type_:
                raise ValueError(
                    "The type_ of parent Category must match the type_ "
                    "of this Category."
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
    def children(self) -> tuple[Self, ...]:
        return self._children_tuple

    @property
    def type_(self) -> CategoryType:
        return self._type

    @property
    def path(self) -> str:
        if self._parent is None:
            return self._name
        return self._parent.path + "/" + self._name

    @property
    def ancestors(self) -> frozenset[Self]:
        ancestors = set()
        node = self._parent
        while node is not None:
            ancestors.add(node)
            node = node._parent  # noqa: SLF001
        return frozenset(ancestors)

    @property
    def descendants(self) -> frozenset[Self]:
        if not self._children_tuple:
            return frozenset()
        descendants = set(self._children_tuple)
        for child in self._children_tuple:
            descendants |= child.descendants
        return frozenset(descendants)

    def __repr__(self) -> str:
        return f"Category('{self.path}', {self._type.name})"

    def is_ancestor_of(self, category: Self) -> bool:
        """Check if this Category is an ancestor of the parameter Category.
        Seems to be slower than checking if category is in self.descendants."""

        if category in self._children_tuple or category.parent in self._children_tuple:
            return True
        if len(self._children_tuple) == 0 or self == category:
            return False
        for child in self._children_tuple:  # noqa: SIM110
            if child.is_ancestor_of(category):
                return True
        return False

    def is_descendant_of(self, category: Self) -> bool:
        """Check if this Category is a descendant of the parameter Category."""
        if self._parent == category:
            return True
        if self._parent is None:
            return False
        return self._parent.is_descendant_of(category)

    def _update_children_tuple(self) -> None:
        self._children_tuple = tuple(
            self._children_dict[key] for key in sorted(self._children_dict.keys())
        )

    def _add_child(self, child: Self) -> None:
        max_index = max(sorted(self._children_dict.keys()), default=-1)
        self._children_dict[max_index + 1] = child
        self._update_children_tuple()

    def _remove_child(self, child: Self) -> None:
        index = self.get_child_index(child)
        aux_dict: dict[int, Self] = {}
        for key, value in self._children_dict.items():
            if key >= index:
                aux_dict[key] = self._children_dict.get(key + 1, None)
            else:
                aux_dict[key] = value
        max_index = max(sorted(aux_dict.keys()), default=0)
        del aux_dict[max_index]
        self._children_dict = aux_dict
        self._update_children_tuple()

    def set_child_index(self, child: Self, index: int) -> None:
        if index < 0:
            raise ValueError("Parameter 'index' must not be negative.")
        if child not in self._children_tuple:
            raise NotFoundError("Parameter 'child' not in this Category's children.")

        current_index = self.get_child_index(child)
        if current_index == index:
            return

        self._remove_child(child)
        aux_dict: dict[int, Self] = {}
        for key, value in self._children_dict.items():
            if key >= index:
                aux_dict[key + 1] = value
            else:
                aux_dict[key] = value
        aux_dict[index] = child
        self._children_dict = aux_dict
        self._update_children_tuple()
        logging.info(f"Changing index from {current_index} to {index}")

    def get_child_index(self, child: Self) -> int:
        return list(self._children_dict.keys())[
            list(self._children_dict.values()).index(child)
        ]

    def serialize(self) -> dict[str, Any]:
        index = self._parent.get_child_index(self) if self._parent is not None else None
        return {
            "datatype": "Category",
            "path": self.path,
            "type": self._type.name,
            "index": index,
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any], categories: dict[str, "Category"]
    ) -> "Category":
        path: str = data["path"]
        parent_path, _, name = path.rpartition("/")
        type_ = CategoryType[data["type"]]
        index: int | None = data["index"]
        obj = Category(name, type_)
        if parent_path:
            obj._parent = categories[parent_path]  # noqa: SLF001
            obj._parent._children_dict[index] = obj  # noqa: SLF001
            obj._parent._update_children_tuple()  # noqa: SLF001
        return obj
