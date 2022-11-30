class Currency:
    def __init__(self, code: str) -> None:
        self.code = code

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Currency code must be a string.")
        elif len(value) != 3 or not value.isalpha():
            raise ValueError("Currency code must be a three letter ISO-4217 code.")
        else:
            self._code = value.upper()
