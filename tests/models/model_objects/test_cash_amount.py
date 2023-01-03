import numbers
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.currency import (
    CashAmount,
    ConversionFactorNotFoundError,
    Currency,
    CurrencyError,
    ExchangeRate,
)
from tests.models.test_assets.composites import (
    cash_amounts,
    currencies,
    everything_except,
)


@given(
    value=st.decimals(min_value=0, allow_infinity=False, allow_nan=False),
    currency=currencies(),
)
def test_creation(value: Decimal, currency: Currency) -> None:
    cash_amount = CashAmount(value, currency)
    assert cash_amount.value == round(value, currency.places)
    assert (
        cash_amount.__repr__()
        == f"CashAmount({round(value,currency.places)} {currency.code})"
    )
    assert str(cash_amount) == f"{round(value,currency.places)} {currency.code}"


# TODO: fix test w.r.t. string value
@given(
    value=everything_except((Decimal, int)),
    currency=currencies(),
)
def test_value_invalid_type(value: Decimal, currency: Currency) -> None:
    with pytest.raises(TypeError, match="CashAmount.value must be a Decimal."):
        CashAmount(value, currency)


@given(
    value=st.sampled_from(
        [Decimal("NaN"), Decimal("sNan"), Decimal("-Infinity"), Decimal("Infinity")]
    ),
    currency=currencies(),
)
def test_value_invalid_value(value: Decimal, currency: Currency) -> None:
    with pytest.raises(ValueError, match="CashAmount.value must be finite."):
        CashAmount(value, currency)


@given(
    value=st.decimals(min_value=0, allow_infinity=False, allow_nan=False),
    currency=everything_except(Currency),
)
def test_currency_invalid_type(value: Decimal, currency: Currency) -> None:
    with pytest.raises(TypeError, match="CashAmount.currency must be a Currency."):
        CashAmount(value, currency)


@given(
    value_1=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
    value_2=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
    currency=currencies(),
)
def test_eq(value_1: Decimal, value_2: Decimal, currency: Currency) -> None:
    amount_1 = CashAmount(value_1, currency)
    amount_2 = CashAmount(value_2, currency)
    expected = amount_1.value == amount_2.value
    assert (amount_1 == amount_2) == expected


@given(cash_amount=cash_amounts(), other=everything_except(CashAmount))
def test_eq_not_cashamount(cash_amount: CashAmount, other: Any) -> None:
    result = cash_amount.__eq__(other)
    assert result == NotImplemented


@given(currency_1=currencies(), currency_2=currencies())
def test_eq_different_currency_zero_value(
    currency_1: Currency, currency_2: Currency
) -> None:
    assume(currency_1 != currency_2)
    amount_1 = CashAmount(Decimal(0), currency_1)
    amount_2 = CashAmount(Decimal(0), currency_2)
    assert amount_1 == amount_2


@given(
    currency_1=currencies(),
    currency_2=currencies(),
)
def test_eq_different_currency_nonzero_value(
    currency_1: Currency, currency_2: Currency
) -> None:
    assume(currency_1 != currency_2)
    amount_1 = CashAmount(Decimal("123"), currency_1)
    amount_2 = CashAmount(Decimal("456"), currency_2)
    with pytest.raises(CurrencyError):
        amount_1.__eq__(amount_2)


@given(
    value_1=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
    value_2=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
    currency=currencies(),
)
def test_lt(value_1: Decimal, value_2: Decimal, currency: Currency) -> None:
    amount_1 = CashAmount(value_1, currency)
    amount_2 = CashAmount(value_2, currency)
    expected = amount_1.value < amount_2.value
    assert (amount_1 < amount_2) == expected


@given(cash_amount=cash_amounts(), other=everything_except(CashAmount))
def test_lt_not_cashamount(cash_amount: CashAmount, other: Any) -> None:
    result = cash_amount.__lt__(other)
    assert result == NotImplemented


@given(cash_amount_1=cash_amounts(), cash_amount_2=cash_amounts())
def test_lt_different_currencies(
    cash_amount_1: CashAmount, cash_amount_2: CashAmount
) -> None:
    assume(cash_amount_1.currency != cash_amount_2.currency)
    with pytest.raises(CurrencyError):
        cash_amount_1.__lt__(cash_amount_2)


@given(
    value_1=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
    value_2=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
    currency=currencies(),
)
def test_sum(value_1: Decimal, value_2: Decimal, currency: Currency) -> None:
    amount_1 = CashAmount(value_1, currency)
    amount_2 = CashAmount(value_2, currency)
    result = sum([amount_1, amount_2])
    expected = CashAmount(amount_1.value + amount_2.value, currency)
    assert result == expected


@given(
    value_1=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
    value_2=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
    currency=currencies(),
)
def test_add_radd(value_1: Decimal, value_2: Decimal, currency: Currency) -> None:
    amount_1 = CashAmount(value_1, currency)
    amount_2 = CashAmount(value_2, currency)
    expected = CashAmount(amount_1.value + amount_2.value, currency)
    assert amount_1.__add__(amount_2) == expected
    assert amount_1.__radd__(amount_2) == expected


@given(
    value=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
    currency=currencies(),
    integer=st.integers(min_value=0, max_value=int(1e10)),
)
def test_add_radd_int(value: Decimal, currency: Currency, integer: int) -> None:
    amount_1 = CashAmount(value, currency)
    expected = CashAmount(amount_1.value + integer, currency)
    assert amount_1.__add__(integer) == expected
    assert amount_1.__radd__(integer) == expected


@given(cash_amount_1=cash_amounts(), cash_amount_2=cash_amounts())
def test_add_radd_different_currencies(
    cash_amount_1: CashAmount, cash_amount_2: CashAmount
) -> None:
    assume(cash_amount_1.currency != cash_amount_2.currency)
    with pytest.raises(CurrencyError):
        cash_amount_1.__add__(cash_amount_2)
    with pytest.raises(CurrencyError):
        cash_amount_1.__radd__(cash_amount_2)


@given(cash_amount=cash_amounts(), number=everything_except(numbers.Real))
def test_add_radd_not_real(cash_amount: CashAmount, number: Any) -> None:
    result = cash_amount.__add__(number)
    assert result == NotImplemented
    result = cash_amount.__radd__(number)
    assert result == NotImplemented


@given(
    value_1=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
    value_2=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
    currency=currencies(),
)
def test_sub_rsub(value_1: Decimal, value_2: Decimal, currency: Currency) -> None:
    amount_1 = CashAmount(value_1, currency)
    amount_2 = CashAmount(value_2, currency)
    expected_sub = CashAmount(amount_1.value - amount_2.value, currency)
    expected_rsub = CashAmount(amount_2.value - amount_1.value, currency)
    assert amount_1.__sub__(amount_2) == expected_sub
    assert amount_1.__rsub__(amount_2) == expected_rsub


@given(cash_amount_1=cash_amounts(), cash_amount_2=cash_amounts())
def test_sub_rsub_different_currencies(
    cash_amount_1: CashAmount, cash_amount_2: CashAmount
) -> None:
    assume(cash_amount_1.currency != cash_amount_2.currency)
    with pytest.raises(CurrencyError):
        cash_amount_1.__sub__(cash_amount_2)
    with pytest.raises(CurrencyError):
        cash_amount_1.__rsub__(cash_amount_2)


@given(cash_amount=cash_amounts(), number=everything_except(numbers.Real))
def test_sub_rsub_not_real(cash_amount: CashAmount, number: Any) -> None:
    result = cash_amount.__sub__(number)
    assert result == NotImplemented
    result = cash_amount.__rsub__(number)
    assert result == NotImplemented


@given(cash_amount=cash_amounts())
def test_convert_to_self(cash_amount: CashAmount) -> None:
    assert cash_amount.convert(cash_amount.currency) == cash_amount


def test_convert_czk_to_btc() -> None:
    currencies = get_currencies()
    cash_amount = CashAmount(Decimal(1_000_000), currencies["CZK"])
    result = cash_amount.convert(currencies["BTC"])
    assert result == CashAmount(Decimal(0.9), currencies["BTC"])


def test_convert_czk_to_btc_date() -> None:
    currencies = get_currencies()
    cash_amount = CashAmount(Decimal(1_000_000), currencies["CZK"])
    date_ = datetime.now(tzinfo).date() - timedelta(days=1)
    result = cash_amount.convert(currencies["BTC"], date_)
    assert result == CashAmount(Decimal(1), currencies["BTC"])


def test_convert_no_path() -> None:
    currencies = get_currencies()
    cash_amount = CashAmount(Decimal(1), currencies["CZK"])
    with pytest.raises(ConversionFactorNotFoundError):
        cash_amount.convert(currencies["XXX"])


def get_currencies() -> dict[str, Currency]:
    btc = Currency("BTC", 8)
    usd = Currency("USD", 2)
    eur = Currency("EUR", 2)
    czk = Currency("CZK", 2)
    pln = Currency("PLN", 2)
    dkk = Currency("DKK", 2)
    nok = Currency("NOK", 2)
    rub = Currency("RUB", 2)
    byn = Currency("BYN", 2)
    xxx = Currency("xxx", 2)

    today = datetime.now(tzinfo).date()
    yesterday = datetime.now(tzinfo).date() - timedelta(days=1)

    exchange_eur_czk = ExchangeRate(eur, czk)
    exchange_eur_czk.set_rate(today, Decimal("25"))
    exchange_eur_czk.set_rate(yesterday, Decimal("20"))
    exchange_eur_pln = ExchangeRate(eur, pln)  # noqa: F841
    exchange_pln_rub = ExchangeRate(pln, rub)  # noqa: F841
    exchange_eur_dkk = ExchangeRate(eur, dkk)  # noqa: F841
    exchange_eur_rub = ExchangeRate(eur, rub)  # noqa: F841
    exchange_eur_usd = ExchangeRate(eur, usd)
    exchange_eur_usd.set_rate(today, Decimal("0.9"))
    exchange_eur_usd.set_rate(yesterday, Decimal("1"))
    exchange_btc_usd = ExchangeRate(btc, usd)
    exchange_btc_usd.set_rate(today, Decimal("40000"))
    exchange_btc_usd.set_rate(yesterday, Decimal("50000"))

    exchange_usd_rub = ExchangeRate(usd, rub)  # noqa: F841
    exchange_rub_byn = ExchangeRate(rub, byn)  # noqa: F841
    exchange_dkk_nok = ExchangeRate(dkk, nok)  # noqa: F841

    return {
        "BTC": btc,
        "USD": usd,
        "EUR": eur,
        "CZK": czk,
        "PLN": pln,
        "DKK": dkk,
        "RUB": rub,
        "BYN": byn,
        "NOK": nok,
        "XXX": xxx,
    }
