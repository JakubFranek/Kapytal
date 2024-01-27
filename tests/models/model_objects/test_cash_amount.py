from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.model_objects.currency_objects import (
    CashAmount,
    ConversionFactorNotFoundError,
    Currency,
    CurrencyError,
    ExchangeRate,
)
from src.models.user_settings import user_settings
from tests.models.test_assets.composites import (
    cash_amounts,
    currencies,
    everything_except,
    valid_decimals,
)


@given(
    value=valid_decimals(),
    currency=currencies(),
)
def test_creation(value: Decimal, currency: Currency) -> None:
    cash_amount = CashAmount(value, currency)
    assert cash_amount.__repr__() == f"CashAmount({cash_amount.to_str_normalized()})"


@given(
    value=everything_except((Decimal, int, str)),
    currency=currencies(),
)
def test_value_invalid_type(value: Any, currency: Currency) -> None:
    with pytest.raises(
        TypeError,
        match="CashAmount.value must be a Decimal, integer or a string",
    ):
        CashAmount(value, currency)


@given(
    value=st.floats(),
    currency=currencies(),
)
def test_value_invalid_type_float(value: float, currency: Currency) -> None:
    with pytest.raises(
        TypeError,
        match="CashAmount.value must be a Decimal, integer or a string",
    ):
        CashAmount(value, currency)


@given(
    value=st.text(),
    currency=currencies(),
)
def test_value_invalid_str(value: str, currency: Currency) -> None:
    try:
        Decimal(value)
    except InvalidOperation:
        with pytest.raises(TypeError, match="CashAmount.value must be a Decimal"):
            CashAmount(value, currency)


@given(
    value=st.integers(
        min_value=-1e10,
        max_value=1e10,
    )
    | st.floats(min_value=-1e10, max_value=1e10, allow_infinity=False, allow_nan=False)
    | valid_decimals(),
    currency=currencies(),
)
def test_value_valid_str(value: str, currency: Currency) -> None:
    value = str(value)
    amount = CashAmount(value, currency)
    assert amount.value_rounded == round(Decimal(value), currency.decimals)


@given(
    value=valid_decimals(),
    currency=everything_except(Currency),
)
def test_currency_invalid_type(value: Decimal, currency: Currency) -> None:
    with pytest.raises(TypeError, match="CashAmount.currency must be a Currency."):
        CashAmount(value, currency)


@given(
    value=valid_decimals(),
    currency=currencies(),
)
def test_value_rounded(value: Decimal, currency: Currency) -> None:
    amount = CashAmount(value, currency)
    currency_places = currency.decimals
    if currency_places < 4:
        assert amount.value_rounded == round(value, currency_places)
    else:
        value_rounded = round(value, currency_places)
        min_places = min(currency.decimals, 4)
        if -value_rounded.as_tuple().exponent > min_places:
            value_rounded = value_rounded.normalize()
            if -value_rounded.as_tuple().exponent < min_places:
                value_rounded = value_rounded.quantize(Decimal(f"1e-{currency_places}"))
        assert amount.value_rounded == value_rounded


def test_value_rounded_specific_values() -> None:
    currency_0 = Currency("ABC", 0)
    currency_2 = Currency("DEF", 2)
    currency_4 = Currency("GHI", 4)
    currency_6 = Currency("JKL", 6)
    currency_18 = Currency("MNO", 18)

    amount_0 = CashAmount(Decimal("1.23456789123456789123456789"), currency_0)
    assert amount_0.value_rounded == Decimal("1")
    amount_2 = CashAmount(Decimal("1.23456789123456789123456789"), currency_2)
    assert amount_2.value_rounded == Decimal("1.23")
    amount_4 = CashAmount(Decimal("1.23456789123456789123456789"), currency_4)
    assert amount_4.value_rounded == Decimal("1.2346")
    amount_6 = CashAmount(Decimal("1.23456789123456789123456789"), currency_6)
    assert amount_6.value_rounded == Decimal("1.234568")
    amount_18 = CashAmount(Decimal("1.23456789123456789123456789"), currency_18)
    assert amount_18.value_rounded == Decimal("1.234567891234567891")

    amount_0 = CashAmount(Decimal("1.00000000000000000000000000"), currency_0)
    assert str(amount_0.value_rounded) == "1"
    amount_2 = CashAmount(Decimal("1.00000000000000000000000000"), currency_2)
    assert str(amount_2.value_rounded) == "1.00"
    amount_4 = CashAmount(Decimal("1.00000000000000000000000000"), currency_4)
    assert str(amount_4.value_rounded) == "1.0000"
    amount_6 = CashAmount(Decimal("1.00000000000000000000000000"), currency_6)
    assert str(amount_6.value_rounded) == "1.0000"
    amount_18 = CashAmount(Decimal("1.00000000000000000000000000"), currency_18)
    assert str(amount_18.value_rounded) == "1.0000"


@given(
    value=valid_decimals(),
    currency=currencies(),
)
def test_value_normalized(value: Decimal, currency: Currency) -> None:
    amount = CashAmount(value, currency)
    value_normalized = value.normalize()
    places = min(currency.decimals, 4)
    if not value_normalized.is_nan() and -value_normalized.as_tuple().exponent < places:
        value_normalized = value_normalized.quantize(Decimal(f"1e-{places}"))
    assert amount.value_normalized == value_normalized


def test_value_normalized_specific_values() -> None:
    currency_0 = Currency("ABC", 0)
    currency_2 = Currency("DEF", 2)
    currency_4 = Currency("GHI", 4)
    currency_6 = Currency("JKL", 6)
    currency_18 = Currency("MNO", 18)

    amount_0 = CashAmount(Decimal("1.23456789123456789123456789"), currency_0)
    assert amount_0.value_normalized == Decimal("1.23456789123456789123456789")
    amount_2 = CashAmount(Decimal("1.23456789123456789123456789"), currency_2)
    assert amount_2.value_normalized == Decimal("1.23456789123456789123456789")
    amount_4 = CashAmount(Decimal("1.23456789123456789123456789"), currency_4)
    assert amount_4.value_normalized == Decimal("1.23456789123456789123456789")
    amount_6 = CashAmount(Decimal("1.23456789123456789123456789"), currency_6)
    assert amount_6.value_normalized == Decimal("1.23456789123456789123456789")
    amount_18 = CashAmount(Decimal("1.23456789123456789123456789"), currency_18)
    assert amount_18.value_normalized == Decimal("1.23456789123456789123456789")

    amount_0 = CashAmount(Decimal("1.00000000000000000000000000"), currency_0)
    assert str(amount_0.value_normalized) == "1"
    amount_2 = CashAmount(Decimal("1.00000000000000000000000000"), currency_2)
    assert str(amount_2.value_normalized) == "1.00"
    amount_4 = CashAmount(Decimal("1.00000000000000000000000000"), currency_4)
    assert str(amount_4.value_normalized) == "1.0000"
    amount_6 = CashAmount(Decimal("1.00000000000000000000000000"), currency_6)
    assert str(amount_6.value_normalized) == "1.0000"
    amount_18 = CashAmount(Decimal("1.00000000000000000000000000"), currency_18)
    assert str(amount_18.value_normalized) == "1.0000"


@given(
    value_1=valid_decimals(),
    value_2=valid_decimals(),
    currency=currencies(),
)
def test_eq(value_1: Decimal, value_2: Decimal, currency: Currency) -> None:
    amount_1 = CashAmount(value_1, currency)
    amount_2 = CashAmount(value_2, currency)
    expected = amount_1.value_normalized == amount_2.value_normalized
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
    assert not amount_1.__eq__(amount_2)


@given(
    value_1=valid_decimals(),
    value_2=valid_decimals(),
    currency=currencies(),
)
def test_lt(value_1: Decimal, value_2: Decimal, currency: Currency) -> None:
    amount_1 = CashAmount(value_1, currency)
    amount_2 = CashAmount(value_2, currency)
    expected = amount_1.value_normalized < amount_2.value_normalized
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
    value_1=valid_decimals(),
    value_2=valid_decimals(),
    currency=currencies(),
)
def test_le(value_1: Decimal, value_2: Decimal, currency: Currency) -> None:
    amount_1 = CashAmount(value_1, currency)
    amount_2 = CashAmount(value_2, currency)
    expected = amount_1.value_normalized <= amount_2.value_normalized
    assert (amount_1 <= amount_2) == expected


@given(cash_amount=cash_amounts(), other=everything_except(CashAmount))
def test_le_not_cashamount(cash_amount: CashAmount, other: Any) -> None:
    result = cash_amount.__le__(other)
    assert result == NotImplemented


@given(cash_amount_1=cash_amounts(), cash_amount_2=cash_amounts())
def test_le_different_currencies(
    cash_amount_1: CashAmount, cash_amount_2: CashAmount
) -> None:
    assume(cash_amount_1.currency != cash_amount_2.currency)
    with pytest.raises(CurrencyError):
        cash_amount_1.__le__(cash_amount_2)


@given(
    value_1=valid_decimals(),
    value_2=valid_decimals(),
    currency=currencies(),
)
def test_sum(value_1: Decimal, value_2: Decimal, currency: Currency) -> None:
    amount_1 = CashAmount(value_1, currency)
    amount_2 = CashAmount(value_2, currency)
    result = sum([amount_1, amount_2], start=currency.zero_amount)
    expected = CashAmount(
        amount_1.value_normalized + amount_2.value_normalized, currency
    )
    assert result == expected


@given(
    value_1=valid_decimals(),
    value_2=valid_decimals(),
    currency=currencies(),
)
def test_add_radd(value_1: Decimal, value_2: Decimal, currency: Currency) -> None:
    amount_1 = CashAmount(value_1, currency)
    amount_2 = CashAmount(value_2, currency)
    expected = CashAmount(
        amount_1.value_normalized + amount_2.value_normalized, currency
    )
    assert amount_1.__add__(amount_2) == expected
    assert amount_1.__radd__(amount_2) == expected


@given(cash_amount_1=cash_amounts(), cash_amount_2=cash_amounts())
def test_add_radd_different_currencies(
    cash_amount_1: CashAmount, cash_amount_2: CashAmount
) -> None:
    assume(cash_amount_1.currency != cash_amount_2.currency)
    with pytest.raises(CurrencyError):
        cash_amount_1.__add__(cash_amount_2)
    with pytest.raises(CurrencyError):
        cash_amount_1.__radd__(cash_amount_2)


@given(cash_amount=cash_amounts(), number=everything_except(CashAmount))
def test_add_radd_invalid_type(cash_amount: CashAmount, number: Any) -> None:
    result = cash_amount.__add__(number)
    assert result == NotImplemented
    result = cash_amount.__radd__(number)
    assert result == NotImplemented


@given(
    value_1=valid_decimals(),
    value_2=valid_decimals(),
    currency=currencies(),
)
def test_sub_rsub(value_1: Decimal, value_2: Decimal, currency: Currency) -> None:
    amount_1 = CashAmount(value_1, currency)
    amount_2 = CashAmount(value_2, currency)
    expected_sub = CashAmount(
        amount_1.value_normalized - amount_2.value_normalized, currency
    )
    expected_rsub = CashAmount(
        amount_2.value_normalized - amount_1.value_normalized, currency
    )
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


@given(cash_amount=cash_amounts(), number=everything_except(CashAmount))
def test_sub_rsub_invalid_type(cash_amount: CashAmount, number: Any) -> None:
    result = cash_amount.__sub__(number)
    assert result == NotImplemented
    result = cash_amount.__rsub__(number)
    assert result == NotImplemented


@given(
    cash_amount=cash_amounts(),
    number=st.integers(min_value=-1e6, max_value=1e6)
    | valid_decimals(min_value=-1e6, max_value=1e6),
)
def test_mul_rmul(cash_amount: CashAmount, number: int | Decimal) -> None:
    expected_mul = CashAmount(cash_amount.value_rounded * number, cash_amount.currency)
    assert cash_amount.__mul__(number) == expected_mul
    assert cash_amount.__rmul__(number) == expected_mul


@given(cash_amount=cash_amounts(), number=everything_except((int, Decimal)))
def test_mul_rmul_invalid_type(cash_amount: CashAmount, number: Any) -> None:
    result = cash_amount.__mul__(number)
    assert result == NotImplemented
    result = cash_amount.__rmul__(number)
    assert result == NotImplemented


@given(
    data=st.data(),
)
def test_truediv_rtruediv(data: st.DataObject) -> None:
    currency = data.draw(currencies())
    amount_1 = data.draw(cash_amounts(currency=currency, min_value=1e-6))
    amount_2 = data.draw(cash_amounts(currency=currency, min_value=1e-6))
    expected_truediv = amount_1.value_normalized / amount_2.value_normalized
    expected_rtruediv = amount_2.value_normalized / amount_1.value_normalized
    assert amount_1.__truediv__(amount_2) == expected_truediv
    assert amount_1.__rtruediv__(amount_2) == expected_rtruediv


@given(
    data=st.data(),
)
def test_truediv_with_numbers(data: st.DataObject) -> None:
    currency = data.draw(currencies())
    amount_1 = data.draw(cash_amounts(currency=currency, min_value=1e-6))
    amount_2 = data.draw(
        st.decimals(min_value=1e-6, allow_infinity=False, allow_nan=False)
    )
    expected_truediv = amount_1.value_normalized / amount_2
    assert amount_1.__truediv__(amount_2).value_normalized == expected_truediv


@given(cash_amount_1=cash_amounts(), cash_amount_2=cash_amounts())
def test_truediv_rtruediv_different_currencies(
    cash_amount_1: CashAmount, cash_amount_2: CashAmount
) -> None:
    assume(cash_amount_1.currency != cash_amount_2.currency)
    with pytest.raises(CurrencyError):
        cash_amount_1.__truediv__(cash_amount_2)
    with pytest.raises(CurrencyError):
        cash_amount_1.__rtruediv__(cash_amount_2)


@given(amount_1=cash_amounts(), amount_2=everything_except((int, Decimal, CashAmount)))
def test_truediv_rtruediv_invalid_type(amount_1: CashAmount, amount_2: Any) -> None:
    result = amount_1.__truediv__(amount_2)
    assert result == NotImplemented
    result = amount_1.__rtruediv__(amount_2)
    assert result == NotImplemented


@given(cash_amount=cash_amounts())
def test_is_positive(cash_amount: CashAmount) -> None:
    assert (cash_amount.value_rounded > 0) == cash_amount.is_positive()


@given(cash_amount=cash_amounts())
def test_convert_to_self(cash_amount: CashAmount) -> None:
    assert cash_amount.convert(cash_amount.currency) == cash_amount


def test_convert_czk_to_btc() -> None:
    currencies = get_currencies()
    cash_amount = CashAmount(Decimal(1_000_000), currencies["CZK"])
    result = cash_amount.convert(currencies["BTC"])
    assert result == CashAmount(Decimal("0.9"), currencies["BTC"])
    # repeat the conversion in the other direction (from BTC to CZK)
    cash_amount = CashAmount(Decimal("0.9"), currencies["BTC"])
    result = cash_amount.convert(currencies["CZK"])
    assert (
        result.to_str_rounded()
        == CashAmount(Decimal(1_000_000), currencies["CZK"]).to_str_rounded()
    )


def test_convert_czk_to_btc_date() -> None:
    currencies = get_currencies()
    cash_amount = CashAmount(Decimal(1_000_000), currencies["CZK"])
    date_ = datetime.now(user_settings.settings.time_zone).date() - timedelta(days=1)
    result = cash_amount.convert(currencies["BTC"], date_)
    assert result == CashAmount(Decimal(1), currencies["BTC"])


def test_convert_no_path() -> None:
    currencies = get_currencies()
    cash_amount = CashAmount(Decimal(1), currencies["CZK"])
    with pytest.raises(ConversionFactorNotFoundError):
        cash_amount.convert(currencies["XXX"])


def test_nan() -> None:
    nan_amount = CashAmount(Decimal("NaN"), Currency("CZK", 2))
    assert not nan_amount.is_positive()
    assert not nan_amount.is_negative()
    assert nan_amount.is_nan()
    assert not nan_amount.is_finite()
    assert nan_amount.value_rounded.is_nan()
    assert nan_amount.value_normalized.is_nan()


def test_round() -> None:
    import locale

    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

    amount = CashAmount(Decimal("1.23456789"), Currency("EUR", 2))

    assert amount.value_normalized == Decimal("1.23456789")
    assert amount.value_rounded == Decimal("1.23")
    assert round(amount, 0) == Decimal(1)
    assert round(amount, 1) == Decimal("1.2")
    assert round(amount, 2) == Decimal("1.23")
    assert round(amount, 3) == Decimal("1.235")
    assert round(amount, 4) == Decimal("1.2346")
    assert round(amount, 5) == Decimal("1.23457")
    assert round(amount, 6) == Decimal("1.234568")

    assert amount.to_str_rounded() == "1.23 EUR"
    assert amount.to_str_rounded(0) == "1 EUR"
    assert amount.to_str_rounded(1) == "1.2 EUR"
    assert amount.to_str_rounded(2) == "1.23 EUR"
    assert amount.to_str_rounded(3) == "1.235 EUR"
    assert amount.to_str_rounded(4) == "1.2346 EUR"
    assert amount.to_str_rounded(5) == "1.23457 EUR"
    assert amount.to_str_rounded(6) == "1.234568 EUR"


def test_round_quantization() -> None:
    import locale

    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

    amount = CashAmount(Decimal("1.0000"), Currency("EUR", 2))

    assert amount.value_normalized == Decimal("1.0000")
    assert amount.value_rounded == Decimal("1.00")
    assert round(amount, 0) == Decimal(1)
    assert round(amount, 1) == Decimal("1.0")
    assert round(amount, 2) == Decimal("1.00")
    assert round(amount, 3) == Decimal("1.000")
    assert round(amount, 4) == Decimal("1.0000")
    assert round(amount, 5) == Decimal("1.00000")
    assert round(amount, 6) == Decimal("1.000000")

    assert amount.to_str_rounded() == "1.00 EUR"
    assert amount.to_str_rounded(0) == "1 EUR"
    assert amount.to_str_rounded(1) == "1.0 EUR"
    assert amount.to_str_rounded(2) == "1.00 EUR"
    assert amount.to_str_rounded(3) == "1.000 EUR"
    assert amount.to_str_rounded(4) == "1.0000 EUR"
    assert amount.to_str_rounded(5) == "1.00000 EUR"
    assert amount.to_str_rounded(6) == "1.000000 EUR"


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

    today = datetime.now(user_settings.settings.time_zone).date()
    yesterday = datetime.now(user_settings.settings.time_zone).date() - timedelta(
        days=1
    )

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
