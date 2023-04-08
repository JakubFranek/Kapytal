from enum import Enum
from typing import Any


class FilterMode(Enum):
    OFF = "Keep all transactions (filter is disabled)"
    KEEP = "Keep transactions matching the filter criteria"
    DISCARD = "Discard transactions matching the filter criteria"


class FilterModeMixin:
    def __init__(
        self, mode: FilterMode, *args: Any, **kwargs: Any  # noqa: ANN401
    ) -> None:
        super().__init__(*args, **kwargs)
        if not isinstance(mode, FilterMode):
            raise TypeError("Parameter 'mode' must be a FilterMode.")
        self._mode = mode

    @property
    def mode(self) -> FilterMode:
        return self._mode
