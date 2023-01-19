import json
from datetime import datetime
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.custom_exceptions import NotFoundError
from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
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
    CashTransfer,
)
from src.models.model_objects.currency import CashAmount, Currency, ExchangeRate
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityType,
)
from src.models.record_keeper import RecordKeeper
from tests.models.test_assets.composites import (
    attributes,
    cash_transactions,
    cash_transfers,
    categories,
)


def test_invalid_object() -> None:
    with pytest.raises(TypeError, match="not JSON serializable"):
        json.dumps(object, cls=CustomJSONEncoder)


def test_decimal() -> None:
    number = Decimal("1.234")
    serialized = json.dumps(number, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert decoded == number


def test_datetime() -> None:
    dt = datetime.now(tzinfo)
    serialized = json.dumps(dt, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert decoded == dt


def test_currency() -> None:
    currency = Currency("CZK", 2)
    serialized = json.dumps(currency, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert decoded == currency


def test_exchange_rate() -> None:
    primary = Currency("EUR", 2)
    secondary = Currency("CZK", 2)
    exchange_rate = ExchangeRate(primary, secondary)
    serialized = json.dumps(exchange_rate, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = ExchangeRate.from_dict(decoded, [primary, secondary])
    assert isinstance(decoded, ExchangeRate)
    assert decoded.primary_currency == exchange_rate.primary_currency
    assert decoded.secondary_currency == exchange_rate.secondary_currency


def test_cash_amount() -> None:
    currency = Currency("EUR", 2)
    cash_amount = CashAmount(Decimal("1.23"), currency)
    serialized = json.dumps(cash_amount, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = CashAmount.from_dict(decoded, [currency])
    assert decoded == cash_amount


def test_cash_amount_currency_not_found() -> None:
    currency = Currency("EUR", 2)
    cash_amount = CashAmount(Decimal("1.23"), currency)
    serialized = json.dumps(cash_amount, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    with pytest.raises(NotFoundError):
        CashAmount.from_dict(decoded, [])


@given(attribute=attributes())
def test_attribute(attribute: Attribute) -> None:
    serialized = json.dumps(attribute, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, Attribute)
    assert decoded.name == attribute.name
    assert decoded.type_ == attribute.type_


@given(parent=categories(), data=st.data())
def test_category(parent: Category, data: st.DataObject) -> None:
    child_1 = data.draw(categories(category_type=parent.type_))
    child_2 = data.draw(categories(category_type=parent.type_))
    child_1.parent = parent
    child_2.parent = parent
    category_tuple = (parent, child_1, child_2)
    serialized = json.dumps(category_tuple, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    category_list = []
    for category_dict in decoded:
        category = Category.from_dict(category_dict, category_list)
        category_list.append(category)
    decoded = category_list[0]
    assert isinstance(decoded, Category)
    assert decoded.name == parent.name
    assert decoded.type_ == parent.type_
    assert decoded.children[0].name == child_1.name
    assert decoded.children[0].parent == decoded
    assert decoded.children[1].name == child_2.name
    assert decoded.children[1].parent == decoded


@given(parent=categories(), data=st.data())
def test_category_parent_not_found(parent: Category, data: st.DataObject) -> None:
    child = data.draw(categories(category_type=parent.type_))
    child.parent = parent
    category_tuple = (child,)
    serialized = json.dumps(category_tuple, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    with pytest.raises(NotFoundError):
        Category.from_dict(decoded[0], category_tuple)


def test_account_group() -> None:
    parent = AccountGroup("Test Name")
    child_1 = AccountGroup("Child 1", parent)
    child_2 = AccountGroup("Child 2", parent)
    child_1.parent = parent
    child_2.parent = parent
    account_groups = [parent, child_1, child_2]
    serialized = json.dumps(account_groups, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    account_groups = []
    for account_group_dict in decoded:
        account_group = AccountGroup.from_dict(account_group_dict, account_groups)
        account_groups.append(account_group)
    decoded = account_groups[0]
    assert isinstance(decoded, AccountGroup)
    assert decoded.name == parent.name
    assert decoded.children[0].name == child_1.name
    assert decoded.children[0].parent == decoded
    assert decoded.children[1].name == child_2.name
    assert decoded.children[1].parent == decoded


def test_account_group_parent_not_found() -> None:
    parent = AccountGroup("Test Name")
    child = AccountGroup("Child 1", parent)
    child.parent = parent
    account_groups = [child]
    serialized = json.dumps(account_groups, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    with pytest.raises(NotFoundError):
        AccountGroup.from_dict(decoded[0], account_groups)


def test_cash_account() -> None:
    currency = Currency("CZK", 2)
    cash_account = CashAccount(
        "Test Name", currency, CashAmount(0, currency), datetime.now(tzinfo)
    )
    serialized = json.dumps(cash_account, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = CashAccount.from_dict(decoded, None, [currency])
    assert isinstance(decoded, CashAccount)
    assert decoded.name == cash_account.name
    assert decoded.currency == cash_account.currency
    assert decoded.initial_balance == cash_account.initial_balance
    assert decoded.initial_datetime == cash_account.initial_datetime
    assert decoded.uuid == cash_account.uuid


def test_cash_account_parent_not_found() -> None:
    currency = Currency("CZK", 2)
    parent = AccountGroup("Test Name")
    child = CashAccount(
        "Child Account", currency, CashAmount(0, currency), datetime.now(tzinfo)
    )
    child.parent = parent
    account_groups = [child]
    serialized = json.dumps(child, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    with pytest.raises(NotFoundError):
        CashAccount.from_dict(decoded, account_groups, [currency])


def test_cash_account_currency_not_found() -> None:
    currency = Currency("CZK", 2)
    parent = AccountGroup("Test Name")
    child = CashAccount(
        "Child Account", currency, CashAmount(0, currency), datetime.now(tzinfo)
    )
    child.parent = parent
    account_groups = [parent]
    serialized = json.dumps(child, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    with pytest.raises(NotFoundError):
        CashAccount.from_dict(decoded, account_groups, [])


def test_security_account() -> None:
    security_account = SecurityAccount("Test Name")
    serialized = json.dumps(security_account, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = SecurityAccount.from_dict(decoded, None)
    assert isinstance(decoded, SecurityAccount)
    assert decoded.name == security_account.name
    assert decoded.uuid == security_account.uuid


def test_security_account_parent_not_found() -> None:
    parent = AccountGroup("Test Name")
    child = SecurityAccount("Child Account")
    child.parent = parent
    account_groups = [child]
    serialized = json.dumps(account_groups, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    with pytest.raises(NotFoundError):
        SecurityAccount.from_dict(decoded[0], account_groups)


def test_security() -> None:
    currency = Currency("CZK", 2)
    security = Security("Test Name", "SYMB.OL", SecurityType.ETF, currency, 1)
    serialized = json.dumps(security, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = Security.from_dict(decoded, [currency])
    assert isinstance(decoded, Security)
    assert decoded.name == security.name
    assert decoded.symbol == security.symbol
    assert decoded.currency == security.currency
    assert decoded.type_ == security.type_
    assert decoded.shares_unit == security.shares_unit
    assert decoded.price_places == security.price_places
    assert decoded.uuid == security.uuid


def test_security_currency_not_found() -> None:
    currency = Currency("CZK", 2)
    security = Security("Test Name", "SYMB.OL", SecurityType.ETF, currency, 1)
    serialized = json.dumps(security, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    with pytest.raises(NotFoundError):
        Security.from_dict(decoded, [])


def test_record_keeper_currencies_exchange_rates() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_currency("EUR", 2)
    record_keeper.add_currency("USD", 2)
    record_keeper.add_exchange_rate("EUR", "CZK")
    record_keeper.add_exchange_rate("USD", "EUR")
    serialized = json.dumps(record_keeper, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, RecordKeeper)
    assert decoded.currencies == decoded.currencies
    assert str(decoded.exchange_rates[0]) == str(record_keeper.exchange_rates[0])
    assert str(decoded.exchange_rates[1]) == str(record_keeper.exchange_rates[1])


def test_record_keeper_account_groups() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("A1", None)
    record_keeper.add_account_group("A2", "A1")
    record_keeper.add_account_group("B2", "A1")
    record_keeper.add_account_group("A3", "A1/A2")
    record_keeper.add_account_group("B1", None)
    record_keeper.add_account_group("C1", None)
    serialized = json.dumps(record_keeper, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, RecordKeeper)
    assert len(record_keeper.account_groups) == len(decoded.account_groups)


def test_record_keeper_accounts() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_currency("EUR", 2)
    record_keeper.add_account_group("Security Accounts", None)
    record_keeper.add_account_group("Cash Accounts", None)
    record_keeper.add_cash_account(
        "CZK Account", "CZK", 0, datetime.now(tzinfo), "Cash Accounts"
    )
    record_keeper.add_cash_account(
        "EUR Account", "EUR", 0, datetime.now(tzinfo), "Cash Accounts"
    )
    record_keeper.add_security_account("Degiro", "Security Accounts")
    serialized = json.dumps(record_keeper, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, RecordKeeper)
    assert len(record_keeper.accounts) == len(decoded.accounts)


def test_record_keeper_invalid_account_datatype() -> None:
    record_keeper = RecordKeeper()
    dictionary = {"datatype": "not a valid Account sub-class"}
    with pytest.raises(ValueError, match="Unexpected 'datatype' value."):
        record_keeper.accounts_from_dicts([dictionary], None, None)


def test_record_keeper_securities() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_currency("EUR", 2)
    record_keeper.add_security(
        "iShares MSCI All World", "IWDA.AS", SecurityType.ETF, "EUR", 1
    )
    record_keeper.add_security(
        "ČSOB Dynamický penzijní fond", "CSOB.DYN", SecurityType.MUTUAL_FUND, "CZK", 1
    )
    serialized = json.dumps(record_keeper, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, RecordKeeper)
    assert len(record_keeper.securities) == len(decoded.securities)


@given(
    tags=st.lists(attributes(AttributeType.TAG), min_size=1, max_size=5),
    payees=st.lists(attributes(AttributeType.PAYEE), min_size=1, max_size=5),
)
def test_record_keeper_tags_and_payees(
    tags: list[Attribute], payees: list[Attribute]
) -> None:
    record_keeper = RecordKeeper()
    record_keeper._tags = tags
    record_keeper._payees = payees
    serialized = json.dumps(record_keeper, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, RecordKeeper)
    assert len(record_keeper.tags) == len(decoded.tags)
    assert len(record_keeper.payees) == len(decoded.payees)


def test_record_keeper_categories() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_category("Food", None, CategoryType.EXPENSE)
    record_keeper.add_category("Groceries", "Food", CategoryType.EXPENSE)
    record_keeper.add_category("Eating out", "Food", CategoryType.EXPENSE)
    record_keeper.add_category("Housing", None, CategoryType.EXPENSE)
    record_keeper.add_category("Rent", "Housing", CategoryType.EXPENSE)
    record_keeper.add_category("Electricity", "Housing", CategoryType.EXPENSE)
    record_keeper.add_category("Water", "Housing", CategoryType.EXPENSE)
    record_keeper.add_category("Work lunch", "Food", CategoryType.EXPENSE)
    serialized = json.dumps(record_keeper, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, RecordKeeper)
    assert len(record_keeper.categories) == len(decoded.categories)


@given(transaction=cash_transactions())
def test_cash_transaction(transaction: CashTransaction) -> None:
    serialized = json.dumps(transaction, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = CashTransaction.from_dict(
        decoded,
        [transaction.account],
        [transaction.payee],
        transaction.categories,
        transaction.tags,
        [transaction.currency],
    )
    assert isinstance(decoded, CashTransaction)
    assert decoded.uuid == transaction.uuid
    assert decoded.description == transaction.description
    assert decoded.datetime_ == transaction.datetime_
    assert decoded.datetime_created == transaction.datetime_created
    assert decoded.type_ == transaction.type_
    assert decoded.account == transaction.account
    assert transaction.payee == transaction.payee
    assert transaction.category_amount_pairs == transaction.category_amount_pairs
    assert transaction.tag_amount_pairs == transaction.tag_amount_pairs


@given(transaction=cash_transactions())
def test_cash_transaction_account_not_found(transaction: CashTransaction) -> None:
    serialized = json.dumps(transaction, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    with pytest.raises(NotFoundError):
        CashTransaction.from_dict(
            decoded,
            [],
            [transaction.payee],
            transaction.categories,
            transaction.tags,
            [transaction.currency],
        )


@given(transaction=cash_transactions())
def test_cash_transaction_payee_not_found(transaction: CashTransaction) -> None:
    serialized = json.dumps(transaction, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    with pytest.raises(NotFoundError):
        CashTransaction.from_dict(
            decoded,
            [transaction.account],
            [],
            transaction.categories,
            transaction.tags,
            [transaction.currency],
        )


@given(transaction=cash_transactions())
def test_cash_transaction_category_not_found(transaction: CashTransaction) -> None:
    serialized = json.dumps(transaction, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    with pytest.raises(NotFoundError):
        CashTransaction.from_dict(
            decoded,
            [transaction.account],
            [transaction.payee],
            [],
            transaction.tags,
            [transaction.currency],
        )


@given(transaction=cash_transactions())
def test_cash_transaction_tag_not_found(transaction: CashTransaction) -> None:
    transaction.set_attributes(
        tag_amount_pairs=[
            (
                Attribute("tag", AttributeType.TAG),
                transaction.amount,
            )
        ]
    )
    serialized = json.dumps(transaction, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    with pytest.raises(NotFoundError):
        CashTransaction.from_dict(
            decoded,
            [transaction.account],
            [transaction.payee],
            transaction.categories,
            [],
            [transaction.currency],
        )


@given(transaction=cash_transfers())
def test_cash_transfer(transaction: CashTransfer) -> None:
    serialized = json.dumps(transaction, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = CashTransfer.from_dict(
        decoded,
        [transaction.sender, transaction.recipient],
        transaction.currencies,
    )
    assert isinstance(decoded, CashTransfer)
    assert decoded.uuid == transaction.uuid
    assert decoded.description == transaction.description
    assert decoded.datetime_ == transaction.datetime_
    assert decoded.datetime_created == transaction.datetime_created
    assert decoded.sender == transaction.sender
    assert decoded.recipient == transaction.recipient
    assert decoded.amount_sent == transaction.amount_sent
    assert decoded.amount_received == transaction.amount_received


@given(transaction=cash_transfers())
def test_cash_transfer_account_not_found(transaction: CashTransfer) -> None:
    serialized = json.dumps(transaction, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    with pytest.raises(NotFoundError):
        CashTransfer.from_dict(
            decoded,
            [],
            transaction.currencies,
        )
