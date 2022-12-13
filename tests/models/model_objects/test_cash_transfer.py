from datetime import datetime
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.cash_objects import CashAccount, CashTransfer
from tests.models.composites import cash_accounts, cash_transfers
from tests.models.testing_constants import min_datetime


@given(
    description=st.text(min_size=0, max_size=256),
    account_sender=cash_accounts(),
    account_recipient=cash_accounts(),
    datetime_=st.datetimes(min_value=min_datetime),
    amount_sent=st.decimals(min_value=0.01, allow_infinity=False, allow_nan=False),
    amount_received=st.decimals(min_value=0.01, allow_infinity=False, allow_nan=False),
)
def test_creation(
    description: str,
    datetime_: datetime,
    account_sender: CashAccount,
    account_recipient: CashAccount,
    amount_sent: Decimal,
    amount_received: Decimal,
) -> None:
    dt_start = datetime.now(tzinfo)
    cash_transfer = CashTransfer(
        description,
        datetime_,
        account_sender,
        account_recipient,
        amount_sent,
        amount_received,
    )

    dt_created_diff = cash_transfer.datetime_created - dt_start

    assert cash_transfer.description == description
    assert cash_transfer.datetime_ == datetime_
    assert cash_transfer.account_sender == account_sender
    assert cash_transfer.account_recipient == account_recipient
    assert cash_transfer.amount_sent == amount_sent
    assert cash_transfer.amount_received == amount_received
    assert dt_created_diff.seconds < 1


@given(
    transfer=cash_transfers(),
    new_account=st.integers()
    | st.floats()
    | st.text()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_account_sender_invalid_type(transfer: CashTransfer, new_account: Any) -> None:
    with pytest.raises(
        TypeError, match="CashTransfer.account_sender must be a CashAccount."
    ):
        transfer.account_sender = new_account


@given(
    transfer=cash_transfers(),
    new_account=st.integers()
    | st.floats()
    | st.text()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_account_recipient_invalid_type(
    transfer: CashTransfer, new_account: Any
) -> None:
    with pytest.raises(
        TypeError, match="CashTransfer.account_recipient must be a CashAccount."
    ):
        transfer.account_recipient = new_account


@given(
    transfer=cash_transfers(),
    new_amount=st.integers()
    | st.floats()
    | st.text()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_amount_sent_invalid_type(transfer: CashTransfer, new_amount: Any) -> None:
    with pytest.raises(TypeError, match="CashTransfer.amount_sent must be a Decimal."):
        transfer.amount_sent = new_amount


@given(
    transfer=cash_transfers(),
    new_amount=st.decimals(max_value=-0.01),
)
def test_amount_sent_invalid_value(transfer: CashTransfer, new_amount: Decimal) -> None:
    with pytest.raises(
        ValueError,
        match="CashTransfer.amount_sent must be a finite and positive Decimal.",
    ):
        transfer.amount_sent = new_amount


@given(
    transfer=cash_transfers(),
    new_amount=st.integers()
    | st.floats()
    | st.text()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_amount_received_invalid_type(transfer: CashTransfer, new_amount: Any) -> None:
    with pytest.raises(
        TypeError, match="CashTransfer.amount_received must be a Decimal."
    ):
        transfer.amount_received = new_amount


@given(
    transfer=cash_transfers(),
    new_amount=st.decimals(max_value=-0.01),
)
def test_amount_received_invalid_value(
    transfer: CashTransfer, new_amount: Decimal
) -> None:
    with pytest.raises(
        ValueError,
        match="CashTransfer.amount_received must be a finite and positive Decimal.",
    ):
        transfer.amount_received = new_amount


@given(
    transfer=cash_transfers(),
    new_sender=cash_accounts(),
)
def test_change_sender(transfer: CashTransfer, new_sender: CashAccount) -> None:

    previous_sender = transfer.account_sender
    assert transfer in previous_sender.transactions
    assert transfer not in new_sender.transactions
    transfer.account_sender = new_sender
    assert transfer in new_sender.transactions
    assert transfer not in previous_sender.transactions


@given(
    transfer=cash_transfers(),
    new_recipient=cash_accounts(),
)
def test_change_recipient(transfer: CashTransfer, new_recipient: CashAccount) -> None:

    previous_recipient = transfer.account_recipient
    assert transfer in previous_recipient.transactions
    assert transfer not in new_recipient.transactions
    transfer.account_recipient = new_recipient
    assert transfer in new_recipient.transactions
    assert transfer not in previous_recipient.transactions


@given(transfer=cash_transfers())
def test_get_amount_for_account(transfer: CashTransfer) -> None:
    expected_sender_amount = -transfer.amount_sent
    expected_recipient_amount = transfer.amount_received

    result_sender = transfer.get_amount_for_account(transfer.account_sender)
    result_recipient = transfer.get_amount_for_account(transfer.account_recipient)

    assert result_sender == expected_sender_amount
    assert result_recipient == expected_recipient_amount


@given(
    transfer=cash_transfers(),
    account=cash_accounts(),
)
def test_get_amount_for_account_invalid_account_value(
    transfer: CashTransfer, account: CashAccount
) -> None:
    assume(account != transfer.account_recipient)
    assume(account != transfer.account_sender)
    with pytest.raises(
        ValueError,
        match='The argument "account" is not related to this CashTransfer.',
    ):
        transfer.get_amount_for_account(account)
