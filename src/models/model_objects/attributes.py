from enum import Enum, auto
from typing import Self

from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin
from src.models.mixins.name_mixin import NameMixin


class Attribute(NameMixin, DatetimeCreatedMixin):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)


class CategoryType(Enum):
    INCOME = auto()
    EXPENSE = auto()
    INCOME_AND_EXPENSE = auto()


class Category(Attribute):
    def __init__(self, name: str, category_type: CategoryType) -> None:
        super().__init__(name)
        self._parent: Self | None = None
        self._children: list[Self] = []
        self.type_ = category_type

    @property
    def parent(self) -> Self | None:
        return self._parent

    @parent.setter
    def parent(self, new_parent: Self | None) -> None:
        if new_parent is not None and not isinstance(new_parent, Category):
            raise TypeError("Category.parent can only be a Category or a None.")

        if self._parent is not None:
            self._parent._children.remove(self)

        if new_parent is not None:
            new_parent._children.append(self)

        self._parent = new_parent

    @property
    def children(self) -> tuple[Self] | None:
        return tuple(self._children)

    @property
    def type_(self) -> CategoryType:
        return self._type

    @type_.setter
    def type_(self, value: CategoryType) -> None:
        if not isinstance(value, CategoryType):
            raise TypeError("Category.type_ must be a CategoryType.")

        self._type = value
