from datetime import datetime
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st
from src.models.custom_exceptions import (
    AlreadyExistsError,
    InvalidOperationError,
    NotFoundError,
)
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    Category,
    CategoryType,
)
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import CashAmount, CurrencyError
from src.models.model_objects.security_objects import (
    SecurityTransaction,
    SecurityTransfer,
)
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from tests.models.test_assets.composites import attributes
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_cash_transactions,
    get_preloaded_record_keeper_with_cash_transfers,
    get_preloaded_record_keeper_with_refunds,
    get_preloaded_record_keeper_with_security_transactions,
)


def test_edit_category() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_category("TEST PARENT 1", CategoryType.EXPENSE)
    record_keeper.add_category("TEST PARENT 2", CategoryType.EXPENSE)
    record_keeper.add_category("TEST PARENT 1/TEST CAT")
    record_keeper.edit_category("TEST PARENT 1/TEST CAT", "TEST PARENT 2/NEW NAME")
    cat = record_keeper.get_category("TEST PARENT 2/NEW NAME")
    assert cat.name == "NEW NAME"
    assert cat.path == "TEST PARENT 2/NEW NAME"


def test_edit_category_move_from_root_with_index() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_category("TEST PARENT 1", CategoryType.EXPENSE)
    record_keeper.add_category("TEST PARENT 2", CategoryType.EXPENSE)
    record_keeper.add_category("TEST CAT", CategoryType.EXPENSE)
    record_keeper.edit_category("TEST CAT", "TEST PARENT 2/NEW NAME", 0)
    cat = record_keeper.get_category("TEST PARENT 2/NEW NAME")
    parent = cat.parent
    assert isinstance(parent, Category)
    assert cat.name == "NEW NAME"
    assert cat.path == "TEST PARENT 2/NEW NAME"
    assert parent.get_child_index(cat) == 0


def test_edit_category_move_to_root_with_index() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_category("TEST PARENT", CategoryType.EXPENSE)
    record_keeper.add_category("TEST PARENT/TEST CAT")
    record_keeper.edit_category("TEST PARENT/TEST CAT", "NEW NAME", 0)
    cat = record_keeper.get_category("NEW NAME")
    assert cat.name == "NEW NAME"
    assert cat.path == "NEW NAME"
    assert record_keeper.root_expense_categories[0].name == "NEW NAME"


def test_edit_category_remove_parent() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_category("TEST PARENT 1", CategoryType.EXPENSE)
    record_keeper.add_category("TEST PARENT 1/TEST CAT")
    record_keeper.edit_category("TEST PARENT 1/TEST CAT", "NEW NAME")
    cat = record_keeper.get_category("NEW NAME")
    assert cat.name == "NEW NAME"
    assert cat.path == "NEW NAME"


def test_edit_category_already_exists() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_category("TEST", CategoryType.EXPENSE)
    record_keeper.add_category("TEST 2", CategoryType.EXPENSE)
    with pytest.raises(AlreadyExistsError):
        record_keeper.edit_category("TEST", "TEST 2")


def test_edit_category_its_own_parent() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_category("TEST", CategoryType.EXPENSE)
    with pytest.raises(InvalidOperationError):
        record_keeper.edit_category("TEST", "TEST/TEST")


def test_edit_category_does_not_exist() -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(NotFoundError):
        record_keeper.edit_category("abc", "def")


def test_edit_payee() -> None:
    record_keeper = RecordKeeper()
    record_keeper._payees.append(Attribute("TEST NAME", AttributeType.PAYEE))
    record_keeper.edit_attribute("TEST NAME", "NEW NAME", AttributeType.PAYEE)
    attribute = record_keeper.payees[0]
    assert attribute.name == "NEW NAME"


def test_edit_tag() -> None:
    record_keeper = RecordKeeper()
    record_keeper._tags.append(Attribute("TEST NAME", AttributeType.TAG))
    record_keeper.edit_attribute("TEST NAME", "NEW NAME", AttributeType.TAG)
    attribute = record_keeper.tags[0]
    assert attribute.name == "NEW NAME"


def test_edit_attribute_does_not_exist() -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(NotFoundError):
        record_keeper.edit_attribute("abc", "def", AttributeType.PAYEE)


def test_edit_security() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_security("TEST NAME", "SMBL", "ETF", "CZK", 1)
    security = record_keeper.get_security_by_name("TEST NAME")
    record_keeper.edit_security(
        uuid=str(security.uuid), name="NEW NAME", symbol="NEWSYMB", type_="NEW TYPE"
    )
    security = record_keeper.securities[0]
    assert security.symbol == "NEWSYMB"
    assert security.name == "NEW NAME"
    assert security.type_ == "NEW TYPE"


def test_edit_security_does_not_exist() -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(NotFoundError):
        record_keeper.edit_security("SMBL", "SYMB", "NEW NAME")


def test_edit_security_account() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("TEST PARENT", None)
    record_keeper.add_account_group("NEW PARENT", None)
    record_keeper.add_security_account("TEST PARENT/TEST NAME")
    record_keeper.edit_security_account("TEST PARENT/TEST NAME", "NEW PARENT/NEW NAME")
    account = record_keeper.accounts[0]
    assert account.name == "NEW NAME"
    assert account.path == "NEW PARENT/NEW NAME"


def test_edit_security_account_does_not_exist() -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(NotFoundError):
        record_keeper.edit_security_account("ABC", "DEF")


def test_edit_security_account_already_exists() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_security_account("TEST")
    record_keeper.add_security_account("DUMMY")
    with pytest.raises(AlreadyExistsError):
        record_keeper.edit_security_account("TEST", "DUMMY")


def test_edit_security_account_group() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("TEST PARENT")
    record_keeper.add_account_group("TEST PARENT/TEST CHILD")
    record_keeper.add_account_group("NEW PARENT")
    record_keeper.edit_account_group("TEST PARENT/TEST CHILD", "NEW PARENT/NEW NAME")
    account_group = record_keeper.get_account_parent_or_none("NEW PARENT/NEW NAME")
    assert isinstance(account_group, AccountGroup)
    assert account_group.name == "NEW NAME"
    assert account_group.path == "NEW PARENT/NEW NAME"


def test_edit_security_account_group_index() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("TEST PARENT")
    record_keeper.add_account_group("TEST PARENT/DUMMY CHILD")
    record_keeper.add_account_group("TEST PARENT/TEST CHILD")
    record_keeper.add_account_group("NEW PARENT")
    record_keeper.edit_account_group(
        "TEST PARENT/TEST CHILD", "NEW PARENT/NEW NAME", index=0
    )
    account_group = record_keeper.get_account_parent("NEW PARENT/NEW NAME")
    parent = account_group.parent
    assert isinstance(parent, AccountGroup)
    assert account_group.name == "NEW NAME"
    assert account_group.path == "NEW PARENT/NEW NAME"
    assert parent.children[0] == account_group


def test_edit_security_account_group_index_no_parent() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("DUMMY CHILD")
    record_keeper.add_account_group("TEST CHILD")
    assert record_keeper.root_account_items[1].name == "TEST CHILD"
    record_keeper.edit_account_group("TEST CHILD", "TEST CHILD", index=0)
    assert record_keeper.root_account_items[0].name == "TEST CHILD"


def test_edit_security_account_group_from_root_to_children() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("TEST")
    record_keeper.add_account_group("DUMMY PARENT")
    assert len(record_keeper.root_account_items) == 2  # noqa: PLR2004
    record_keeper.edit_account_group("TEST", "DUMMY PARENT/TEST")
    assert len(record_keeper.root_account_items) == 1


def test_edit_security_account_group_from_child_to_root() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("DUMMY PARENT")
    record_keeper.add_account_group("DUMMY PARENT/TEST")
    assert len(record_keeper.root_account_items) == 1
    record_keeper.edit_account_group("DUMMY PARENT/TEST", "TEST")
    assert len(record_keeper.root_account_items) == 2  # noqa: PLR2004


def test_edit_security_account_group_already_exists() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("TEST")
    record_keeper.add_account_group("DUMMY")
    with pytest.raises(AlreadyExistsError):
        record_keeper.edit_account_group("TEST", "DUMMY")


def test_edit_security_account_group_does_not_exist() -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(NotFoundError):
        record_keeper.edit_account_group("ABC", "GHI/DEF")


def test_edit_security_account_group_invalid_parent() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("TEST")
    with pytest.raises(InvalidOperationError):
        record_keeper.edit_account_group("TEST", "TEST/XXX")


def test_edit_cash_account() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_account_group("TEST PARENT", None)
    record_keeper.add_account_group("NEW PARENT", None)
    record_keeper.add_cash_account("TEST PARENT/TEST NAME", "CZK", 0)
    record_keeper.edit_cash_account(
        "TEST PARENT/TEST NAME", "NEW PARENT/NEW NAME", 1000
    )
    account = record_keeper.accounts[0]
    assert isinstance(account, CashAccount)
    assert account.name == "NEW NAME"
    assert account.path == "NEW PARENT/NEW NAME"
    assert account.initial_balance.value_rounded == Decimal(1000)


def test_edit_cash_transactions_descriptions() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        and transaction.currency.code == "CZK"
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    edit_string = "TEST EDIT"
    record_keeper.edit_cash_transactions(uuids, description=edit_string)
    for transaction in cash_transactions:
        assert transaction.description == edit_string


def test_edit_cash_transactions_datetimes() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        and transaction.currency.code == "CZK"
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    edit_datetime = datetime.now(user_settings.settings.time_zone)
    record_keeper.edit_cash_transactions(uuids, datetime_=edit_datetime)
    for transaction in cash_transactions:
        assert transaction.datetime_ == edit_datetime


def test_edit_cash_transactions_payees() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        and transaction.currency.code == "CZK"
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    edit_payee = "TEST PAYEE"
    record_keeper.edit_cash_transactions(uuids, payee_name=edit_payee)
    for transaction in cash_transactions:
        assert transaction.payee.name == edit_payee


def test_edit_cash_transactions_categories() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        and transaction.currency.code == "CZK"
        and transaction.type_ == CashTransactionType.EXPENSE
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    edit_category = "TEST CATEGORY"
    edit_category_amount_pair = [(edit_category, None)]
    record_keeper.edit_cash_transactions(
        uuids, category_path_amount_pairs=edit_category_amount_pair
    )
    expenses = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        and transaction.type_ == CashTransactionType.EXPENSE
        and transaction.currency.code == "CZK"
    ]
    for transaction in expenses:
        assert transaction.category_amount_pairs[0][0].name == edit_category


def test_edit_cash_transactions_tags() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        and transaction.currency.code == "CZK"
        and transaction.type_ == CashTransactionType.EXPENSE
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    edit_tag = "TEST TAG"
    edit_tag_amount_pair = [(edit_tag, Decimal(1))]
    record_keeper.edit_cash_transactions(
        uuids, tag_name_amount_pairs=edit_tag_amount_pair
    )
    for transaction in cash_transactions:
        assert transaction.tag_amount_pairs[0][0].name == edit_tag


def test_edit_cash_transactions_account() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        and transaction.currency.code == "CZK"
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    edit_account = "Test Account CZK"
    record_keeper.add_cash_account(
        path="Test Account CZK",
        currency_code="CZK",
        initial_balance_value=Decimal(0),
    )
    record_keeper.edit_cash_transactions(uuids, account_path=edit_account)
    for transaction in cash_transactions:
        assert transaction.account.path == edit_account


def test_edit_cash_transactions_invalid_indexes() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    record_keeper.add_cash_transfer(
        "",
        datetime.now(user_settings.settings.time_zone),
        "Bank Accounts/Raiffeisen CZK",
        "Bank Accounts/Moneta EUR",
        1,
        1,
    )
    transactions = list(record_keeper.transactions)
    uuids = [str(transaction.uuid) for transaction in transactions]
    with pytest.raises(TypeError, match="Type of Transaction"):
        record_keeper.edit_cash_transactions(uuids)


def test_edit_cash_transactions_multiple_currencies() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    record_keeper.add_tag("test tag")
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        and transaction.type_ == CashTransactionType.EXPENSE
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    edit_description = "test description"
    edit_payee = record_keeper.payees[0].name
    edit_category_pair = ((record_keeper.categories[0].path, None),)
    edit_tag_pair = ((record_keeper.tags[1].name, None),)
    edit_datetime = datetime.now(user_settings.settings.time_zone)
    record_keeper.edit_cash_transactions(
        uuids,
        description=edit_description,
        payee_name=edit_payee,
        datetime_=edit_datetime,
        category_path_amount_pairs=edit_category_pair,
        tag_name_amount_pairs=edit_tag_pair,
    )
    for transaction in cash_transactions:
        assert transaction.description == edit_description
        assert transaction.payee.name == edit_payee
        assert transaction.datetime_ == edit_datetime
        assert record_keeper.categories[0] in transaction.categories
        assert record_keeper.tags[1] in transaction.tags


def test_edit_cash_transactions_multiple_currencies_invalid_account() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        and transaction.type_ == CashTransactionType.EXPENSE
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    with pytest.raises(ValueError, match="'account_path' must be None"):
        record_keeper.edit_cash_transactions(
            uuids, account_path=cash_transactions[0].account.path
        )


def test_edit_cash_transactions_multiple_currencies_invalid_category_amounts() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        and transaction.type_ == CashTransactionType.EXPENSE
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    with pytest.raises(ValueError, match="Category amounts must be None"):
        record_keeper.edit_cash_transactions(
            uuids, category_path_amount_pairs=cash_transactions[0].category_amount_pairs
        )


def test_edit_cash_transactions_multiple_currencies_invalid_tag_amounts() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        and transaction.type_ == CashTransactionType.EXPENSE
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    with pytest.raises(ValueError, match="Tag amounts must be None"):
        record_keeper.edit_cash_transactions(
            uuids, tag_name_amount_pairs=cash_transactions[0].tag_amount_pairs
        )


def test_edit_cash_transactions_multiple_types() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    with pytest.raises(InvalidOperationError):
        record_keeper.edit_cash_transactions(
            uuids, transaction_type=CashTransactionType.INCOME
        )


def test_edit_cash_transfer_invalid_types() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if not isinstance(transaction, CashTransfer)
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    with pytest.raises(TypeError, match="Type of Transaction"):
        record_keeper.edit_cash_transfers(uuids)


def test_edit_cash_transfer_description() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transfers()
    transfers = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransfer)
    ]
    uuids = [str(transfer.uuid) for transfer in transfers]
    edit_string = "TEST EDIT"
    record_keeper.edit_cash_transfers(uuids, description=edit_string)
    for transfer in transfers:
        assert transfer.description == edit_string


def test_edit_cash_transfer_datetime() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transfers()
    transfers = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransfer)
    ]
    uuids = [str(transfer.uuid) for transfer in transfers]
    edit_datetime = datetime.now(user_settings.settings.time_zone)
    record_keeper.edit_cash_transfers(uuids, datetime_=edit_datetime)
    for transfer in transfers:
        assert transfer.datetime_ == edit_datetime


def test_edit_cash_transfer_sender() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transfers()
    edit_sender = "Bank Accounts/Raiffeisen CZK"
    transfers = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransfer)
        and transaction.recipient.path != edit_sender
        and transaction.sender.currency.code == "CZK"
    ]
    uuids = [str(transfer.uuid) for transfer in transfers]
    record_keeper.edit_cash_transfers(uuids, sender_path=edit_sender)
    for transfer in transfers:
        assert transfer.sender.path == edit_sender


def test_edit_cash_transfer_recipient() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transfers()
    edit_recipient = "Bank Accounts/Raiffeisen CZK"
    transfers = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransfer)
        and transaction.sender.path != edit_recipient
        and transaction.recipient.currency.code == "CZK"
    ]
    uuids = [str(transfer.uuid) for transfer in transfers]
    record_keeper.edit_cash_transfers(uuids, recipient_path=edit_recipient)
    for transfer in transfers:
        assert transfer.recipient.path == edit_recipient


def test_edit_cash_transfer_amount_sent() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transfers()
    edit_amount_sent = Decimal(1)
    transfers = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransfer)
        and transaction.sender.currency.code == "CZK"
    ]
    uuids = [str(transfer.uuid) for transfer in transfers]
    record_keeper.edit_cash_transfers(uuids, amount_sent=edit_amount_sent)
    for transfer in transfers:
        assert transfer.amount_sent.value_rounded == edit_amount_sent


def test_edit_cash_transfer_amount_received() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transfers()
    edit_amount_received = Decimal(1)
    transfers = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransfer)
        and transaction.recipient.currency.code == "CZK"
    ]
    uuids = [str(transfer.uuid) for transfer in transfers]
    record_keeper.edit_cash_transfers(uuids, amount_received=edit_amount_received)
    for transfer in transfers:
        assert transfer.amount_received.value_rounded == edit_amount_received


def test_edit_cash_transfer_amount_sent_currency_not_same() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transfers()
    edit_amount_sent = Decimal(1)
    transfers = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransfer)
    ]
    uuids = [str(transfer.uuid) for transfer in transfers]
    with pytest.raises(CurrencyError):
        record_keeper.edit_cash_transfers(uuids, amount_sent=edit_amount_sent)


def test_edit_cash_transfer_amounts_currencies_not_same() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transfers()
    edit_sender = record_keeper.accounts[0]
    edit_recipient = record_keeper.accounts[1]
    edit_amount_sent = Decimal(1)
    edit_amount_received = Decimal(1)
    transfers = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransfer)
    ]
    uuids = [str(transfer.uuid) for transfer in transfers]
    record_keeper.edit_cash_transfers(
        uuids,
        amount_sent=edit_amount_sent,
        amount_received=edit_amount_received,
        sender_path=edit_sender.path,
        recipient_path=edit_recipient.path,
    )
    for transfer in transfers:
        assert transfer.amount_sent.value_normalized == edit_amount_sent
        assert transfer.amount_received.value_normalized == edit_amount_received
        assert transfer.sender == edit_sender
        assert transfer.recipient == edit_recipient


def test_edit_cash_transfer_amount_received_currency_not_same() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transfers()
    edit_amount_received = Decimal(1)
    transfers = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransfer)
    ]
    uuids = [str(transfer.uuid) for transfer in transfers]
    with pytest.raises(CurrencyError):
        record_keeper.edit_cash_transfers(uuids, amount_received=edit_amount_received)


def test_edit_refunds_same_values() -> None:
    record_keeper = get_preloaded_record_keeper_with_refunds()
    refunds = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, RefundTransaction)
        and transaction.currency.code == "CZK"
    ]
    uuids = [str(transfer.uuid) for transfer in refunds]
    record_keeper.edit_refunds(uuids)


def test_edit_refunds_invalid_transaction_types() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    transactions = record_keeper.transactions
    uuids = [str(transfer.uuid) for transfer in transactions]
    with pytest.raises(TypeError, match="Type of Transaction"):
        record_keeper.edit_refunds(uuids)


def test_edit_refunds_currency_not_same() -> None:
    record_keeper = get_preloaded_record_keeper_with_refunds()
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, RefundTransaction)
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    with pytest.raises(CurrencyError):
        record_keeper.edit_refunds(uuids)


def test_edit_refunds_change_account() -> None:
    record_keeper = get_preloaded_record_keeper_with_refunds()
    edit_account_path = "Bank Accounts/Fio CZK"
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, RefundTransaction)
        and transaction.currency.code == "CZK"
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    record_keeper.edit_refunds(uuids, account_path=edit_account_path)
    for transaction in transactions:
        assert transaction.account.path == edit_account_path


def test_edit_refunds_change_payee() -> None:
    record_keeper = get_preloaded_record_keeper_with_refunds()
    edit_payee = "TEST PAYEE"
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, RefundTransaction)
        and transaction.currency.code == "CZK"
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    record_keeper.edit_refunds(uuids, payee_name=edit_payee)
    for transaction in transactions:
        assert transaction.payee.name == edit_payee


def test_edit_refunds_change_tag_amounts() -> None:
    record_keeper = get_preloaded_record_keeper_with_refunds()
    edit_category_amount_pairs = [("Food and Drink/Groceries", Decimal(250))]
    edit_tag_amount_pairs = [("Test Tag", Decimal(250))]
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, RefundTransaction)
        and transaction.currency.code == "CZK"
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    record_keeper.edit_refunds(
        uuids,
        category_path_amount_pairs=edit_category_amount_pairs,
        tag_name_amount_pairs=edit_tag_amount_pairs,
    )
    for transaction in transactions:
        assert transaction.tag_amount_pairs == (
            (
                (
                    transaction.tag_amount_pairs[0][0],
                    CashAmount(250, transaction.currency),
                )
            ),
        )


def test_edit_security_transactions_same_values() -> None:
    record_keeper = get_preloaded_record_keeper_with_security_transactions()
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, SecurityTransaction)
        and transaction.currency.code == "EUR"
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    record_keeper.edit_security_transactions(uuids)


def test_edit_security_transactions_invalid_transaction_types() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    transactions = record_keeper.transactions
    uuids = [str(transfer.uuid) for transfer in transactions]
    with pytest.raises(TypeError, match="Type of Transaction"):
        record_keeper.edit_security_transactions(uuids)


def test_edit_security_transactions_currency_not_same() -> None:
    record_keeper = get_preloaded_record_keeper_with_security_transactions()
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, SecurityTransaction)
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    with pytest.raises(CurrencyError):
        record_keeper.edit_security_transactions(uuids)


def test_edit_security_transactions_change_symbol() -> None:
    edit_name = "iShares MSCI World"
    record_keeper = get_preloaded_record_keeper_with_security_transactions()
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, SecurityTransaction)
        and transaction.security.symbol == "VWCE.DE"
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    security = record_keeper.get_security_by_name(edit_name)
    record_keeper.edit_security_transactions(uuids, security_name=security.name)
    for transaction in transactions:
        assert transaction.security.name == edit_name


def test_edit_security_transactions_change_cash_account() -> None:
    edit_cash_account = "Bank Accounts/Revolut EUR"
    record_keeper = get_preloaded_record_keeper_with_security_transactions()
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, SecurityTransaction)
        and transaction.security.symbol == "VWCE.DE"
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    record_keeper.edit_security_transactions(uuids, cash_account_path=edit_cash_account)
    for transaction in transactions:
        assert transaction.cash_account.path == edit_cash_account


def test_edit_security_transactions_change_security_account() -> None:
    edit_security_account = "Security Accounts/Degiro"
    record_keeper = get_preloaded_record_keeper_with_security_transactions()
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, SecurityTransaction)
        and transaction.security.symbol == "VWCE.DE"
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    record_keeper.edit_security_transactions(
        uuids, security_account_path=edit_security_account
    )
    for transaction in transactions:
        assert transaction.security_account.path == edit_security_account


def test_edit_security_transactions_change_price_per_share() -> None:
    edit_price = Decimal(1)
    record_keeper = get_preloaded_record_keeper_with_security_transactions()
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, SecurityTransaction)
        and transaction.security.symbol == "VWCE.DE"
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    record_keeper.edit_security_transactions(uuids, price_per_share=edit_price)
    for transaction in transactions:
        assert transaction.price_per_share.value_rounded == edit_price


def test_edit_security_transactions_change_shares() -> None:
    edit_shares = Decimal(1)
    record_keeper = get_preloaded_record_keeper_with_security_transactions()
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, SecurityTransaction)
        and transaction.security.symbol == "VWCE.DE"
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    record_keeper.edit_security_transactions(uuids, shares=edit_shares)
    for transaction in transactions:
        assert transaction.shares == edit_shares


def test_edit_security_transfers_same_values() -> None:
    record_keeper = get_preloaded_record_keeper_with_security_transactions()
    tansfers = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, SecurityTransfer)
    ]
    uuids = [str(transfer.uuid) for transfer in tansfers]
    record_keeper.edit_security_transfers(uuids)


def test_edit_security_transfers_invalid_transaction_types() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    transactions = record_keeper.transactions
    uuids = [str(transfer.uuid) for transfer in transactions]
    with pytest.raises(TypeError, match="Type of Transaction"):
        record_keeper.edit_security_transfers(uuids)


def test_edit_security_transfers_change_symbol() -> None:
    edit_name = "iShares MSCI World"
    record_keeper = get_preloaded_record_keeper_with_security_transactions()
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, SecurityTransfer)
        and transaction.security.symbol == "VWCE.DE"
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    record_keeper.edit_security_transfers(uuids, security_name=edit_name)
    for transaction in transactions:
        assert transaction.security.name == edit_name


def test_edit_security_transactions_change_security_accounts() -> None:
    edit_sender = "Security Accounts/Degiro"
    edit_recipient = "Security Accounts/Interactive Brokers"
    record_keeper = get_preloaded_record_keeper_with_security_transactions()
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, SecurityTransfer)
        and transaction.security.symbol == "VWCE.DE"
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    record_keeper.edit_security_transfers(
        uuids, sender_path=edit_sender, recipient_path=edit_recipient
    )
    for transaction in transactions:
        assert transaction.sender.path == edit_sender
        assert transaction.recipient.path == edit_recipient


@given(tags=st.lists(attributes(AttributeType.TAG), min_size=1, max_size=5))
def test_add_and_remove_tags_to_transactions(tags: list[Attribute]) -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    valid_tags: list[Attribute] = []
    for tag in tags:
        if any(tag.name == other.name for other in valid_tags):
            continue
        valid_tags.append(tag)

    for tag in valid_tags:
        record_keeper._tags.append(tag)
    tag_names = [tag.name for tag in valid_tags]
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if not isinstance(transaction, RefundTransaction)
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    record_keeper.add_tags_to_transactions(uuids, tag_names)
    for transaction in transactions:
        for tag in valid_tags:
            assert tag in transaction.tags
    for tag in valid_tags:
        record_keeper.remove_tags_from_transactions(uuids, [tag.name])
        for transaction in transactions:
            assert tag not in transaction.tags


@given(tags=st.lists(attributes(AttributeType.TAG), min_size=1, max_size=5))
def test_add_and_remove_tags_empty_uuid(tags: list[Attribute]) -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    for tag in tags:
        record_keeper._tags.append(tag)
    tag_names = [tag.name for tag in tags]
    record_keeper.add_tags_to_transactions([], tag_names)
