from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin


class Currency(DatetimeCreatedMixin):
    def __init__(self, code: str) -> None:
        if not isinstance(code, str):
            raise TypeError("Currency.code must be a string.")

        if len(code) != 3 or not code.isalpha():
            raise ValueError("Currency.code must be a three letter ISO-4217 code.")

        super().__init__()
        self._code = code.upper()

    @property
    def code(self) -> str:
        return self._code
