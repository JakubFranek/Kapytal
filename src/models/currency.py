class Currency:
    def __init__(self, code: str) -> None:
        self.code = code

    @property
    def code(self) -> str:
        return self._name

    @code.setter
    def code(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Currency name must be a string.")
        elif len(value) != 3:
            raise ValueError("Currency name must be a three character ISO-4217 code.")
        else:
            self._name = value
