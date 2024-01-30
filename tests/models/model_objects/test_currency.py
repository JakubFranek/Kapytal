import string
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.model_objects.currency_objects import (
    Currency,
    CurrencyError,
    ExchangeRate,
)
from tests.models.test_assets.composites import currencies, everything_except


@given(
    code=st.text(alphabet=string.ascii_letters, min_size=3, max_size=3),
    decimals=st.integers(min_value=0, max_value=8),
)
def test_creation(code: str, decimals: int) -> None:
    currency = Currency(code, decimals)

    assert currency.code == code.upper()
    assert currency.__repr__() == f"Currency({code.upper()})"
    assert currency.__str__() == code.upper()
    assert currency.decimals == decimals
    assert currency.convertible_to == set()
    assert currency.exchange_rates == {}


@given(code=st.text(max_size=2), decimals=st.integers(min_value=0, max_value=8))
def test_code_too_short(code: str, decimals: int) -> None:
    with pytest.raises(
        ValueError, match="Currency.code must be a three letter ISO-4217 code."
    ):
        Currency(code, decimals)


@given(code=st.text(min_size=4), decimals=st.integers(min_value=0, max_value=8))
def test_code_too_long(code: str, decimals: int) -> None:
    with pytest.raises(
        ValueError, match="Currency.code must be a three letter ISO-4217 code."
    ):
        Currency(code, decimals)


@given(
    code=st.text(min_size=3, max_size=3), decimals=st.integers(min_value=0, max_value=8)
)
def test_code_not_alpha(code: str, decimals: int) -> None:
    assume(any(char.isdigit() for char in code))
    with pytest.raises(
        ValueError, match="Currency.code must be a three letter ISO-4217 code."
    ):
        Currency(code, decimals)


@given(code=everything_except(str), decimals=st.integers(min_value=0, max_value=8))
def test_code_not_string(code: Any, decimals: int) -> None:
    with pytest.raises(TypeError, match="Currency.code must be a string."):
        Currency(code, decimals)


@given(
    code=st.text(alphabet=string.ascii_letters, min_size=3, max_size=3),
    decimals=everything_except(int),
)
def test_decimal_invalid_type(code: Any, decimals: int) -> None:
    with pytest.raises(TypeError, match="Currency.decimals must be an integer."):
        Currency(code, decimals)


@given(
    code=st.text(alphabet=string.ascii_letters, min_size=3, max_size=3),
    decimals=st.integers(max_value=-1),
)
def test_decimals_invalid_value(code: Any, decimals: int) -> None:
    with pytest.raises(ValueError, match="Currency.decimals must not be negative."):
        Currency(code, decimals)


@given(
    code=st.text(alphabet=string.ascii_letters, min_size=3, max_size=3),
    decimals_1=st.integers(min_value=0, max_value=8),
    decimals_2=st.integers(min_value=0, max_value=8),
)
def test_eq_hash(code: str, decimals_1: int, decimals_2: int) -> None:
    currency_1 = Currency(code, decimals_1)
    currency_2 = Currency(code, decimals_2)
    assert currency_1 == currency_2
    assert currency_1.__hash__() == currency_2.__hash__()


@given(currency=currencies(), other=everything_except(Currency))
def test_eq_different_type(currency: Currency, other: Any) -> None:
    result = currency.__eq__(other)
    assert result == NotImplemented


@given(currency=currencies(), exchange_rate=everything_except(ExchangeRate))
def test_add_exchange_rate_invalid_type(currency: Currency, exchange_rate: Any) -> None:
    with pytest.raises(
        TypeError, match="Parameter 'exchange_rate' must be an ExchangeRate."
    ):
        currency.add_exchange_rate(exchange_rate)


@given(currency=currencies(), other_1=currencies(), other_2=currencies())
def test_add_exchange_rate_unrelated_currency(
    currency: Currency, other_1: Currency, other_2: Currency
) -> None:
    assume(currency not in {other_1, other_2})
    assume(other_1 != other_2)
    exchange_rate = ExchangeRate(other_1, other_2)
    with pytest.raises(CurrencyError):
        currency.add_exchange_rate(exchange_rate)


@given(currency=currencies(), exchange_rate=everything_except(ExchangeRate))
def test_remove_exchange_rate_invalid_type(
    currency: Currency, exchange_rate: Any
) -> None:
    with pytest.raises(
        TypeError, match="Parameter 'exchange_rate' must be an ExchangeRate."
    ):
        currency.remove_exchange_rate(exchange_rate)


@given(currency=currencies(), other=currencies())
def test_remove_exchange_rate(currency: Currency, other: Currency) -> None:
    assume(currency != other)
    exchange_rate = ExchangeRate(currency, other)
    assert other in currency.convertible_to
    currency.remove_exchange_rate(exchange_rate)
    assert other not in currency.convertible_to
