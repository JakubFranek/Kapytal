from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.mixins.name_mixin import NameLengthError
from src.models.model_objects.security_objects import (
    InvalidCharacterError,
    Security,
    SecurityType,
)
from tests.models.test_assets.composites import everything_except


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=st.sampled_from(SecurityType),
)
def test_creation(name: str, symbol: str, type_: SecurityType) -> None:
    security = Security(name, symbol, type_)
    assert security.name == name
    assert security.symbol == symbol.upper()
    assert security.type_ == type_
    assert security.price == 0
    assert security.price_history == {}
    assert (
        security.__repr__()
        == f"Security(symbol='{security.symbol}', type={security.type_.name})"
    )
    assert isinstance(security.__hash__(), int)


@given(
    name=st.just(""),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=st.sampled_from(SecurityType),
)
def test_name_too_short(name: str, symbol: str, type_: SecurityType) -> None:
    with pytest.raises(NameLengthError):
        Security(name, symbol, type_)


@given(
    name=st.text(min_size=65),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=st.sampled_from(SecurityType),
)
def test_name_too_long(name: str, symbol: str, type_: SecurityType) -> None:
    with pytest.raises(NameLengthError):
        Security(name, symbol, type_)


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=everything_except(SecurityType),
)
def test_type_invalid_type(name: str, symbol: str, type_: Any) -> None:
    with pytest.raises(TypeError, match="Security.type_ must be a SecurityType."):
        Security(name, symbol, type_)


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=everything_except(str),
    type_=st.sampled_from(SecurityType),
)
def test_symbol_invalid_type(name: str, symbol: str, type_: Any) -> None:
    with pytest.raises(TypeError, match="Security.symbol must be a string."):
        Security(name, symbol, type_)


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=st.just(""),
    type_=st.sampled_from(SecurityType),
)
def test_symbol_too_short(name: str, symbol: str, type_: Any) -> None:
    with pytest.raises(ValueError, match="Security.symbol length must be within"):
        Security(name, symbol, type_)


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=st.text(min_size=9),
    type_=st.sampled_from(SecurityType),
)
def test_symbol_too_long(name: str, symbol: str, type_: Any) -> None:
    with pytest.raises(ValueError, match="Security.symbol length must be within"):
        Security(name, symbol, type_)


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=st.text(min_size=1, max_size=8),
    type_=st.sampled_from(SecurityType),
)
def test_symbol_invalid_chars(name: str, symbol: str, type_: Any) -> None:
    assume(any(char not in Security.SYMBOL_ALLOWED_CHARS for char in symbol))
    with pytest.raises(InvalidCharacterError):
        Security(name, symbol, type_)


@given(
    date_=st.dates(),
    price=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
)
def test_set_price(date_: date, price: Decimal) -> None:
    security = get_security()
    security.set_price(date_, price)
    assert security.price == price
    assert security.price_history[date_] == price


@given(
    date_=everything_except(date),
    price=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
)
def test_set_price_invalid_date_type(date_: Any, price: Decimal) -> None:
    security = get_security()
    with pytest.raises(TypeError, match="Argument 'date_' must be a date."):
        security.set_price(date_, price)


@given(date_=st.dates(), price=everything_except(Decimal))
def test_set_price_invalid_price_type(date_: date, price: Any) -> None:
    security = get_security()
    with pytest.raises(TypeError, match="Argument 'price' must be a Decimal."):
        security.set_price(date_, price)


@given(date_=st.dates(), price=st.decimals(max_value=-0.01))
def test_set_price_invalid_price_value(date_: date, price: Any) -> None:
    security = get_security()
    with pytest.raises(
        ValueError, match="Argument 'price' must be a finite, non-negative Decimal."
    ):
        security.set_price(date_, price)


def get_security() -> Security:
    return Security(
        "Vanguard FTSE All-World UCITS ETF USD Acc", "VWCE.DE", SecurityType.ETF
    )
