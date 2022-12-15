from datetime import datetime
from enum import Enum, auto
from typing import Self

from src.models.constants import tzinfo
from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin
from src.models.mixins.datetime_edited_mixin import DatetimeEditedMixin
from src.models.mixins.name_mixin import NameMixin


class AttributeType(Enum):
    TAG = auto()
    PAYEE = auto()


class CategoryType(Enum):
    INCOME = auto()
    EXPENSE = auto()
    INCOME_AND_EXPENSE = auto()


class Attribute(NameMixin, DatetimeCreatedMixin):
    def __init__(self, name: str, type_: AttributeType) -> None:
        super().__init__(name=name)

        if not isinstance(type_, AttributeType):
            raise TypeError("Attribute.type_ must be an AttributeType.")

        self._type = type_

    @property
    def type_(self) -> AttributeType:
        return self._type


class Category(NameMixin, DatetimeCreatedMixin, DatetimeEditedMixin):
    def __init__(self, name: str, type_: CategoryType) -> None:
        super().__init__(name)
        self._parent: Self | None = None
        self._children: list[Self] = []

        if not isinstance(type_, CategoryType):
            raise TypeError("Category.type_ must be a CategoryType.")
        self._type = type_

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
                    "The type_ of new_parent must match the type_ of this Category."
                )

        if self._parent is not None:
            self._parent._children.remove(self)

        if new_parent is not None:
            new_parent._children.append(self)

        self._parent = new_parent
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def children(self) -> tuple[Self]:
        return tuple(self._children)

    @property
    def type_(self) -> CategoryType:
        return self._type

    def __str__(self) -> str:
        if self.parent is None:
            return self.name
        return str(self.parent) + "/" + self.name
