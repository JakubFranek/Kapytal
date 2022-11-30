from src.models.currency import Currency


class Account:
    NAME_MIN_LENGTH = 1
    NAME_MAX_LENGTH = 32

    def __init__(self, name: str, currency: Currency) -> None:
        self.name = name
        self.currency = currency

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Account name must be a string.")
        elif (
            len(value) < Account.NAME_MIN_LENGTH or len(value) > Account.NAME_MAX_LENGTH
        ):
            raise ValueError(
                f"""Account name length must be between {Account.NAME_MIN_LENGTH} 
                and {Account.NAME_MAX_LENGTH} characters."""
            )
        else:
            self._name = value
