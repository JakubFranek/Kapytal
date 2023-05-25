from typing import Any
from uuid import UUID, uuid4


class UUIDMixin:
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs)
        self._uuid = uuid4()

    @property
    def uuid(self) -> UUID:
        return self._uuid

    def __hash__(self) -> int:
        return hash(self._uuid.int)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, UUIDMixin):
            return self._uuid.int == __o._uuid.int  # noqa: SLF001
        return NotImplemented
