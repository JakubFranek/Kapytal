from datetime import datetime
from types import NoneType
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransfer,
    TransferSameAccountError,
    UnrelatedAccountError,
)
from src.models.model_objects.currency import CashAmount, Currency, CurrencyError
from tests.models.test_assets.composites import (
    cash_accounts,
    cash_amounts,
    cash_transfers,
    currencies,
    everything_except,
)
from tests.models.test_assets.constants import min_datetime


@given(
    description=st.text(min_size=0, max_size=256),
    account_sender=cash_accounts(),
    account_recipient=cash_accounts(),
    datetime_=st.datetimes(min_value=min_datetime, timezones=st.just(tzinfo)),
    data=st.data(),
)
def test_creation(
    description: str,
    datetime_: datetime,
    account_sender: CashAccount,
    account_recipient: CashAccount,
    data: st.DataObject,
) -> None:
    amount_sent = data.draw(
        cash_amounts(currency=account_sender.currency, min_value="0.01"),
    )
    amount_received = data.draw(
        cash_amounts(currency=account_recipient.currency, min_value="0.01"),
    )

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
    assert transfer.sender == account_sender
    assert transfer.recipient == account_recipient
    assert transfer.amount_sent == amount_sent
    assert transfer.amount_received == amount_received
    assert transfer.__repr__() == (
        f"CashTransfer(sent={transfer.amount_sent}, "
        f"sender='{transfer.sender.name}', "
        f"received={transfer.amount_received}, "
        f"recipient='{transfer.recipient.name}', "
        f"{transfer.datetime_.strftime('%Y-%m-%d')})"
    )
    assert dt_created_diff.seconds < 1


@given(transfer=cash_transfers(), new_amount=everything_except((CashAmount, NoneType)))
def test_amount_sent_invalid_type(transfer: CashTransfer, new_amount: Any) -> None:
    with pytest.raises(TypeError, match="CashTransfer amounts must be CashAmounts."):
        transfer.set_attributes(amount_sent=new_amount)


@given(transfer=cash_transfers(), data=st.data())
def test_amount_sent_invalid_value(transfer: CashTransfer, data: st.DataObject) -> None:
    new_amount = data.draw(cash_amounts(max_value="-0.01"))
    with pytest.raises(ValueError, match="CashTransfer amounts must be positive."):
        transfer.set_attributes(amount_sent=new_amount)


@given(transfer=cash_transfers(), new_amount=everything_except((CashAmount, NoneType)))
def test_amount_received_invalid_type(transfer: CashTransfer, new_amount: Any) -> None:
    with pytest.raises(TypeError, match="CashTransfer amounts must be CashAmounts."):
        transfer.set_attributes(amount_received=new_amount)


@given(transfer=cash_transfers(), data=st.data())
def test_amount_received_invalid_value(
    transfer: CashTransfer, data: st.DataObject
) -> None:
    new_amount = data.draw(cash_amounts(max_value="-0.01"))
    with pytest.raises(ValueError, match="CashTransfer amounts must be positive."):
        transfer.set_attributes(amount_received=new_amount)


@given(transfer=cash_transfers())
def test_get_amount_for_account(transfer: CashTransfer) -> None:
    expected_sender_amount = -transfer.amount_sent
    expected_recipient_amount = transfer.amount_received

    result_sender = transfer.get_amount(transfer.sender)
    result_recipient = transfer.get_amount(transfer.recipient)

    assert result_sender == expected_sender_amount
    assert result_recipient == expected_recipient_amount


@given(
    transaction=cash_transfers(),
    account=everything_except(CashAccount),
)
def test_get_amount_invalid_account_type(
    transaction: CashTransfer, account: Any
) -> None:
    with pytest.raises(TypeError, match="Parameter 'account' must be a CashAccount."):
        transaction.get_amount(account)


@given(
    transfer=cash_transfers(),
    account=cash_accounts(),
)
def test_get_amount_invalid_account_value(
    transfer: CashTransfer, account: CashAccount
) -> None:
    with pytest.raises(UnrelatedAccountError):
        transfer.get_amount(account)


@given(
    transfer=cash_transfers(),
    data=st.data(),
)
def test_set_accounts(transfer: CashTransfer, data: st.DataObject) -> None:
    new_sender = data.draw(cash_accounts(currency=transfer.sender.currency))
    new_recipient = data.draw(cash_accounts(currency=transfer.recipient.currency))

    current_sender = transfer.sender
    current_recipient = transfer.recipient

    assert transfer.sender != new_sender
    assert transfer.recipient != new_recipient
    assert transfer in current_sender.transactions
    assert transfer in current_recipient.transactions
    assert transfer not in new_sender.transactions
    assert transfer not in new_recipient.transactions

    transfer.set_attributes(sender=new_sender, recipient=new_recipient)

    assert transfer.sender == new_sender
    assert transfer.recipient == new_recipient
    assert transfer not in current_sender.transactions
    assert transfer not in current_recipient.transactions
    assert transfer in new_sender.transactions
    assert transfer in new_recipient.transactions


@given(transfer=cash_transfers(), new_sender=everything_except((CashAccount, NoneType)))
def test_set_accounts_invalid_sender_type(
    transfer: CashTransfer, new_sender: Any
) -> None:
    with pytest.raises(TypeError, match="Parameter 'sender' must be a CashAccount."):
        transfer.set_attributes(sender=new_sender)


@given(
    transfer=cash_transfers(), new_recipient=everything_except((CashAccount, NoneType))
)
def test_set_accounts_invalid_recipient_type(
    transfer: CashTransfer, new_recipient: Any
) -> None:
    with pytest.raises(TypeError, match="Parameter 'recipient' must be a CashAccount."):
        transfer.set_attributes(recipient=new_recipient)


@given(currency=currencies(), data=st.data())
def test_set_accounts_same_account(currency: Currency, data: st.DataObject) -> None:
    transfer = data.draw(
        cash_transfers(currency_recipient=currency, currency_sender=currency)
    )
    with pytest.raises(TransferSameAccountError):
        transfer.set_attributes(recipient=transfer.sender)


@given(transfer=cash_transfers())
def test_validate_attributes_same_values(transfer: CashTransfer) -> None:
    transfer.validate_attributes()


@given(transfer=cash_transfers(), currency_1=currencies(), currency_2=currencies())
def test_validate_amount_invalid_currency(
    transfer: CashTransfer, currency_1: Currency, currency_2: Currency
) -> None:
    assume(currency_1 != currency_2)
    with pytest.raises(CurrencyError):
        transfer._validate_amount(CashAmount(1, currency_1), currency_2)


@given(transfer=cash_transfers())
def test_set_attributes_same_values(transfer: CashTransfer) -> None:
    prev_description = transfer.description
    prev_datetime = transfer.datetime_
    prev_sender = transfer.sender
    prev_recipient = transfer.recipient
    prev_amount_sent = transfer.amount_sent
    prev_amount_received = transfer.amount_received
    transfer.set_attributes()
    assert prev_description == transfer.description
    assert prev_datetime == transfer.datetime_
    assert prev_sender == transfer.sender
    assert prev_recipient == transfer.recipient
    assert prev_amount_sent == transfer.amount_sent
    assert prev_amount_received == transfer.amount_received
