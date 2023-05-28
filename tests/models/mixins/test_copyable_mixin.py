import copy
from dataclasses import dataclass

from src.models.mixins.copyable_mixin import CopyableMixin


@dataclass
class Data:
    value: int


class ConcreteCopyableMixin(CopyableMixin):
    def __init__(self) -> None:
        super().__init__()
        self.immutable = Data(1)
        self.mutable = [Data(1)]


class ConcreteCopyableMixinWithSlots(CopyableMixin):
    __slots__ = ("immutable", "mutable")

    def __init__(self) -> None:
        super().__init__()
        self.immutable = Data(1)
        self.mutable = [Data(1)]


def test_copy() -> None:
    concrete_obj = ConcreteCopyableMixin()
    concrete_copy = copy.copy(concrete_obj)
    assert concrete_obj.immutable == concrete_copy.immutable
    assert concrete_obj.mutable == concrete_copy.mutable
    assert concrete_obj.mutable is concrete_copy.mutable


def test_deep_copy() -> None:
    concrete_obj = ConcreteCopyableMixin()
    concrete_copy = copy.deepcopy(concrete_obj)
    assert concrete_obj.immutable == concrete_copy.immutable
    assert concrete_obj.mutable == concrete_copy.mutable
    assert concrete_obj.mutable is not concrete_copy.mutable


def test_copy_slots() -> None:
    concrete_obj = ConcreteCopyableMixinWithSlots()
    concrete_copy = copy.copy(concrete_obj)
    assert concrete_obj.immutable == concrete_copy.immutable
    assert concrete_obj.mutable == concrete_copy.mutable
    assert concrete_obj.mutable is concrete_copy.mutable


def test_deep_copy_slots() -> None:
    concrete_obj = ConcreteCopyableMixinWithSlots()
    concrete_copy = copy.deepcopy(concrete_obj)
    assert concrete_obj.immutable == concrete_copy.immutable
    assert concrete_obj.mutable == concrete_copy.mutable
    assert concrete_obj.mutable is not concrete_copy.mutable
