from datetime import datetime
from enum import Enum, auto
from typing import Self

from src.models.constants import tzinfo
from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin
from src.models.mixins.datetime_edited_mixin import DatetimeEditedMixin
from src.models.mixins.name_mixin import NameMixin


class InvalidCategoryError(ValueError):
    """Raised when invalid Category is supplied."""


class InvalidAttributeError(ValueError):
    """Raised when invalid Attribute is supplied."""


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

    def __repr__(self) -> str:
        return f"Attribute('{self.name}', {self.type_.name})"


class Category(NameMixin, DatetimeCreatedMixin, DatetimeEditedMixin):
    def __init__(
        self, name: str, type_: CategoryType, parent: Self | None = None
    ) -> None:
        super().__init__(name)

        if not isinstance(type_, CategoryType):
            raise TypeError("Category.type_ must be a CategoryType.")
        self._type = type_

        self.parent: Self | None = parent
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
                    "The type_ of parent Category must match the type_"
                    " of this Category."
                )

        if hasattr(self, "_parent") and self._parent is not None:
            self._parent._children.remove(self)

        if new_parent is not None:
            new_parent._children.append(self)

        self._parent = new_parent
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def children(self) -> tuple[Self, ...]:
        return tuple(self._children)

    @property
    def type_(self) -> CategoryType:
        return self._type

    def __str__(self) -> str:
        if self.parent is None:
            return self.name
        return str(self.parent) + "/" + self.name

    def __repr__(self) -> str:
        return f"Category('{self.name}', {self.type_.name}, parent={self.parent})"
