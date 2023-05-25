import uuid
from typing import Any


class UUIDMixin:
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs)
        self._uuid = uuid.uuid4()

    @property
    def uuid(self) -> uuid.UUID:
        return self._uuid

    def __hash__(self) -> int:
        return hash(self._uuid.int)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, UUIDMixin):
            return self._uuid.int == __o._uuid.int  # noqa: SLF001
        return NotImplemented
