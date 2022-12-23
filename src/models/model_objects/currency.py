import copy
import operator
from datetime import date
from decimal import Decimal
from functools import total_ordering
from typing import Self

from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin


class CurrencyError(ValueError):
    """Raised when invalid Currency is supplied."""


# TODO: add CurrencyExchangeRate objects or something? (w/ history)
# TODO: add no. of decimal places per Currency?
class Currency(DatetimeCreatedMixin):
    def __init__(self, code: str) -> None:
        if not isinstance(code, str):
            raise TypeError("Currency.code must be a string.")

        if len(code) != 3 or not code.isalpha():
            raise ValueError("Currency.code must be a three letter ISO-4217 code.")

        super().__init__()
        self._code = code.upper()
        self._exchange_rates: dict[Currency, "ExchangeRate"] = {}

    @property
    def code(self) -> str:
        return self._code

    @property
    def convertible_currencies(self) -> set[Self]:
        return set([currency for currency in self._exchange_rates])

    def __repr__(self) -> str:
        return f"Currency('{self.code}')"

    def __hash__(self) -> int:
        return hash(self._code)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Currency):
            return NotImplemented
        return self._code == __o.code

    def add_exchange_rate(self, exchange_rate: "ExchangeRate") -> None:
        if not isinstance(exchange_rate, ExchangeRate):
            raise TypeError("Argument 'exchange_rate' must be an ExchangeRate.")
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
            raise TypeError("Argument 'exchange_rate' must be an ExchangeRate.")
        other_currency = exchange_rate.currencies - {self}
        del self._exchange_rates[other_currency.pop()]

    def get_exchange_rate(self, currency: Self) -> "ExchangeRate":
        if not isinstance(currency, Currency):
            raise TypeError("Currency.get_exchange_rate() argument must be a Currency.")
        return self._exchange_rates[currency]


class ExchangeRate:
    def __init__(
        self, primary_currency: Currency, secondary_currency: Currency
    ) -> None:
        if not isinstance(primary_currency, Currency):
            raise TypeError("ExchangeRate.primary_currency must be a Currency.")
        if not isinstance(secondary_currency, Currency):
            raise TypeError("ExchangeRate.secondary_currency must be a Currency.")
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
            return Decimal(0)
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
            raise TypeError("Argument 'date_' must be a date.")
        if not isinstance(rate, Decimal):
            raise TypeError("Argument 'rate' must be a Decimal.")
        if not rate.is_finite() or rate < 0:
            raise ValueError("Argument 'rate' must be finite and non-negative.")
        self._rate_history[date_] = rate


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
        if self.currency != __o.currency:
            if self.value == 0 and __o.value == 0:
                # If values are zero, amounts are equal regardless of currency
                return True
            return NotImplemented
        return self.value == __o.value

    def __lt__(self, __o: object) -> bool:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        if self.currency != __o.currency:
            return NotImplemented
        return self.value < __o.value

    def convert(self, target_currency: Currency, date_: date | None = None) -> Self:
        exchange_rates = self._get_exchange_rates(self.currency, target_currency, set())
        if len(exchange_rates) == 0:
            raise ValueError("No way to convert CashAmount to target_currency found.")
        amount = self
        for exchange_rate in exchange_rates:
            amount = amount._convert(exchange_rate, date_)
        return amount

    # TODO: this should probably be in Currency
    # and return a number of some sorts?
    def _get_exchange_rates(
        self,
        current_currency: Currency,
        target_currency: Currency,
        ignore_currencies: set[Currency],
    ) -> list[ExchangeRate]:
        if len(ignore_currencies) == 0:
            ignore_currencies = {current_currency}

        if target_currency in current_currency.convertible_currencies:
            # Direct ExchangeRate found!
            return [current_currency.get_exchange_rate(target_currency)]

        # Direct ExchangeRate not found...
        # Get unexplored currencies to iterate over.
        iterable_currencies = [
            currency
            for currency in current_currency.convertible_currencies
            if currency not in ignore_currencies
        ]
        # Ignore these currencies in future deeper searches (no need to go back).
        ignore_currencies = ignore_currencies | current_currency.convertible_currencies
        for currency in iterable_currencies:
            exchange_rates = self._get_exchange_rates(
                currency, target_currency, ignore_currencies
            )
            if exchange_rates is None:
                continue  # Reached a dead end.
            # ExchangeRate to target_currency found!
            # Append ExchangeRate to get there from current_currency.
            exchange_rates.insert(0, current_currency.get_exchange_rate(currency))
            return exchange_rates
        return None  # Reached a dead-end.

    def _convert(self, exchange_rate: ExchangeRate, date_: date | None = None) -> Self:
        if self.currency == exchange_rate.primary_currency:
            operation = operator.mul
            new_currency = exchange_rate.secondary_currency
        else:
            operation = operator.truediv
            new_currency = exchange_rate.primary_currency

        if date_ is None:
            rate = exchange_rate.latest_rate
        else:
            rate = exchange_rate.rate_history[date_]

        return CashAmount(operation(self.value, rate), new_currency)
