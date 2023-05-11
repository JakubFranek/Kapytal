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
        return hash(self._uuid)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, UUIDMixin):
            return NotImplemented
        return self._uuid == __o._uuid  # noqa: SLF001
