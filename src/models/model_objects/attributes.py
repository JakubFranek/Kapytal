from enum import Enum, auto
from typing import Any, Self

from src.models.mixins.json_serializable_mixin import JSONSerializableMixin
from src.models.mixins.name_mixin import NameMixin
from src.models.utilities.find_helpers import find_category_by_path


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
    INCOME = auto()
    EXPENSE = auto()
    INCOME_AND_EXPENSE = auto()


class Attribute(NameMixin, JSONSerializableMixin):
    def __init__(self, name: str, type_: AttributeType) -> None:
        super().__init__(name=name)

        if not isinstance(type_, AttributeType):
            raise TypeError("Attribute.type_ must be an AttributeType.")

        self._type = type_

    @property
    def type_(self) -> AttributeType:
        return self._type

    def __repr__(self) -> str:
        return f"Attribute('{self.name}', {self.type_.name})"

    def serialize(self) -> dict[str, Any]:
        return {"datatype": "Attribute", "name": self._name, "type_": self._type.name}

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Self:
        name = data["name"]
        type_ = AttributeType[data["type_"]]
        return Attribute(name, type_)


class Category(NameMixin, JSONSerializableMixin):
    def __init__(
        self, name: str, type_: CategoryType, parent: Self | None = None
    ) -> None:
        super().__init__(name)

        if not isinstance(type_, CategoryType):
            raise TypeError("Category.type_ must be a CategoryType.")
        self._type = type_

        self.parent = parent
        self._children: list[Self] = []

    @property
    def parent(self) -> Self | None:
        return self._parent

    @parent.setter
    def parent(self, new_parent: Self | None) -> None:
        if new_parent is not None:
            if not isinstance(new_parent, Category):
                raise TypeError("Category.parent must be a Category or a None.")
            if new_parent.type_ != self.type_:
                raise ValueError(
                    "The type_ of parent Category must match the type_ "
                    "of this Category."
                )

        if hasattr(self, "_parent") and self._parent is not None:
            self._parent._children.remove(self)

        if new_parent is not None:
            new_parent._children.append(self)

        self._parent = new_parent

    @property
    def children(self) -> tuple[Self, ...]:
        return tuple(self._children)

    @property
    def type_(self) -> CategoryType:
        return self._type

    @property
    def path(self) -> str:
        if self.parent is None:
            return self.name
        return self.parent.path + "/" + self.name

    def __repr__(self) -> str:
        return f"Category(path='{self.path}', {self.type_.name})"

    def serialize(self) -> dict[str, Any]:
        return {
            "datatype": "Category",
            "path": self.path,
            "type_": self._type.name,
        }

    @staticmethod
    def deserialize(data: dict[str, Any], categories: list["Category"]) -> "Category":
        path: str = data["path"]
        parent_path, _, name = path.rpartition("/")
        type_ = CategoryType[data["type_"]]
        obj = Category(name, type_)
        if parent_path != "":
            obj.parent = find_category_by_path(parent_path, categories)
        return obj
