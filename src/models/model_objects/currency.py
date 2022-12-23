from decimal import Decimal
from functools import total_ordering

from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin


class CurrencyError(ValueError):
    """Raised when invalid Currency is supplied."""


# TODO: add CurrencyExchangeRate objects or something? (w/ history)
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

    def __repr__(self) -> str:
        return f"Currency('{self.code}')"


@total_ordering
class CashAmount:
    """An immutable object comprising of Decimal value and a Currency."""

    def __init__(self, value: Decimal, currency: Currency) -> None:
        if not isinstance(value, Decimal):
            raise TypeError("CashAmount.value must be a Decimal.")
        if not value.is_finite() or value < 0:
            raise ValueError("CashAmount.value must be finite and non-negative.")
        self._value = value
        if not isinstance(currency, Currency):
            raise TypeError("CashAmount.currency must be a Currency.")
        self._currency = currency

    @property
    def value(self) -> Decimal:
        return self._value

    @property
    def currency(self) -> Currency:
        return self._currency

    def __repr__(self) -> str:
        return f"CashAmount({self._value} {self._currency.code})"

    def __str__(self) -> str:
        return f"{self._value} {self._currency.code}"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        return self.currency == __o.currency and self.value == __o.value

    def __lt__(self, __o: object) -> bool:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        if self.currency != __o.currency:
            return NotImplemented
        return self.value < __o.value
