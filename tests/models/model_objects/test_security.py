from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.mixins.name_mixin import NameLengthError
from src.models.model_objects.currency_objects import (
    CashAmount,
    Currency,
    CurrencyError,
)
from src.models.model_objects.security_objects import InvalidCharacterError, Security
from tests.models.test_assets.composites import (
    currencies,
    decimal_powers_of_10,
    everything_except,
    names,
    securities,
    valid_decimals,
)


@given(
    name=names(min_size=1, max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=names(min_size=1, max_size=32),
    currency=currencies(),
    shares_unit=decimal_powers_of_10(),
)
def test_creation(
    name: str,
    symbol: str,
    type_: str,
    currency: Currency,
    shares_unit: Decimal,
) -> None:
    security = Security(name, symbol, type_, currency, shares_unit)
    assert security.name == name
    assert security.symbol == symbol.upper()
    assert security.type_ == type_
    assert security.currency == currency
    assert security.price == CashAmount(Decimal(0), currency)
    assert security.latest_date is None
    assert security.price_history == {}
    assert security.price_history_pairs == ()
    assert security.decimal_price_history_pairs == ()
    assert security.__repr__() == f"Security('{security.name}')"
    assert security.__str__() == security.name
    assert isinstance(security.__hash__(), int)
    assert security.shares_unit == shares_unit


@given(
    name=st.just(""),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=names(min_size=1, max_size=32),
    shares_unit=valid_decimals(min_value=1e-10, max_value=1),
    currency=currencies(),
)
def test_name_too_short(
    name: str,
    symbol: str,
    type_: str,
    shares_unit: Decimal,
    currency: Currency,
) -> None:
    with pytest.raises(NameLengthError):
        Security(name, symbol, type_, currency, shares_unit)


@given(
    name=names(min_size=65),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=names(min_size=1, max_size=32),
    currency=currencies(),
    shares_unit=valid_decimals(min_value=1e-10, max_value=1),
)
def test_name_too_long(
    name: str,
    symbol: str,
    type_: str,
    currency: Currency,
    shares_unit: Decimal,
) -> None:
    with pytest.raises(NameLengthError):
        Security(name, symbol, type_, currency, shares_unit)


@given(
    name=names(max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=everything_except(str),
    currency=currencies(),
    shares_unit=valid_decimals(min_value=1e-10, max_value=1),
)
def test_type_invalid_type(
    name: str, symbol: str, type_: Any, currency: Currency, shares_unit: Decimal
) -> None:
    with pytest.raises(TypeError, match="Security.type_ must be a string."):
        Security(name, symbol, type_, currency, shares_unit)


@given(
    name=names(min_size=1, max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=st.just(""),
    currency=currencies(),
    shares_unit=valid_decimals(min_value=1e-10, max_value=1),
)
def test_type_too_short(
    name: str, symbol: str, type_: str, currency: Currency, shares_unit: Decimal
) -> None:
    with pytest.raises(ValueError, match="Security.type_ length must be within"):
        Security(name, symbol, type_, currency, shares_unit)


@given(
    name=names(min_size=1, max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=names(min_size=33, max_size=100),
    currency=currencies(),
    shares_unit=valid_decimals(min_value=1e-10, max_value=1),
)
def test_type_too_long(
    name: str, symbol: str, type_: str, currency: Currency, shares_unit: Decimal
) -> None:
    with pytest.raises(ValueError, match="Security.type_ length must be within"):
        Security(name, symbol, type_, currency, shares_unit)


@given(
    name=names(min_size=1, max_size=64),
    symbol=everything_except(str),
    type_=names(min_size=1, max_size=32),
    currency=currencies(),
    shares_unit=valid_decimals(min_value=1e-10, max_value=1),
)
def test_symbol_invalid_type(
    name: str, symbol: str, type_: str, currency: Currency, shares_unit: Decimal
) -> None:
    with pytest.raises(TypeError, match="Security.symbol must be a string."):
        Security(name, symbol, type_, currency, shares_unit)


@given(
    name=names(min_size=1, max_size=64),
    symbol=st.text(min_size=9),
    type_=names(min_size=1, max_size=32),
    currency=currencies(),
    shares_unit=valid_decimals(min_value=1e-10, max_value=1),
)
def test_symbol_too_long(
    name: str, symbol: str, type_: str, currency: Currency, shares_unit: Decimal
) -> None:
    with pytest.raises(ValueError, match="Security.symbol length must be within"):
        Security(name, symbol, type_, currency, shares_unit)


@given(
    name=names(min_size=1, max_size=64),
    symbol=st.text(min_size=1, max_size=8),
    type_=names(min_size=1, max_size=32),
    currency=currencies(),
    shares_unit=valid_decimals(min_value=1e-10, max_value=1),
)
def test_symbol_invalid_chars(
    name: str, symbol: str, type_: str, currency: Currency, shares_unit: Decimal
) -> None:
    assume(any(char not in Security.SYMBOL_ALLOWED_CHARS for char in symbol))
    with pytest.raises(InvalidCharacterError):
        Security(name, symbol, type_, currency, shares_unit)


@given(
    name=names(min_size=1, max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=names(min_size=1, max_size=32),
    currency=everything_except(Currency),
    shares_unit=valid_decimals(min_value=1e-10, max_value=1),
)
def test_currency_invalid_type(
    name: str, symbol: str, type_: str, currency: Any, shares_unit: Decimal
) -> None:
    with pytest.raises(TypeError, match="Security.currency must be a Currency."):
        Security(name, symbol, type_, currency, shares_unit)


@given(
    name=names(min_size=1, max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=names(min_size=1, max_size=32),
    currency=currencies(),
    shares_unit=everything_except((Decimal, str, int)),
)
def test_shares_unit_invalid_type(
    name: str, symbol: str, type_: str, currency: Currency, shares_unit: Any
) -> None:
    with pytest.raises(TypeError, match="Security.shares_unit must be"):
        Security(name, symbol, type_, currency, shares_unit)


@given(
    name=names(min_size=1, max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=names(min_size=1, max_size=32),
    currency=currencies(),
    shares_unit=st.sampled_from(
        [
            Decimal("NaN"),
            Decimal("sNan"),
            Decimal("-Infinity"),
            Decimal("Infinity"),
            0,
            -1,
        ]
    ),
)
def test_shares_unit_invalid_value(
    name: str, symbol: str, type_: str, currency: Currency, shares_unit: Any
) -> None:
    with pytest.raises(
        ValueError, match="Security.shares_unit must be finite and positive."
    ):
        Security(name, symbol, type_, currency, shares_unit)


@given(
    data=st.data(),
    name=names(min_size=1, max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=names(min_size=1, max_size=32),
    currency=currencies(),
)
def test_shares_unit_not_power_of_10(
    data: st.DataObject,
    name: str,
    symbol: str,
    type_: str,
    currency: Currency,
) -> None:
    shares_unit = data.draw(valid_decimals(min_value=1e-10))
    assume(shares_unit.log10() % 1 != 0)
    with pytest.raises(ValueError, match="Security.shares_unit must be a power of 10."):
        Security(name, symbol, type_, currency, shares_unit)


@given(
    data=st.data(),
)
def test_set_price(
    data: st.DataObject,
) -> None:
    security = get_security()
    currency = security.currency
    price = CashAmount(data.draw(valid_decimals()), currency)
    date_ = data.draw(st.dates())
    security.set_price(date_, price)
    assert security.price.value_normalized == price.value_normalized
    assert security.price_history[date_].value_normalized == price.value_normalized
    assert security.price == price
    assert security.latest_date == date_
    price_2 = CashAmount(data.draw(valid_decimals()), currency)
    date_2 = data.draw(st.dates())
    security.set_price(date_2, price_2)
    assert security.price_history[date_2].value_normalized == price_2.value_normalized
    if date_2 > date_:
        assert security.price == price_2
        assert security.latest_date == date_2


@given(
    data=st.data(),
)
def test_set_and_delete_price(
    data: st.DataObject,
) -> None:
    security = get_security()
    currency = security.currency
    price = CashAmount(data.draw(valid_decimals()), currency)
    date_ = data.draw(st.dates())
    security.set_price(date_, price)
    assert security.price.value_normalized == price.value_normalized
    assert security.price_history[date_].value_normalized == price.value_normalized
    assert security.price == price
    assert security.latest_date == date_

    security.delete_price(date_)
    assert security.price.is_nan()
    assert security.latest_date is None


@given(
    date_=everything_except(date),
    price=valid_decimals(min_value=0),
)
def test_set_price_invalid_date_type(date_: Any, price: Decimal) -> None:
    security = get_security()
    with pytest.raises(TypeError, match="Parameter 'date_' must be a date."):
        security.set_price(date_, price)


@given(date_=st.dates(), price=everything_except(CashAmount))
def test_set_price_invalid_price_type(date_: date, price: Any) -> None:
    security = get_security()
    with pytest.raises(TypeError, match="Parameter 'price' must be a CashAmount."):
        security.set_price(date_, price)


@given(
    date_=st.dates(),
    value=valid_decimals(),
    currency=currencies(),
)
def test_set_price_invalid_currency(
    date_: date, value: Decimal, currency: Currency
) -> None:
    security = get_security()
    assume(currency != security.currency)
    price = CashAmount(value, currency)
    with pytest.raises(CurrencyError):
        security.set_price(date_, price)


@given(security=securities(), other=everything_except(Security))
def test_eq_different_types(security: Security, other: Any) -> None:
    assert (security == other) is False


@given(
    currency=currencies(),
    data=st.data(),
)
def test_set_prices(currency: Currency, data: st.DataObject) -> None:
    data = data.draw(
        st.lists(
            st.tuples(
                st.dates(),
                st.decimals(min_value=0.01, allow_infinity=False, allow_nan=False),
            ),
            min_size=0,
            max_size=5,
        )
    )
    data_prep: list[tuple[date, CashAmount]] = []
    for date_, rate in data:
        data_prep.append((date_, CashAmount(rate, currency)))

    security = Security("NAME", "SYMB", "TYPE", currency, 1)
    security.set_prices(data_prep)

    if len(data_prep) != 0:
        latest_date = max(date_ for date_, _ in data_prep)
        latest_rate = None
        for date_, rate in data_prep:
            if date_ == latest_date:
                latest_rate = rate
                break
        assert security.price == latest_rate
        assert security.price_history[latest_date] == latest_rate

    else:
        latest_date = None
        latest_rate = Decimal("NaN")
        assert security._latest_price.is_nan()

    assert security.latest_date == latest_date


def get_security() -> Security:
    return Security(
        "Vanguard FTSE All-World UCITS ETF USD Acc",
        "VWCE.DE",
        "ETF",
        Currency("EUR", 2),
        shares_unit=1,
    )
