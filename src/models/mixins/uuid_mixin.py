import uuid


class UUIDMixin:
    def __init__(self) -> None:
        super().__init__()
        self._uuid = uuid.uuid4()

    @property
    def uuid(self) -> uuid.UUID:
        return self._uuid
