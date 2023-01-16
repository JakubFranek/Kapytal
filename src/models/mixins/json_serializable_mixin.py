from abc import ABC, abstractmethod
from typing import Any, Self


class JSONSerializableMixin(ABC):
    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def from_dict(data: dict[str, Any]) -> Self:
        raise NotImplementedError
