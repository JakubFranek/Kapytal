from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.mixins.name_mixin import NameLengthError
from src.models.model_objects.currency import CashAmount, Currency
from src.models.model_objects.security_objects import (
    InvalidCharacterError,
    Security,
    SecurityType,
)
from tests.models.test_assets.composites import (
    currencies,
    everything_except,
    securities,
)
from tests.models.test_assets.get_valid_objects import get_security


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=st.sampled_from(SecurityType),
    currency=currencies(),
    data=st.data(),
)
def test_creation(
    name: str, symbol: str, type_: SecurityType, currency: Currency, data: st.DataObject
) -> None:
    places = data.draw(st.integers(min_value=currency.places, max_value=8) | st.none())
    security = Security(name, symbol, type_, currency, places)
    assert security.name == name
    assert security.symbol == symbol.upper()
    assert security.type_ == type_
    assert security.currency == currency
    assert security.price == CashAmount(Decimal(0), currency)
    assert security.price_history == {}
    assert (
        security.__repr__()
        == f"Security(symbol='{security.symbol}', type={security.type_.name})"
    )
    assert isinstance(security.__hash__(), int)
    if places is None:
        assert security.places == currency.places
    else:
        assert security.places == places


@given(
    name=st.just(""),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=st.sampled_from(SecurityType),
    currency=currencies(),
)
def test_name_too_short(
    name: str, symbol: str, type_: SecurityType, currency: Currency
) -> None:
    with pytest.raises(NameLengthError):
        Security(name, symbol, type_, currency)


@given(
    name=st.text(min_size=65),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=st.sampled_from(SecurityType),
    currency=currencies(),
)
def test_name_too_long(
    name: str, symbol: str, type_: SecurityType, currency: Currency
) -> None:
    with pytest.raises(NameLengthError):
        Security(name, symbol, type_, currency)


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=everything_except(SecurityType),
    currency=currencies(),
)
def test_type_invalid_type(
    name: str, symbol: str, type_: Any, currency: Currency
) -> None:
    with pytest.raises(TypeError, match="Security.type_ must be a SecurityType."):
        Security(name, symbol, type_, currency)


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=everything_except(str),
    type_=st.sampled_from(SecurityType),
    currency=currencies(),
)
def test_symbol_invalid_type(
    name: str, symbol: str, type_: Any, currency: Currency
) -> None:
    with pytest.raises(TypeError, match="Security.symbol must be a string."):
        Security(name, symbol, type_, currency)


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=st.just(""),
    type_=st.sampled_from(SecurityType),
    currency=currencies(),
)
def test_symbol_too_short(
    name: str, symbol: str, type_: Any, currency: Currency
) -> None:
    with pytest.raises(ValueError, match="Security.symbol length must be within"):
        Security(name, symbol, type_, currency)


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=st.text(min_size=9),
    type_=st.sampled_from(SecurityType),
    currency=currencies(),
)
def test_symbol_too_long(
    name: str, symbol: str, type_: Any, currency: Currency
) -> None:
    with pytest.raises(ValueError, match="Security.symbol length must be within"):
        Security(name, symbol, type_, currency)


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=st.text(min_size=1, max_size=8),
    type_=st.sampled_from(SecurityType),
    currency=currencies(),
)
def test_symbol_invalid_chars(
    name: str, symbol: str, type_: Any, currency: Currency
) -> None:
    assume(any(char not in Security.SYMBOL_ALLOWED_CHARS for char in symbol))
    with pytest.raises(InvalidCharacterError):
        Security(name, symbol, type_, currency)


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=st.sampled_from(SecurityType),
    currency=everything_except(Currency),
)
def test_currency_invalid_type(
    name: str, symbol: str, type_: Any, currency: Currency
) -> None:
    with pytest.raises(TypeError, match="Security.currency must be a Currency."):
        Security(name, symbol, type_, currency)


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=st.sampled_from(SecurityType),
    currency=currencies(),
    places=everything_except((int, type(None))),
)
def test_places_invalid_type(
    name: str, symbol: str, type_: Any, currency: Currency, places: Any
) -> None:
    with pytest.raises(TypeError, match="Security.places must be an integer or None."):
        Security(name, symbol, type_, currency, places)


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=st.sampled_from(SecurityType),
    currency=currencies(),
    data=st.data(),
)
def test_places_invalid_value(
    name: str, symbol: str, type_: Any, currency: Currency, data: st.DataObject
) -> None:
    places = data.draw(st.integers(max_value=currency.places - 1))
    with pytest.raises(
        ValueError,
        match="Security.places must not be smaller than Security.currency.places.",
    ):
        Security(name, symbol, type_, currency, places)


@given(
    date_=st.dates(),
    value=st.decimals(
        min_value=-1e10, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
)
def test_set_price(date_: date, value: Decimal) -> None:
    security = get_security()
    currency = security.currency
    price = CashAmount(value, currency)
    security.set_price(date_, price)
    assert security.price.value == round(price.value, security.places)
    assert security.price_history[date_].value == round(price.value, security.places)


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


@given(date_=st.dates(), price=everything_except(CashAmount))
def test_set_price_invalid_price_type(date_: date, price: Any) -> None:
    security = get_security()
    with pytest.raises(TypeError, match="Argument 'price' must be a CashAmount."):
        security.set_price(date_, price)


@given(security=securities(), other=everything_except(Security))
def test_eq_different_types(security: Security, other: Any) -> None:
    assert (security == other) is False
