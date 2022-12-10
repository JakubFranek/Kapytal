class NameMixin:
    NAME_MIN_LENGTH = 1
    NAME_MAX_LENGTH = 32

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{self.__class__.__name__}.name must be a string.")

        if not hasattr(self, "_name") or (
            hasattr(self, "_name") and self._name != value
        ):
            if (
                len(value) < NameMixin.NAME_MIN_LENGTH
                or len(value) > NameMixin.NAME_MAX_LENGTH
            ):
                raise ValueError(
                    f"{self.__class__.__name__}.name length must be between "
                    f"{NameMixin.NAME_MIN_LENGTH} and "
                    f"{NameMixin.NAME_MAX_LENGTH} characters."
                )
            self._name = value
