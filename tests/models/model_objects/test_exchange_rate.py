from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.model_objects.currency_objects import (
    Currency,
    CurrencyError,
    ExchangeRate,
)
from src.models.user_settings import user_settings
from tests.models.test_assets.composites import (
    currencies,
    everything_except,
    valid_decimals,
)


@given(primary=currencies(), secondary=currencies())
def test_creation(primary: Currency, secondary: Currency) -> None:
    assume(primary != secondary)
    exchange_rate = ExchangeRate(primary, secondary)
    assert exchange_rate.primary_currency == primary
    assert exchange_rate.secondary_currency == secondary
    assert exchange_rate.currencies == {primary, secondary}
    assert exchange_rate.rate_history == {}
    assert exchange_rate.rate_history_pairs == ()
    assert exchange_rate.latest_rate.is_nan()
    assert exchange_rate.latest_date is None
    assert exchange_rate.earliest_date is None
    assert exchange_rate.rate_decimals == 0
    assert exchange_rate.__repr__() == (
        f"ExchangeRate({primary.code}/{secondary.code})"
    )
    assert exchange_rate.__str__() == f"{primary.code}/{secondary.code}"
    assert secondary in primary.convertible_to
    assert primary in secondary.convertible_to
    assert exchange_rate.calculate_return(None).is_nan()


@given(
    primary=currencies(),
    secondary=currencies(),
    rate=valid_decimals(min_value=0.01) | st.integers(min_value=1, max_value=1e6),
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
    primary=currencies(),
    secondary=currencies(),
    rate=valid_decimals(min_value=0.01) | st.integers(min_value=1, max_value=1e6),
    date_=st.dates(),
)
def test_set_and_delete_rate(
    primary: Currency, secondary: Currency, rate: Decimal, date_: date
) -> None:
    assume(primary != secondary)
    exchange_rate = ExchangeRate(primary, secondary)
    exchange_rate.set_rate(date_, rate)
    assert exchange_rate.latest_rate == rate
    assert exchange_rate.rate_history[date_] == rate
    exchange_rate.delete_rate(date_)
    assert exchange_rate.latest_rate.is_nan()
    assert exchange_rate.rate_history.get(date_) is None


@given(
    primary=currencies(),
    secondary=currencies(),
    rate=valid_decimals(min_value=0.01)
    | st.integers(min_value=1, max_value=1e6)
    | st.floats(
        min_value=1,
        max_value=1e6,
        allow_infinity=False,
        allow_nan=False,
        allow_subnormal=False,
    ),
    date_=st.dates(),
)
def test_set_rate_from_str(
    primary: Currency, secondary: Currency, rate: Decimal, date_: date
) -> None:
    assume(primary != secondary)
    exchange_rate = ExchangeRate(primary, secondary)
    rate = str(rate)
    exchange_rate.set_rate(date_, rate)
    assert exchange_rate.latest_rate == Decimal(rate)
    assert exchange_rate.rate_history[date_] == Decimal(rate)


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
    rate=valid_decimals(min_value=0),
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
    rate=everything_except((Decimal, int, str)),
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
    rate=st.decimals(max_value=0),
    date_=st.dates(),
)
def test_set_rate_invalid_rate_value(
    primary: Currency, secondary: Currency, rate: Any, date_: date
) -> None:
    assume(primary != secondary)
    exchange_rate = ExchangeRate(primary, secondary)
    with pytest.raises(
        ValueError, match="Parameter 'rate' must be finite and positive."
    ):
        exchange_rate.set_rate(date_, rate)


def test_get_rate() -> None:
    primary = Currency("EUR", 2)
    secondary = Currency("CZK", 2)
    exchange_rate = ExchangeRate(primary, secondary)

    assert exchange_rate.get_rate(
        datetime.now(tz=user_settings.settings.time_zone)
    ).is_nan()

    date_1 = datetime.now(tz=user_settings.settings.time_zone) - timedelta(days=2)
    date_2 = datetime.now(tz=user_settings.settings.time_zone) - timedelta(days=1)
    date_3 = datetime.now(tz=user_settings.settings.time_zone)
    rate_1 = Decimal(25)
    rate_2 = Decimal(24)
    rate_3 = Decimal(23)

    exchange_rate.set_rate(date_1, rate_1)
    assert exchange_rate.latest_rate == rate_1
    assert exchange_rate.get_rate() == rate_1
    assert exchange_rate.get_rate(date_1) == rate_1
    assert exchange_rate.get_rate(date_1 + timedelta(days=1)) == rate_1

    exchange_rate.set_rate(date_2, rate_2)
    exchange_rate.set_rate(date_3, rate_3)

    assert exchange_rate.latest_rate == rate_3
    assert exchange_rate.get_rate() == rate_3
    assert exchange_rate.get_rate(date_1) == rate_1
    assert exchange_rate.get_rate(date_2) == rate_2
    assert exchange_rate.get_rate(date_3) == rate_3
    assert exchange_rate.get_rate(date_3 + timedelta(days=1)) == rate_3
    assert exchange_rate.get_rate(date_1 - timedelta(days=1)) == rate_1


@given(
    primary=currencies(),
    secondary=currencies(),
    data=st.data(),
)
def test_set_rates(primary: Currency, secondary: Currency, data: st.DataObject) -> None:
    assume(primary != secondary)

    data_: list[tuple[date, Decimal]] = data.draw(
        st.lists(
            st.tuples(
                st.dates(),
                st.decimals(
                    min_value="0.01",
                    max_value=1_000_000,
                    allow_infinity=False,
                    allow_nan=False,
                ),
            ),
            min_size=0,
            max_size=5,
        )
    )

    _dates = {date_ for date_, _ in data_}
    assume(len(_dates) == len(data_))

    exchange_rate = ExchangeRate(primary, secondary)
    exchange_rate.set_rates(data_)

    if len(data_) != 0:
        latest_date = max(date_ for date_, _ in data_)
        latest_rate = None
        for date_, rate in data_:
            if date_ == latest_date:
                latest_rate = rate
                break
        assert round(exchange_rate.latest_rate, 10) == round(latest_rate, 10)
        assert round(exchange_rate.rate_history[latest_date], 10) == round(
            latest_rate, 10
        )
    else:
        latest_date = None
        latest_rate = Decimal("NaN")
        assert exchange_rate.latest_rate.is_nan()

    assert exchange_rate.latest_date == latest_date
