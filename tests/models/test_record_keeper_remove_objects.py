from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from src.models.constants import tzinfo
from src.models.custom_exceptions import InvalidOperationError
from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.model_objects.security_objects import (
    SecurityTransactionType,
    SecurityType,
)
from src.models.record_keeper import DoesNotExistError, RecordKeeper
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_remove_account() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("PARENT", None)
    parent = record_keeper.account_groups[0]

    record_keeper.add_security_account("TEST NAME", "PARENT")
    assert len(parent.children) != 0
    assert len(record_keeper.accounts) != 0

    record_keeper.remove_account("PARENT/TEST NAME")
    assert parent.children == ()
    assert record_keeper.accounts == ()


def test_remove_account_does_not_exist() -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(DoesNotExistError):
        record_keeper.remove_account("")


def test_remove_account_has_children() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("PARENT", None)
    parent = record_keeper.account_groups[0]

    record_keeper.add_security_account("TEST SENDER", "PARENT")
    record_keeper.add_security_account("TEST RECIPIENT", "PARENT")
    assert len(parent.children) != 0
    assert len(record_keeper.accounts) != 0

    record_keeper.add_currency("CZK", 2)
    record_keeper.add_security("NAME", "SYMB", SecurityType.ETF, "CZK", 1)
    sender_path = "PARENT/TEST SENDER"
    recipient_path = "PARENT/TEST RECIPIENT"
    record_keeper.add_security_transfer(
        "", datetime.now(tzinfo), "SYMB", Decimal(1), sender_path, recipient_path
    )

    with pytest.raises(InvalidOperationError):
        record_keeper.remove_account("PARENT/TEST SENDER")


def test_remove_account_group() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("PARENT", None)
    parent = record_keeper.account_groups[0]

    record_keeper.add_account_group("TEST NAME", "PARENT")
    assert len(parent.children) != 0
    assert len(record_keeper.account_groups) != 0

    record_keeper.remove_account_group("PARENT/TEST NAME")
    assert parent.children == ()
    assert record_keeper.account_groups == (parent,)


def test_remove_account_group_does_not_exist() -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(DoesNotExistError):
        record_keeper.remove_account_group("")


def test_remove_account_group_has_children() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("PARENT", None)
    parent = record_keeper.account_groups[0]

    record_keeper.add_account_group("TEST NAME", "PARENT")
    assert len(parent.children) != 0
    assert len(record_keeper.account_groups) != 0

    record_keeper.add_account_group("TEST CHILD", "PARENT/TEST NAME")

    with pytest.raises(InvalidOperationError):
        record_keeper.remove_account_group("PARENT/TEST NAME")


def test_remove_transactions() -> None:
    record_keeper = get_preloaded_record_keeper_with_various_transactions()
    assert record_keeper.transactions != ()
    refund_uuids = [
        str(transaction.uuid)
        for transaction in record_keeper.transactions
        if isinstance(transaction, RefundTransaction)
    ]
    record_keeper.remove_transactions(refund_uuids)
    refunds = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, RefundTransaction)
    ]
    assert refunds == []
    other_uuids = [str(transaction.uuid) for transaction in record_keeper.transactions]
    record_keeper.remove_transactions(other_uuids)
    assert record_keeper.transactions == ()


def test_remove_transactions_is_refunded() -> None:
    record_keeper = get_preloaded_record_keeper_with_various_transactions()
    assert record_keeper.transactions != ()
    refunded_transaction_uuids = [
        str(transaction.uuid)
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction) and transaction.is_refunded
    ]
    with pytest.raises(InvalidOperationError):
        record_keeper.remove_transactions(refunded_transaction_uuids)


def test_remove_security() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_security("NAME", "SYMB", SecurityType.ETF, "CZK", 1)
    assert len(record_keeper.securities) == 1
    record_keeper.remove_security("SYMB")
    assert record_keeper.securities == ()


def test_remove_security_referenced_in_transaction() -> None:
    record_keeper = get_preloaded_record_keeper_with_various_transactions()
    security = record_keeper.securities[0]
    with pytest.raises(InvalidOperationError):
        record_keeper.remove_security(security.symbol)


def test_remove_currency() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    assert len(record_keeper.currencies) == 1
    record_keeper.remove_currency("CZK")
    assert len(record_keeper.currencies) == 0


def test_remove_currency_referenced_in_security() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_security("NAME", "SYMB", SecurityType.ETF, "CZK", 1)
    with pytest.raises(InvalidOperationError):
        record_keeper.remove_currency("CZK")


def test_remove_currency_referenced_in_exchange_rate() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_currency("EUR", 2)
    record_keeper.add_exchange_rate("CZK", "EUR")
    with pytest.raises(InvalidOperationError):
        record_keeper.remove_currency("CZK")


def test_remove_currency_referenced_in_transaction() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_security_account("SECURITY ACC", None)
    record_keeper.add_cash_account(
        "CASH ACC", "CZK", 0, datetime.now(tzinfo) - timedelta(days=1), None
    )
    record_keeper.add_security("NAME", "SYMB", SecurityType.ETF, "CZK", 1)
    record_keeper.add_security_transaction(
        "",
        datetime.now(tzinfo),
        SecurityTransactionType.BUY,
        "SYMB",
        1,
        1,
        1,
        "SECURITY ACC",
        "CASH ACC",
    )
    with pytest.raises(InvalidOperationError):
        record_keeper.remove_currency("CZK")


def test_remove_exchange_rate() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_currency("EUR", 2)
    record_keeper.add_exchange_rate("CZK", "EUR")
    assert len(record_keeper.exchange_rates) == 1
    record_keeper.remove_exchange_rate("CZK/EUR")
    assert len(record_keeper.exchange_rates) == 0


def test_remove_exchange_rate_does_not_exist() -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(DoesNotExistError):
        record_keeper.remove_exchange_rate("CZK/EUR")
