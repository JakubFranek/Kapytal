# TODO: rename this module

import copy
import operator
from datetime import date
from decimal import Decimal
from functools import total_ordering
from typing import Self

from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin


class CurrencyError(ValueError):
    """Raised when invalid Currency is supplied."""


class NoExchangeRateError(ValueError):
    """Raised when exchange rate is requested but none is available."""


class ConversionFactorNotFoundError(ValueError):
    """Raised when a conversion factor cannot be calculated
    for the given Currency pair."""


class Currency(DatetimeCreatedMixin):
    def __init__(self, code: str, places: int) -> None:
        super().__init__()

        if not isinstance(code, str):
            raise TypeError("Currency.code must be a string.")
        if len(code) != 3 or not code.isalpha():
            raise ValueError("Currency.code must be a three letter ISO-4217 code.")
        self._code = code.upper()

        if not isinstance(places, int):
            raise TypeError("Currency.places must be an integer.")
        if places < 0:
            raise ValueError("Currency.places must not be negative.")
        self._places = places

        self._exchange_rates: dict[Currency, "ExchangeRate"] = {}

    @property
    def code(self) -> str:
        return self._code

    @property
    def places(self) -> int:
        return self._places

    @property
    def convertible_to(self) -> set[Self]:
        return set(self._exchange_rates)

    @property
    def exchange_rates(self) -> dict[Self, "ExchangeRate"]:
        return copy.deepcopy(self._exchange_rates)

    def __repr__(self) -> str:
        return f"Currency({self.code})"

    def __hash__(self) -> int:
        return hash(self._code)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Currency):
            return NotImplemented
        return self._code == __o.code

    def add_exchange_rate(self, exchange_rate: "ExchangeRate") -> None:
        if not isinstance(exchange_rate, ExchangeRate):
            raise TypeError("Parameter 'exchange_rate' must be an ExchangeRate.")
        if (
            exchange_rate.primary_currency != self
            and exchange_rate.secondary_currency != self
        ):
            raise CurrencyError(
                f"Provided ExchangeRate ({exchange_rate}) "
                f"does not relate to this Currency ({self.code})."
            )
        other_currency = exchange_rate.currencies - {self}
        self._exchange_rates[other_currency.pop()] = exchange_rate

    def remove_exchange_rate(self, exchange_rate: "ExchangeRate") -> None:
        if not isinstance(exchange_rate, ExchangeRate):
            raise TypeError("Parameter 'exchange_rate' must be an ExchangeRate.")
        other_currency = exchange_rate.currencies - {self}
        del self._exchange_rates[other_currency.pop()]

    def get_conversion_factor(
        self, target_currency: Self, date_: date | None = None
    ) -> Decimal:
        exchange_rates = Currency._get_exchange_rates(self, target_currency)
        if exchange_rates is None:
            raise ConversionFactorNotFoundError(
                f"No path from {self.code} to {target_currency.code} found."
            )

        factor = Decimal(1)
        current_currency = self
        for exchange_rate in exchange_rates:
            if current_currency == exchange_rate.primary_currency:
                operation = operator.mul
                current_currency = exchange_rate.secondary_currency
            else:
                operation = operator.truediv
                current_currency = exchange_rate.primary_currency
            if date_ is None:
                rate = exchange_rate.latest_rate
            else:
                rate = exchange_rate.rate_history[date_]
            factor = operation(factor, rate)
        return factor

    @staticmethod
    def _get_exchange_rates(
        current_currency: "Currency",
        target_currency: "Currency",
        ignore_currencies: set["Currency"] | None = None,
    ) -> list["ExchangeRate"] | None:
        if ignore_currencies is None:
            ignore_currencies = {current_currency}

        if target_currency in current_currency.convertible_to:
            # Direct ExchangeRate found!
            return [current_currency._exchange_rates[target_currency]]

        # Direct ExchangeRate not found...
        # Get unexplored currencies to iterate over.
        iterable_currencies = [
            currency
            for currency in current_currency.convertible_to
            if currency not in ignore_currencies
        ]
        # Ignore these currencies in future deeper searches (no need to go back).
        ignore_currencies = ignore_currencies | current_currency.convertible_to
        for loop_currency in iterable_currencies:
            exchange_rates = Currency._get_exchange_rates(  # noqa: NEW100
                loop_currency, target_currency, ignore_currencies
            )
            if exchange_rates is None:
                continue  # Reached a dead end.
            # ExchangeRate to target_currency found!
            # Append ExchangeRate needed get there from the current_currency.
            exchange_rates.insert(0, current_currency._exchange_rates[loop_currency])
            return exchange_rates
        return None  # Reached a dead-end.


class ExchangeRate:
    def __init__(
        self, primary_currency: Currency, secondary_currency: Currency
    ) -> None:
        if not isinstance(primary_currency, Currency):
            raise TypeError("ExchangeRate.primary_currency must be a Currency.")
        if not isinstance(secondary_currency, Currency):
            raise TypeError("ExchangeRate.secondary_currency must be a Currency.")
        if primary_currency == secondary_currency:
            raise CurrencyError("ExchangeRate currencies must not be the same.")
        self._primary_currency = primary_currency
        self._secondary_currency = secondary_currency

        self._primary_currency.add_exchange_rate(self)
        self._secondary_currency.add_exchange_rate(self)

        self._rate_history: dict[date, Decimal] = {}

    @property
    def primary_currency(self) -> Currency:
        return self._primary_currency

    @property
    def secondary_currency(self) -> Currency:
        return self._secondary_currency

    @property
    def currencies(self) -> set[Currency]:
        return {self._primary_currency, self._secondary_currency}

    @property
    def rate_history(self) -> dict[date, Decimal]:
        return copy.deepcopy(self._rate_history)

    @property
    def latest_rate(self) -> Decimal:
        if len(self._rate_history) == 0:
            raise NoExchangeRateError("No exchange rate data.")
        latest_date = max(date_ for date_ in self._rate_history)
        return self._rate_history[latest_date]

    def __repr__(self) -> str:
        return (
            "ExchangeRate("
            f"{self._primary_currency.code}/{self._secondary_currency.code})"
        )

    def __str__(self) -> str:
        return f"{self._primary_currency.code}/{self._secondary_currency.code}"

    def set_rate(self, date_: date, rate: Decimal) -> None:
        if not isinstance(date_, date):
            raise TypeError("Parameter 'date_' must be a date.")
        if not isinstance(rate, Decimal):
            raise TypeError("Parameter 'rate' must be a Decimal.")
        if not rate.is_finite() or rate < 0:
            raise ValueError("Parameter 'rate' must be finite and non-negative.")
        self._rate_history[date_] = rate


@total_ordering
class CashAmount:
    """An immutable object comprising of Decimal value and a Currency."""

    def __init__(self, value: Decimal | int | str, currency: Currency) -> None:
        if not isinstance(value, (Decimal, int, str)):
            raise TypeError(
                "CashAmount.value must be a Decimal, integer or a string "
                "containing a number."
            )
        _value = Decimal(value)
        if not _value.is_finite():
            raise ValueError("CashAmount.value must be finite.")
        self._value = _value

        if not isinstance(currency, Currency):
            raise TypeError("CashAmount.currency must be a Currency.")
        self._currency = currency

    @property
    def value(self) -> Decimal:
        return round(self._value, self.currency.places)

    @property
    def currency(self) -> Currency:
        return self._currency

    def __repr__(self) -> str:
        return f"CashAmount({self.value} {self._currency.code})"

    def __str__(self) -> str:
        return f"{self.value} {self._currency.code}"

    def __hash__(self) -> int:
        return hash((self.value, self.currency))

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        if self.currency != __o.currency:
            if self.value == 0 and __o.value == 0:
                return True  # If values are zero, amounts are always equal
            raise CurrencyError("CashAmount.currency of operands must match.")
        return self.value == __o.value

    def __lt__(self, __o: object) -> bool:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        if self.currency != __o.currency:
            raise CurrencyError("CashAmount.currency of operands must match.")
        return self.value < __o.value

    def __neg__(self) -> Self:
        return CashAmount(-self.value, self.currency)

    def __add__(self, __o: object) -> Self:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        if self.currency != __o.currency:
            raise CurrencyError("CashAmount.currency of operands must match.")
        return CashAmount(self.value + __o.value, self.currency)

    def __radd__(self, __o: object) -> Self:
        return self.__add__(__o)

    def __sub__(self, __o: object) -> Self:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        if self.currency != __o.currency:
            raise CurrencyError("CashAmount.currency of operands must match.")
        return CashAmount(self.value - __o.value, self.currency)

    def __rsub__(self, __o: object) -> Self:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        if self.currency != __o.currency:
            raise CurrencyError("CashAmount.currency of operands must match.")
        return CashAmount(__o.value - self.value, self.currency)

    def __mul__(self, __o: object) -> Self:
        if not isinstance(__o, (int, Decimal)):
            return NotImplemented
        return CashAmount(self.value * __o, self.currency)

    def __rmul__(self, __o: object) -> Self:
        return self.__mul__(__o)

    def convert(self, target_currency: Currency, date_: date | None = None) -> Self:
        if target_currency == self.currency:
            return self
        factor = self.currency.get_conversion_factor(target_currency, date_)
        return CashAmount(self.value * factor, target_currency)
