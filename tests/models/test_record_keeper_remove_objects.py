from datetime import datetime
from decimal import Decimal

import pytest

from src.models.constants import tzinfo
from src.models.custom_exceptions import InvalidOperationError, NotFoundError
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    Category,
    CategoryType,
)
from src.models.model_objects.cash_objects import (
    CashTransaction,
    CashTransactionType,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import Currency
from src.models.model_objects.security_objects import SecurityTransactionType
from src.models.record_keeper import RecordKeeper
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_remove_account() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("PARENT", None)
    parent = record_keeper.account_groups[0]

    record_keeper.add_security_account("PARENT/TEST NAME")
    assert len(parent.children) != 0
    assert len(record_keeper.accounts) != 0

    record_keeper.remove_account("PARENT/TEST NAME")
    assert parent.children == ()
    assert record_keeper.accounts == ()


def test_remove_account_no_parent() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_security_account("TEST NAME")
    assert len(record_keeper.accounts) != 0
    assert len(record_keeper.root_account_items) != 0

    record_keeper.remove_account("TEST NAME")
    assert record_keeper.accounts == ()
    assert record_keeper.root_account_items == ()


def test_remove_account_does_not_exist() -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(NotFoundError):
        record_keeper.remove_account("")


def test_remove_account_has_children() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("PARENT", None)
    parent = record_keeper.account_groups[0]

    record_keeper.add_security_account("PARENT/TEST SENDER")
    record_keeper.add_security_account("PARENT/TEST RECIPIENT")
    assert len(parent.children) != 0
    assert len(record_keeper.accounts) != 0

    record_keeper.add_currency("CZK", 2)
    record_keeper.add_security("NAME", "SYMB", "ETF", "CZK", 1)
    sender_path = "PARENT/TEST SENDER"
    recipient_path = "PARENT/TEST RECIPIENT"
    record_keeper.add_security_transfer(
        "", datetime.now(tzinfo), "NAME", Decimal(1), sender_path, recipient_path
    )

    with pytest.raises(InvalidOperationError):
        record_keeper.remove_account("PARENT/TEST SENDER")


def test_remove_account_group() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("PARENT")
    parent = record_keeper.account_groups[0]

    record_keeper.add_account_group("PARENT/TEST NAME")
    assert len(parent.children) != 0
    assert len(record_keeper.account_groups) != 0

    record_keeper.remove_account_group("PARENT/TEST NAME")
    assert parent.children == ()
    assert record_keeper.account_groups == (parent,)


def test_remove_account_group_no_parent() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("TEST NAME")
    assert len(record_keeper.account_groups) != 0
    assert len(record_keeper.root_account_items) != 0

    record_keeper.remove_account_group("TEST NAME")
    assert record_keeper.account_groups == ()
    assert record_keeper.root_account_items == ()


def test_remove_account_group_does_not_exist() -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(NotFoundError):
        record_keeper.remove_account_group("")


def test_remove_account_group_has_children() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("PARENT")
    parent = record_keeper.account_groups[0]

    record_keeper.add_account_group("PARENT/TEST NAME")
    assert len(parent.children) != 0
    assert len(record_keeper.account_groups) != 0

    record_keeper.add_account_group("PARENT/TEST NAME/TEST CHILD")

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
    record_keeper.add_security("NAME", "SYMB", "ETF", "CZK", 1)
    security = record_keeper.get_security_by_name("NAME")
    assert len(record_keeper.securities) == 1
    record_keeper.remove_security(str(security.uuid))
    assert record_keeper.securities == ()


def test_remove_security_referenced_in_transaction() -> None:
    record_keeper = get_preloaded_record_keeper_with_various_transactions()
    security = record_keeper.securities[0]
    with pytest.raises(InvalidOperationError):
        record_keeper.remove_security(str(security.uuid))


def test_remove_currency() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    base_currency: Currency = record_keeper.base_currency
    assert len(record_keeper.currencies) == 1
    assert base_currency.code == "CZK"
    record_keeper.remove_currency("CZK")
    assert len(record_keeper.currencies) == 0
    assert record_keeper.base_currency is None


def test_remove_currency_referenced_in_security() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_security("NAME", "SYMB", "ETF", "CZK", 1)
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
    record_keeper.add_cash_account("CASH ACC", "CZK", 0, None)
    record_keeper.add_security("NAME", "SYMB", "ETF", "CZK", 1)
    record_keeper.add_security_transaction(
        "",
        datetime.now(tzinfo),
        SecurityTransactionType.BUY,
        "NAME",
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
    with pytest.raises(NotFoundError):
        record_keeper.remove_exchange_rate("CZK/EUR")


def test_remove_tag() -> None:
    record_keeper = RecordKeeper()
    record_keeper._tags.append(Attribute("TAG", AttributeType.TAG))
    record_keeper.remove_tag("TAG")
    assert len(record_keeper.tags) == 0


def test_remove_tag_in_transaction() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_cash_account("ACCOUNT", "CZK", 0, None)
    record_keeper.add_cash_transaction(
        "",
        datetime.now(tzinfo),
        CashTransactionType.EXPENSE,
        "ACCOUNT",
        [("Category", Decimal(1))],
        "PAYEE",
        [(("TAG"), Decimal(1))],
    )
    with pytest.raises(InvalidOperationError):
        record_keeper.remove_tag("TAG")


def test_remove_payee() -> None:
    record_keeper = RecordKeeper()
    record_keeper._payees.append(Attribute("PAYEE", AttributeType.PAYEE))
    record_keeper.remove_payee("PAYEE")
    assert len(record_keeper.tags) == 0


def test_remove_payee_in_transaction() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_cash_account("ACCOUNT", "CZK", 0, None)
    record_keeper.add_cash_transaction(
        "",
        datetime.now(tzinfo),
        CashTransactionType.EXPENSE,
        "ACCOUNT",
        [("Category", Decimal(1))],
        "PAYEE",
        [(("TAG"), Decimal(1))],
    )
    with pytest.raises(InvalidOperationError):
        record_keeper.remove_payee("PAYEE")


def test_remove_category() -> None:
    record_keeper = RecordKeeper()
    record_keeper._categories.append(Category("CATEGORY", CategoryType.EXPENSE, None))
    record_keeper.remove_category("CATEGORY")
    assert len(record_keeper.tags) == 0


def test_remove_category_in_transaction() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_cash_account("ACCOUNT", "CZK", 0, None)
    record_keeper.add_cash_transaction(
        "",
        datetime.now(tzinfo),
        CashTransactionType.EXPENSE,
        "ACCOUNT",
        [("Category", Decimal(1))],
        "PAYEE",
        [(("TAG"), Decimal(1))],
    )
    with pytest.raises(InvalidOperationError):
        record_keeper.remove_category("Category")
