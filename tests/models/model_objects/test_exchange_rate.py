from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.model_objects.currency import (
    Currency,
    CurrencyError,
    ExchangeRate,
    NoExchangeRateError,
)
from tests.models.test_assets.composites import currencies, everything_except


@given(primary=currencies(), secondary=currencies())
def test_creation(primary: Currency, secondary: Currency) -> None:
    assume(primary != secondary)
    exchange_rate = ExchangeRate(primary, secondary)
    assert exchange_rate.primary_currency == primary
    assert exchange_rate.secondary_currency == secondary
    assert exchange_rate.currencies == {primary, secondary}
    assert exchange_rate.rate_history == {}
    with pytest.raises(NoExchangeRateError):
        exchange_rate.latest_rate
    assert exchange_rate.__repr__() == (
        f"ExchangeRate({primary.code}/{secondary.code})"
    )
    assert exchange_rate.__str__() == f"{primary.code}/{secondary.code}"
    assert secondary in primary.convertible_to
    assert primary in secondary.convertible_to


@given(
    primary=currencies(),
    secondary=currencies(),
    rate=st.decimals(min_value=0, allow_infinity=False, allow_nan=False),
    date_=st.dates(),
)
def test_set_rate(
    primary: Currency, secondary: Currency, rate: Decimal, date_: date
) -> None:
    assume(primary != secondary)
    exchange_rate = ExchangeRate(primary, secondary)
    exchange_rate.set_rate(date_, rate)
    assert exchange_rate.latest_rate == rate
    assert exchange_rate.rate_history[date_] == rate


@given(
    primary=everything_except(Currency),
    secondary=currencies(),
)
def test_invalid_primary_type(primary: Currency, secondary: Currency) -> None:
    with pytest.raises(
        TypeError, match="ExchangeRate.primary_currency must be a Currency."
    ):
        ExchangeRate(primary, secondary)


@given(
    primary=currencies(),
    secondary=everything_except(Currency),
)
def test_invalid_secondary_type(primary: Currency, secondary: Currency) -> None:
    with pytest.raises(
        TypeError, match="ExchangeRate.secondary_currency must be a Currency."
    ):
        ExchangeRate(primary, secondary)


@given(
    currency=currencies(),
)
def test_same_currencies(currency: Currency) -> None:
    with pytest.raises(CurrencyError):
        ExchangeRate(currency, currency)


@given(
    primary=currencies(),
    secondary=currencies(),
    rate=st.decimals(min_value=0, allow_infinity=False, allow_nan=False),
    date_=everything_except(date),
)
def test_set_rate_invalid_date_type(
    primary: Currency, secondary: Currency, rate: Decimal, date_: Any
) -> None:
    assume(primary != secondary)
    exchange_rate = ExchangeRate(primary, secondary)
    with pytest.raises(TypeError, match="Parameter 'date_' must be a date."):
        exchange_rate.set_rate(date_, rate)


@given(
    primary=currencies(),
    secondary=currencies(),
    rate=everything_except(Decimal),
    date_=st.dates(),
)
def test_set_rate_invalid_rate_type(
    primary: Currency, secondary: Currency, rate: Any, date_: date
) -> None:
    assume(primary != secondary)
    exchange_rate = ExchangeRate(primary, secondary)
    with pytest.raises(TypeError, match="Parameter 'rate' must be a Decimal."):
        exchange_rate.set_rate(date_, rate)


@given(
    primary=currencies(),
    secondary=currencies(),
    rate=st.decimals(max_value=-0.01),
    date_=st.dates(),
)
def test_set_rate_invalid_rate_value(
    primary: Currency, secondary: Currency, rate: Any, date_: date
) -> None:
    assume(primary != secondary)
    exchange_rate = ExchangeRate(primary, secondary)
    with pytest.raises(
        ValueError, match="Parameter 'rate' must be finite and non-negative."
    ):
        exchange_rate.set_rate(date_, rate)
