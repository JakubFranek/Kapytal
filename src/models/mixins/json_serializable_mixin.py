from abc import ABC, abstractmethod
from typing import Any


class JSONSerializableMixin(ABC):
    __slots__ = ()

    @abstractmethod
    def serialize(self) -> dict[str, Any]:
        """Serialize object to a JSON compatible dictionary."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def deserialize(data: dict[str, Any]) -> "JSONSerializableMixin":
        """Deserialize object from a JSON compatible dictionary."""
        raise NotImplementedError
