import logging
import operator
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from functools import total_ordering
from typing import Any, Self

from src.models.mixins.copyable_mixin import CopyableMixin
from src.models.mixins.json_serializable_mixin import JSONSerializableMixin
from src.models.user_settings import user_settings

quantizers: dict[int, Decimal] = {}
for i in range(0, 12):
    quantizers[i] = Decimal(f"1e-{i}")


class CurrencyError(ValueError):
    """Raised when invalid Currency is supplied."""


class ConversionFactorNotFoundError(ValueError):
    """Raised when a conversion factor cannot be calculated
    for the given Currency pair."""


class Currency(CopyableMixin, JSONSerializableMixin):
    __slots__ = ("_code", "_places", "_exchange_rates", "_factor_cache", "_zero_amount")
    CODE_LENGTH = 3

    def __init__(self, code: str, places: int) -> None:
        super().__init__()

        if not isinstance(code, str):
            raise TypeError("Currency.code must be a string.")
        if len(code) != Currency.CODE_LENGTH or not code.isalpha():
            raise ValueError("Currency.code must be a three letter ISO-4217 code.")
        self._code = code.upper()

        if not isinstance(places, int):
            raise TypeError("Currency.places must be an integer.")
        if places < 0:
            raise ValueError("Currency.places must not be negative.")
        self._places = places

        self._exchange_rates: dict[Currency, "ExchangeRate"] = {}
        self._factor_cache: dict[str, Decimal] = {}
        self._zero_amount: CashAmount = CashAmount(0, self)

    @property
    def code(self) -> str:
        return self._code

    @property
    def places(self) -> int:
        return self._places

    @property
    def zero_amount(self) -> "CashAmount":
        return self._zero_amount

    @property
    def convertible_to(self) -> set[Self]:
        return set(self._exchange_rates)

    @property
    def exchange_rates(self) -> dict[Self, "ExchangeRate"]:
        return self._exchange_rates

    def __repr__(self) -> str:
        return f"Currency({self._code})"

    def __str__(self) -> str:
        return self._code

    def __hash__(self) -> int:
        return hash(self._code)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Currency):
            return NotImplemented
        return self._code == __o._code  # noqa: SLF001

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
        self.reset_cache()

    def remove_exchange_rate(self, exchange_rate: "ExchangeRate") -> None:
        if not isinstance(exchange_rate, ExchangeRate):
            raise TypeError("Parameter 'exchange_rate' must be an ExchangeRate.")
        other_currency = exchange_rate.currencies - {self}
        del self._exchange_rates[other_currency.pop()]
        self.reset_cache()

    def reset_cache(self) -> None:
        self._factor_cache = {}

    def get_conversion_factor(
        self, target_currency: Self, date_: date | None = None
    ) -> Decimal:
        cache_key = f"{self._code}/{target_currency.code}"
        # try to get conversion factor from cache
        if date_ is None:
            factor = self._factor_cache.get(cache_key)
            if factor is not None:
                return factor
            reversed_cache_key = f"{target_currency.code}/{self._code}"
            factor = target_currency._factor_cache.get(  # noqa: SLF001
                reversed_cache_key
            )
            if factor is not None:
                return 1 / factor

        exchange_rates = Currency._get_exchange_rates(  # noqa: SLF001
            self, target_currency
        )
        if exchange_rates is None:
            logging.warning(
                f"No path from {self._code} to {target_currency.code} found."
            )
            raise ConversionFactorNotFoundError(
                f"No path from {self._code} to {target_currency.code} found."
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
        self._factor_cache[cache_key] = factor
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
            return [current_currency.exchange_rates[target_currency]]

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
            exchange_rates = Currency._get_exchange_rates(  # noqa: SLF001
                loop_currency, target_currency, ignore_currencies
            )
            if exchange_rates is None:
                continue  # Reached a dead end.
            # ExchangeRate to target_currency found!
            # Append ExchangeRate needed to get there from the current_currency.
            exchange_rates.insert(0, current_currency.exchange_rates[loop_currency])
            return exchange_rates
        return None  # Reached a dead-end.

    def serialize(self) -> dict:
        return {"datatype": "Currency", "code": self._code, "places": self._places}

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Currency":
        return Currency(code=data["code"], places=data["places"])


class ExchangeRate(CopyableMixin, JSONSerializableMixin):
    __slots__ = (
        "_primary_currency",
        "_secondary_currency",
        "_rate_history",
        "_latest_rate",
        "_latest_date",
    )

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
        return self._rate_history

    @property
    def rate_history_pairs(self) -> tuple[tuple[date, Decimal]]:
        pairs = [(date_, rate) for date_, rate in self._rate_history.items()]
        pairs.sort()
        return tuple(pairs)

    @property
    def latest_rate(self) -> Decimal:
        if len(self._rate_history) == 0:
            return Decimal("NaN")
        return self._latest_rate

    @property
    def latest_date(self) -> date | None:
        if len(self._rate_history) == 0:
            return None
        return self._latest_date

    def __repr__(self) -> str:
        return (
            "ExchangeRate("
            f"{self._primary_currency.code}/{self._secondary_currency.code})"
        )

    def __str__(self) -> str:
        return f"{self._primary_currency.code}/{self._secondary_currency.code}"

    def set_rate(self, date_: date, rate: Decimal | int | str) -> None:
        if not isinstance(date_, date):
            raise TypeError("Parameter 'date_' must be a date.")
        if not isinstance(rate, Decimal | int | str):
            raise TypeError(
                "Parameter 'rate' must be a Decimal, integer or a string "
                "containing a number."
            )
        _rate = Decimal(rate)
        if not _rate.is_finite() or _rate <= 0:
            raise ValueError("Parameter 'rate' must be finite and positive.")
        self._rate_history[date_] = _rate.normalize()
        self._latest_date = max(date_ for date_ in self._rate_history)
        self._latest_rate = self._rate_history[self._latest_date]
        self.primary_currency.reset_cache()
        self.secondary_currency.reset_cache()

    # TODO: implement this in User Interface
    def delete_rate(self, date_: date) -> None:
        del self._rate_history[date_]

    def prepare_for_deletion(self) -> None:
        self.primary_currency.remove_exchange_rate(self)
        self.primary_currency.reset_cache()
        self.secondary_currency.remove_exchange_rate(self)
        self.secondary_currency.reset_cache()

    def serialize(self) -> dict:
        date_rate_pairs = [
            [date_.strftime("%Y-%m-%d"), str(rate.normalize())]
            for date_, rate in self.rate_history_pairs
        ]
        return {
            "datatype": "ExchangeRate",
            "primary_currency_code": self._primary_currency.code,
            "secondary_currency_code": self._secondary_currency.code,
            "date_rate_pairs": date_rate_pairs,
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any], currencies: dict[str, Currency]
    ) -> "ExchangeRate":
        primary_code = data["primary_currency_code"]
        secondary_code = data["secondary_currency_code"]
        date_rate_pairs: list[list[str, str]] = data["date_rate_pairs"]

        primary = currencies[primary_code]
        secondary = currencies[secondary_code]

        obj = ExchangeRate(primary, secondary)
        for date_, rate in date_rate_pairs:
            obj.set_rate(
                datetime.strptime(date_, "%Y-%m-%d")
                .replace(tzinfo=user_settings.settings.time_zone)
                .date(),
                rate,
            )

        return obj


@total_ordering
class CashAmount(CopyableMixin, JSONSerializableMixin):
    """An immutable object comprising of Decimal value and a Currency."""

    __slots__ = (
        "_raw_value",
        "_currency",
        "_value_rounded",
        "_value_normalized",
        "_str_rounded",
        "_str_normalized",
    )

    def __init__(self, value: Decimal | int | str, currency: Currency) -> None:
        if isinstance(value, float):
            raise TypeError(
                "CashAmount.value must be a Decimal, integer or a string "
                "containing a number."
            )
        try:
            self._raw_value = Decimal(value)
        except (TypeError, InvalidOperation, ValueError) as exc:
            raise TypeError(
                "CashAmount.value must be a Decimal, integer or a string "
                "containing a number."
            ) from exc

        if not self._raw_value.is_finite():
            raise ValueError("CashAmount.value must be finite.")

        if not isinstance(currency, Currency):
            raise TypeError("CashAmount.currency must be a Currency.")
        self._currency = currency

    @property
    def value_rounded(self) -> Decimal:
        if not hasattr(self, "_value_rounded"):
            self._value_rounded = round(self._raw_value, self._currency.places)
        return self._value_rounded

    @property
    def value_normalized(self) -> Decimal:
        if not hasattr(self, "_value_normalized"):
            self._value_normalized = self._raw_value.normalize()
            if -self._value_normalized.as_tuple().exponent < self._currency.places:
                self._value_normalized = self._value_normalized.quantize(
                    quantizers[self._currency.places]
                )
        return self._value_normalized

    @property
    def currency(self) -> Currency:
        return self._currency

    def __repr__(self) -> str:
        return f"CashAmount({self.to_str_normalized()})"

    def __str__(self) -> str:
        return self.to_str_normalized()

    def __hash__(self) -> int:
        return hash((self._raw_value, self._currency))

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        if self._currency != __o._currency:  # noqa: SLF001
            if self._raw_value == 0 and __o._raw_value == 0:  # noqa: SLF001
                return True  # If values are zero, amounts are always equal
            raise CurrencyError("CashAmount.currency of operands must match.")
        return self._raw_value == __o._raw_value  # noqa: SLF001

    def __lt__(self, __o: object) -> bool:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        if self._currency != __o._currency:  # noqa: SLF001
            raise CurrencyError("CashAmount.currency of operands must match.")
        return self._raw_value < __o._raw_value  # noqa: SLF001

    def __le__(self, __o: object) -> bool:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        if self._currency != __o._currency:  # noqa: SLF001
            raise CurrencyError("CashAmount.currency of operands must match.")
        return self._raw_value <= __o._raw_value  # noqa: SLF001

    def __neg__(self) -> Self:
        obj = object.__new__(CashAmount)
        obj._raw_value = -self._raw_value  # noqa: SLF001
        obj._currency = self._currency  # noqa: SLF001
        return obj

    def __add__(self, __o: object) -> Self:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        if self._currency != __o._currency:  # noqa: SLF001
            raise CurrencyError("CashAmount.currency of operands must match.")
        obj = object.__new__(CashAmount)
        obj._raw_value = self._raw_value + __o._raw_value  # noqa: SLF001
        obj._currency = self._currency  # noqa: SLF001
        return obj

    def __radd__(self, __o: object) -> Self:
        return self.__add__(__o)

    def __sub__(self, __o: object) -> Self:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        if self._currency != __o._currency:  # noqa: SLF001
            raise CurrencyError("CashAmount.currency of operands must match.")
        obj = object.__new__(CashAmount)
        obj._raw_value = self._raw_value - __o._raw_value  # noqa: SLF001
        obj._currency = self._currency  # noqa: SLF001
        return obj

    def __rsub__(self, __o: object) -> Self:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        if self._currency != __o._currency:  # noqa: SLF001
            raise CurrencyError("CashAmount.currency of operands must match.")
        obj = object.__new__(CashAmount)
        obj._raw_value = __o._raw_value - self._raw_value  # noqa: SLF001
        obj._currency = self._currency  # noqa: SLF001
        return obj

    def __mul__(self, __o: object) -> Self:
        if not isinstance(__o, int | Decimal):
            return NotImplemented
        obj = object.__new__(CashAmount)
        obj._raw_value = self._raw_value * __o  # noqa: SLF001
        obj._currency = self._currency  # noqa: SLF001
        return obj

    def __rmul__(self, __o: object) -> Self:
        return self.__mul__(__o)

    def __truediv__(self, __o: object) -> Decimal:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        if self._currency != __o._currency:  # noqa: SLF001
            raise CurrencyError("CashAmount.currency of operands must match.")
        return self._raw_value / __o._raw_value  # noqa: SLF001

    def __rtruediv__(self, __o: object) -> Decimal:
        if not isinstance(__o, CashAmount):
            return NotImplemented
        if self._currency != __o._currency:  # noqa: SLF001
            raise CurrencyError("CashAmount.currency of operands must match.")
        return __o._raw_value / self._raw_value  # noqa: SLF001

    def is_positive(self) -> bool:
        return self._raw_value > 0

    def is_negative(self) -> bool:
        return self._raw_value < 0

    def to_str_rounded(self) -> str:
        if not hasattr(self, "_str_rounded"):
            self._str_rounded = (
                f"{self.value_rounded:,.{self._currency.places}f} {self._currency.code}"
            )
        return self._str_rounded

    def to_str_normalized(self) -> str:
        if not hasattr(self, "_str_normalized"):
            self._str_normalized = f"{self.value_normalized:,} {self._currency.code}"
        return self._str_normalized

    def convert(self, target_currency: Currency, date_: date | None = None) -> Self:
        if target_currency == self._currency:
            return self
        if self._raw_value == 0:
            return target_currency.zero_amount
        factor = self._currency.get_conversion_factor(target_currency, date_)
        obj = object.__new__(CashAmount)
        obj._raw_value = self._raw_value * factor  # noqa: SLF001
        obj._currency = target_currency  # noqa: SLF001
        return obj

    def serialize(self) -> dict[str, Any]:
        return self.to_str_normalized()

    @staticmethod
    def deserialize(
        cash_amount_string: str, currencies: dict[str, Currency]
    ) -> "CashAmount":
        value, _, currency_code = cash_amount_string.partition(" ")
        value = value.replace(",", "")  # remove any thousands separators
        currency = currencies[currency_code]
        return CashAmount(value, currency)