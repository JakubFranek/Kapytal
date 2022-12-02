import string
from collections.abc import Callable
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.models.accounts.cash_account import CashAccount
from src.models.currency import Currency


@st.composite
def currencies(draw: Callable[[st.SearchStrategy[str]], str]) -> Currency:
    name = draw(st.text(alphabet=string.ascii_letters, min_size=3, max_size=3))
    return Currency(name)


@given(
    name=st.text(min_size=1, max_size=32),
    currency=currencies(),
    initial_balance=st.decimals(min_value=0, allow_nan=False, allow_infinity=False),
)
def test_creation_pass(name: str, currency: Currency, initial_balance: Decimal) -> None:
    cash_account = CashAccount(name, currency, initial_balance)
    assert cash_account.name == name
    assert cash_account.currency == currency
    assert cash_account.balance == initial_balance
    assert cash_account.initial_balance == initial_balance


@given(
    name=st.text(min_size=1, max_size=32),
    currency=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
    initial_balance=st.decimals(min_value=0, allow_nan=False, allow_infinity=False),
)
def test_currency_incorrect_type(
    name: str, currency: Any, initial_balance: Decimal
) -> None:
    with pytest.raises(
        TypeError, match="CashAccount currency must be of type Currency."
    ):
        CashAccount(name, currency, initial_balance)


@given(
    name=st.text(min_size=1, max_size=32),
    currency=currencies(),
    initial_balance=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_initial_balance_not_decimal(
    name: str, currency: Currency, initial_balance: Any
) -> None:
    with pytest.raises(
        TypeError, match="CashAccount initial balance must be a Decimal."
    ):
        CashAccount(name, currency, initial_balance)


@given(
    name=st.text(min_size=1, max_size=32),
    currency=currencies(),
    initial_balance=st.decimals(max_value=-0.01, allow_nan=True, allow_infinity=True),
)
def test_initial_balance_invalid_values(
    name: str, currency: Currency, initial_balance: Decimal
) -> None:
    with pytest.raises(
        ValueError, match="CashAccount initial balance must be positive and finite."
    ):
        CashAccount(name, currency, initial_balance)


@given(
    name=st.text(min_size=1, max_size=32),
    currency=currencies(),
    initial_balance=st.decimals(min_value=0, allow_nan=False, allow_infinity=False),
    balance=st.decimals(allow_nan=False, allow_infinity=False),
)
def test_balance_set(
    name: str, currency: Currency, initial_balance: Decimal, balance: Decimal
) -> None:
    cash_account = CashAccount(name, currency, initial_balance)
    assert cash_account.initial_balance == initial_balance
    assert cash_account.balance == initial_balance
    cash_account.balance = balance
    assert cash_account.balance == balance


@given(
    name=st.text(min_size=1, max_size=32),
    currency=currencies(),
    initial_balance=st.decimals(min_value=0, allow_nan=False, allow_infinity=False),
    balance=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_balance_not_decimal(
    name: str, currency: Currency, initial_balance: Decimal, balance: Any
) -> None:
    cash_account = CashAccount(name, currency, initial_balance)
    with pytest.raises(TypeError, match="CashAccount balance must be a Decimal."):
        cash_account.balance = balance


@given(
    name=st.text(min_size=1, max_size=32),
    currency=currencies(),
    initial_balance=st.decimals(min_value=0, allow_nan=False, allow_infinity=False),
    balance=st.sampled_from([Decimal("NaN"), Decimal("inf"), Decimal("-inf")]),
)
def test_balance_invalid_values(
    name: str, currency: Currency, initial_balance: Decimal, balance: Decimal
) -> None:
    cash_account = CashAccount(name, currency, initial_balance)
    with pytest.raises(ValueError, match="CashAccount balance must be finite."):
        cash_account.balance = balance
