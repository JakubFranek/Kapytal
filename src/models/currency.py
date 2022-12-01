from datetime import datetime

from src.models.constants import tzinfo


class Currency:
    def __init__(self, code: str) -> None:
        self.code = code
        self._date_created = datetime.now(tzinfo)

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Currency code must be a string.")

        if len(value) != 3 or not value.isalpha():
            raise ValueError("Currency code must be a three letter ISO-4217 code.")

        self._code = value.upper()

    @property
    def date_created(self) -> datetime:
        return self._date_created
