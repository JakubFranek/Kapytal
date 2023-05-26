from typing import Any

from src.models.custom_exceptions import InvalidCharacterError


class NameLengthError(ValueError):
    """Raised when the length of 'name' string is incorrect."""


class NameMixin:
    __slots__ = ()

    NAME_MIN_LENGTH = 1
    NAME_MAX_LENGTH = 32

    def __init__(
        self,
        name: str,
        allow_slash: bool,  # noqa: FBT001
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        super().__init__(*args, **kwargs)

        if not isinstance(allow_slash, bool):
            raise TypeError("Parameter 'allow_slash' must be a boolean.")
        self._allow_slash = allow_slash
        # colons always forbidden, as they are used for Attribute:Amount pairs
        # in JSON de/serialization
        self._allow_colon = False

        self.name = name

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        if not isinstance(name, str):
            raise TypeError(f"{self.__class__.__name__}.name must be a string.")

        if hasattr(self, "_name") and self._name == name:
            return

        if len(name) < self.NAME_MIN_LENGTH or len(name) > self.NAME_MAX_LENGTH:
            raise NameLengthError(
                f"{self.__class__.__name__}.name length must be between "
                f"{self.NAME_MIN_LENGTH} and "
                f"{self.NAME_MAX_LENGTH} characters (currently {len(name)})."
            )
        if not self._allow_slash and "/" in name:
            raise InvalidCharacterError(
                f"Slashes in {self.__class__.__name__}.name are forbidden."
            )
        if not self._allow_colon and ":" in name:
            raise InvalidCharacterError(
                f"Colons in {self.__class__.__name__}.name are forbidden."
            )

        self._name: str = name
