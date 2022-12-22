from datetime import datetime
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransfer,
    TransferSameAccountError,
    UnrelatedAccountError,
)
from tests.models.test_assets.composites import (
    cash_accounts,
    cash_transfers,
    everything_except,
)
from tests.models.test_assets.constants import min_datetime


@given(
    description=st.text(min_size=0, max_size=256),
    account_sender=cash_accounts(),
    account_recipient=cash_accounts(),
    datetime_=st.datetimes(min_value=min_datetime),
    amount_sent=st.decimals(min_value="0.01", allow_infinity=False, allow_nan=False),
    amount_received=st.decimals(
        min_value="0.01", allow_infinity=False, allow_nan=False
    ),
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
    transfer = CashTransfer(
        description,
        datetime_,
        account_sender,
        account_recipient,
        amount_sent,
        amount_received,
    )

    dt_created_diff = transfer.datetime_created - dt_start

    assert transfer.description == description
    assert transfer.datetime_ == datetime_
    assert transfer.account_sender == account_sender
    assert transfer.account_recipient == account_recipient
    assert transfer.amount_sent == amount_sent
    assert transfer.amount_received == amount_received
    assert transfer.__repr__() == (
        f"CashTransfer({transfer.amount_sent} {transfer.account_sender.currency.code} "
        f"from '{transfer.account_sender.name}', "
        f"{transfer.amount_received} {transfer.account_recipient.currency.code} "
        f"to '{transfer.account_recipient.name}', "
        f"{transfer.datetime_.strftime('%Y-%m-%d')})"
    )
    assert dt_created_diff.seconds < 1


@given(transfer=cash_transfers(), new_amount=everything_except(Decimal))
def test_amount_sent_invalid_type(transfer: CashTransfer, new_amount: Any) -> None:
    with pytest.raises(TypeError, match="CashTransfer.amount_sent must be a Decimal."):
        transfer.amount_sent = new_amount


@given(
    transfer=cash_transfers(),
    new_amount=st.decimals(max_value="-0.01"),
)
def test_amount_sent_invalid_value(transfer: CashTransfer, new_amount: Decimal) -> None:
    with pytest.raises(
        ValueError,
        match="CashTransfer.amount_sent must be a finite and positive Decimal.",
    ):
        transfer.amount_sent = new_amount


@given(transfer=cash_transfers(), new_amount=everything_except(Decimal))
def test_amount_received_invalid_type(transfer: CashTransfer, new_amount: Any) -> None:
    with pytest.raises(
        TypeError, match="CashTransfer.amount_received must be a Decimal."
    ):
        transfer.amount_received = new_amount


@given(
    transfer=cash_transfers(),
    new_amount=st.decimals(max_value="-0.01"),
)
def test_amount_received_invalid_value(
    transfer: CashTransfer, new_amount: Decimal
) -> None:
    with pytest.raises(
        ValueError,
        match="CashTransfer.amount_received must be a finite and positive Decimal.",
    ):
        transfer.amount_received = new_amount


@given(transfer=cash_transfers())
def test_get_amount_for_account(transfer: CashTransfer) -> None:
    expected_sender_amount = -transfer.amount_sent
    expected_recipient_amount = transfer.amount_received

    result_sender = transfer.get_amount_for_account(transfer.account_sender)
    result_recipient = transfer.get_amount_for_account(transfer.account_recipient)

    assert result_sender == expected_sender_amount
    assert result_recipient == expected_recipient_amount


@given(
    transaction=cash_transfers(),
    account=everything_except(CashAccount),
)
def test_get_amount_for_account_invalid_account_type(
    transaction: CashTransfer, account: Any
) -> None:
    with pytest.raises(TypeError, match="Argument 'account' must be a CashAccount."):
        transaction.get_amount_for_account(account)


@given(
    transfer=cash_transfers(),
    account=cash_accounts(),
)
def test_get_amount_for_account_invalid_account_value(
    transfer: CashTransfer, account: CashAccount
) -> None:
    with pytest.raises(UnrelatedAccountError):
        transfer.get_amount_for_account(account)


@given(
    transfer=cash_transfers(), new_sender=cash_accounts(), new_recipient=cash_accounts()
)
def test_set_accounts(
    transfer: CashTransfer, new_sender: CashAccount, new_recipient: CashAccount
) -> None:
    current_sender = transfer.account_sender
    current_recipient = transfer.account_recipient

    assert transfer.account_sender != new_sender
    assert transfer.account_recipient != new_recipient
    assert transfer in current_sender.transactions
    assert transfer in current_recipient.transactions
    assert transfer not in new_sender.transactions
    assert transfer not in new_recipient.transactions

    transfer.set_accounts(new_sender, new_recipient)

    assert transfer.account_sender == new_sender
    assert transfer.account_recipient == new_recipient
    assert transfer not in current_sender.transactions
    assert transfer not in current_recipient.transactions
    assert transfer in new_sender.transactions
    assert transfer in new_recipient.transactions


@given(transfer=cash_transfers(), new_sender=everything_except(CashAccount))
def test_set_accounts_invalid_sender_type(
    transfer: CashTransfer, new_sender: Any
) -> None:
    current_recipient = transfer.account_recipient
    with pytest.raises(
        TypeError, match="Argument 'account_sender' must be a CashAccount."
    ):
        transfer.set_accounts(new_sender, current_recipient)


@given(transfer=cash_transfers(), new_recipient=everything_except(CashAccount))
def test_set_accounts_invalid_recipient_type(
    transfer: CashTransfer, new_recipient: Any
) -> None:
    current_sender = transfer.account_sender
    with pytest.raises(
        TypeError, match="Argument 'account_recipient' must be a CashAccount."
    ):
        transfer.set_accounts(current_sender, new_recipient)


@given(transfer=cash_transfers(), new_account=cash_accounts())
def test_set_accounts_same_account(
    transfer: CashTransfer, new_account: CashAccount
) -> None:
    with pytest.raises(TransferSameAccountError):
        transfer.set_accounts(new_account, new_account)
