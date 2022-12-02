import time
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.enums import CashTransactionType
from src.models.transactions.attributes.payee import Payee

timezone_offset = +1.0  # Central European Time (CET = UTC+01:00)
tzinfo = timezone(timedelta(hours=timezone_offset))

quanta = Decimal("0.01")


@st.composite
def payees(draw: Callable[[st.SearchStrategy[str]], str]) -> Payee:
    name = draw(st.text(min_size=1, max_size=32))
    return Payee(name)


@given(name=st.text(min_size=1, max_size=32))
def test_creation_pass(name: str) -> None:
    dt_start = datetime.now(tzinfo)
    payee = Payee(name)

    dt_created_diff = payee.date_created - dt_start
    dt_edited_diff = payee.date_last_edited - dt_start

    assert payee.name == name
    assert dt_created_diff.seconds < 1
    assert dt_created_diff == dt_edited_diff
    assert payee.total_expense == 0
    assert payee.total_income == 0
    assert payee.total_sum == 0
    assert payee.total_volume == 0


@given(
    name=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()])
)
def test_name_not_string(name: Any) -> None:
    with pytest.raises(TypeError, match="Payee name must be a string."):
        Payee(name)


@given(name=st.just(""))
def test_name_too_short(name: str) -> None:
    with pytest.raises(ValueError, match="Payee name length must be*"):
        Payee(name)


@given(name=st.text(min_size=33))
def test_name_too_long(name: str) -> None:
    with pytest.raises(ValueError, match="Payee name length must be*"):
        Payee(name)


@given(
    name=st.text(min_size=1, max_size=32),
    new_name=st.text(min_size=1, max_size=32),
)
def test_date_last_edited(name: str, new_name: str) -> None:
    assume(name != new_name)
    payee = Payee(name)
    time.sleep(1 / 1_000_000.0)
    payee.name = new_name

    assert payee.name == new_name
    assert payee.date_created != payee.date_last_edited


@given(
    name=st.text(min_size=1, max_size=32),
    amount_1=st.decimals(
        min_value=0, max_value=1e20, allow_infinity=False, allow_nan=False
    ),
    amount_2=st.decimals(
        min_value=0, max_value=1e20, allow_infinity=False, allow_nan=False
    ),
    transaction_type_1=st.sampled_from(CashTransactionType),
    transaction_type_2=st.sampled_from(CashTransactionType),
)
def test_update_totals(
    name: str,
    amount_1: Decimal,
    amount_2: Decimal,
    transaction_type_1: CashTransactionType,
    transaction_type_2: CashTransactionType,
) -> None:
    payee = Payee(name)
    payee.update_totals(amount_1, transaction_type_1)
    payee.update_totals(amount_2, transaction_type_2)

    expected_expense = Decimal(0)
    expected_income = Decimal(0)
    expected_sum = Decimal(0)
    if transaction_type_1 == CashTransactionType.INCOME:
        expected_income += amount_1
        expected_sum += amount_1
    else:
        expected_expense += amount_1
        expected_sum -= amount_1

    if transaction_type_2 == CashTransactionType.INCOME:
        expected_income += amount_2
        expected_sum += amount_2
    else:
        expected_expense += amount_2
        expected_sum -= amount_2
    expected_volume = amount_1 + amount_2

    assert payee.total_volume.quantize(quanta) == expected_volume.quantize(quanta)
    assert payee.total_sum.quantize(quanta) == expected_sum.quantize(quanta)
    assert payee.total_expense.quantize(quanta) == expected_expense.quantize(quanta)
    assert payee.total_income.quantize(quanta) == expected_income.quantize(quanta)


@given(
    payee=payees(),
    amount=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
    transaction_type=st.sampled_from(CashTransactionType),
)
def test_update_totals_invalid_amount_type(
    payee: Payee, amount: Any, transaction_type: CashTransactionType
) -> None:
    with pytest.raises(TypeError, match="Update amount must be of type Decimal."):
        payee.update_totals(amount, transaction_type)


@given(
    payee=payees(),
    amount=st.decimals(min_value=0, allow_infinity=False, allow_nan=False),
    transaction_type=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_update_totals_invalid_transaction_type_type(
    payee: Payee, amount: Any, transaction_type: CashTransactionType
) -> None:
    with pytest.raises(
        TypeError, match="Transaction type must be of type CashTransactionType."
    ):
        payee.update_totals(amount, transaction_type)


@given(
    payee=payees(),
    amount=st.decimals(max_value=-0.01, allow_nan=True, allow_infinity=True),
    transaction_type=st.sampled_from(CashTransactionType),
)
def test_update_totals_invalid_amount_value(
    payee: Payee, amount: Any, transaction_type: CashTransactionType
) -> None:
    with pytest.raises(
        ValueError, match="Update amount must be a finite and positive Decimal."
    ):
        payee.update_totals(amount, transaction_type)
