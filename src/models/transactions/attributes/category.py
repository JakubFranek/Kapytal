from typing import Self

from src.models.transactions.attributes.attribute import Attribute


class Category(Attribute):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._parent: Self | None = None
        self._children: list[Self] = []

    @property
    def parent(self) -> Self | None:
        return self._parent

    @parent.setter
    def parent(self, new_parent: Self | None) -> None:
        if new_parent is not None and not isinstance(new_parent, Category):
            raise TypeError("Category parent can only be a Category or a None.")

        if self._parent is not None:
            self._parent._children.remove(self)

        if new_parent is not None:
            new_parent._children.append(self)

        self._parent = new_parent

    @property
    def children(self) -> tuple[Self] | None:
        return tuple(self._children)
