import copy
from typing import Any, Self


class CopyableMixin:
    __slots__ = ()

    def __copy__(self) -> Self:
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo: dict[int, Any]) -> Self:
        cls = type(self)
        result = cls.__new__(cls)
        memo[id(self)] = result
        if hasattr(self, "__slots__"):
            for name in self.__slots__:
                setattr(result, name, copy.deepcopy(getattr(self, name), memo))
        if hasattr(self, "__dict__"):
            for key, value in self.__dict__.items():
                setattr(result, key, copy.deepcopy(value, memo))
        return result
