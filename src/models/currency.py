from datetime import datetime

from src.models.constants import tzinfo


class Currency:
    def __init__(self, code: str) -> None:
        if not isinstance(code, str):
            raise TypeError("Currency code must be a string.")

        if len(code) != 3 or not code.isalpha():
            raise ValueError("Currency code must be a three letter ISO-4217 code.")

        self._code = code.upper()
        self._date_created = datetime.now(tzinfo)

    @property
    def code(self) -> str:
        return self._code

    @property
    def date_created(self) -> datetime:
        return self._date_created
