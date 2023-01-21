import json
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.models.constants import tzinfo
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
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import CashAmount, Currency, ExchangeRate
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
    SecurityType,
)
from src.models.record_keeper import RecordKeeper
from tests.models.test_assets.composites import (
    attributes,
    cash_transactions,
    cash_transfers,
    categories,
    security_transactions,
    security_transfers,
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
    decoded = ExchangeRate.deserialize(decoded, [primary, secondary])
    assert isinstance(decoded, ExchangeRate)
    assert decoded.primary_currency == exchange_rate.primary_currency
    assert decoded.secondary_currency == exchange_rate.secondary_currency


def test_cash_amount() -> None:
    currency = Currency("EUR", 2)
    cash_amount = CashAmount(Decimal("1.23"), currency)
    serialized = json.dumps(cash_amount, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = CashAmount.deserialize(decoded, [currency])
    assert decoded == cash_amount


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
        category = Category.deserialize(category_dict, category_list)
        category_list.append(category)
    decoded = category_list[0]
    assert isinstance(decoded, Category)
    assert decoded.name == parent.name
    assert decoded.type_ == parent.type_
    assert decoded.children[0].name == child_1.name
    assert decoded.children[0].parent == decoded
    assert decoded.children[1].name == child_2.name
    assert decoded.children[1].parent == decoded


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
        account_group = AccountGroup.deserialize(account_group_dict, account_groups)
        account_groups.append(account_group)
    decoded = account_groups[0]
    assert isinstance(decoded, AccountGroup)
    assert decoded.name == parent.name
    assert decoded.children[0].name == child_1.name
    assert decoded.children[0].parent == decoded
    assert decoded.children[1].name == child_2.name
    assert decoded.children[1].parent == decoded


def test_cash_account() -> None:
    currency = Currency("CZK", 2)
    cash_account = CashAccount(
        "Test Name", currency, CashAmount(0, currency), datetime.now(tzinfo)
    )
    serialized = json.dumps(cash_account, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = CashAccount.deserialize(decoded, None, [currency])
    assert isinstance(decoded, CashAccount)
    assert decoded.name == cash_account.name
    assert decoded.currency == cash_account.currency
    assert decoded.initial_balance == cash_account.initial_balance
    assert decoded.initial_datetime == cash_account.initial_datetime
    assert decoded.uuid == cash_account.uuid


def test_security_account() -> None:
    security_account = SecurityAccount("Test Name")
    serialized = json.dumps(security_account, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = SecurityAccount.deserialize(decoded, None)
    assert isinstance(decoded, SecurityAccount)
    assert decoded.name == security_account.name
    assert decoded.uuid == security_account.uuid


def test_security() -> None:
    currency = Currency("CZK", 2)
    security = Security("Test Name", "SYMB.OL", SecurityType.ETF, currency, 1)
    serialized = json.dumps(security, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = Security.deserialize(decoded, [currency])
    assert isinstance(decoded, Security)
    assert decoded.name == security.name
    assert decoded.symbol == security.symbol
    assert decoded.currency == security.currency
    assert decoded.type_ == security.type_
    assert decoded.shares_unit == security.shares_unit
    assert decoded.price_places == security.price_places
    assert decoded.uuid == security.uuid


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
        record_keeper._deserialize_accounts([dictionary], None, None)


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
    decoded = CashTransaction.deserialize(
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


@given(transaction=cash_transfers())
def test_cash_transfer(transaction: CashTransfer) -> None:
    serialized = json.dumps(transaction, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = CashTransfer.deserialize(
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


@given(transaction=cash_transactions(type_=CashTransactionType.EXPENSE))
def test_refund_transaction(transaction: CashTransaction) -> None:
    transaction.set_attributes(
        tag_amount_pairs=[
            (Attribute("test tag", AttributeType.TAG), transaction.amount)
        ]
    )
    refund = RefundTransaction(
        "A short description",
        transaction.datetime_ + timedelta(days=1),
        transaction.account,
        transaction,
        transaction.category_amount_pairs,
        transaction.tag_amount_pairs,
        transaction.payee,
    )
    transaction.remove_refund(refund)
    serialized = json.dumps(refund, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = RefundTransaction.deserialize(
        decoded,
        [transaction.account],
        [transaction],
        [transaction.payee],
        transaction.categories,
        transaction.tags,
        transaction.currencies,
    )
    assert isinstance(decoded, RefundTransaction)
    assert decoded.uuid == refund.uuid
    assert decoded.description == refund.description
    assert decoded.datetime_ == refund.datetime_
    assert decoded.datetime_created == refund.datetime_created
    assert decoded.account == refund.account
    assert decoded.refunded_transaction.uuid == transaction.uuid
    assert decoded.payee == refund.payee
    assert decoded.category_amount_pairs == refund.category_amount_pairs
    assert decoded.tag_amount_pairs == refund.tag_amount_pairs


@given(transaction=security_transactions())
def test_security_transaction(transaction: SecurityTransaction) -> None:
    serialized = json.dumps(transaction, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = SecurityTransaction.deserialize(
        decoded,
        [transaction.cash_account, transaction.security_account],
        [transaction.currency],
        [transaction.security],
    )
    assert isinstance(decoded, SecurityTransaction)
    assert decoded.uuid == transaction.uuid
    assert decoded.description == transaction.description
    assert decoded.datetime_ == transaction.datetime_
    assert decoded.datetime_created == transaction.datetime_created
    assert decoded.type_ == transaction.type_
    assert decoded.security == transaction.security
    assert decoded.price_per_share == transaction.price_per_share
    assert decoded.fees == transaction.fees
    assert decoded.cash_account == transaction.cash_account
    assert decoded.security_account == transaction.security_account


@given(transaction=security_transfers())
def test_security_transfer(transaction: SecurityTransfer) -> None:
    serialized = json.dumps(transaction, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = SecurityTransfer.deserialize(
        decoded,
        [transaction.sender, transaction.recipient],
        [transaction.security],
    )
    assert isinstance(decoded, SecurityTransfer)
    assert decoded.uuid == transaction.uuid
    assert decoded.description == transaction.description
    assert decoded.datetime_ == transaction.datetime_
    assert decoded.datetime_created == transaction.datetime_created
    assert decoded.security == transaction.security
    assert decoded.sender == transaction.sender
    assert decoded.recipient == transaction.recipient


def test_record_keeper_transactions() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_currency("EUR", 2)
    record_keeper.add_exchange_rate("EUR", "CZK")
    record_keeper.add_security(
        "ČSOB Dynamický penzijní fond", "CSOB.DYN", SecurityType.MUTUAL_FUND, "CZK", 1
    )
    record_keeper.add_account_group("Bank Accounts", None)
    record_keeper.add_cash_account(
        "Raiffeisen", "CZK", 15000, datetime.now(tzinfo), "Bank Accounts"
    )
    record_keeper.add_cash_account(
        "Moneta", "CZK", 0, datetime.now(tzinfo), "Bank Accounts"
    )
    record_keeper.add_security_account("ČSOB penzijní účet", None)
    record_keeper.add_security_account("ČSOB penzijní účet 2", None)
    record_keeper.add_cash_transaction(
        "chili con carne ingredients",
        datetime.now(tzinfo),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Raiffeisen",
        [("Food/Groceries", 1000)],
        "Albert",
        [("Split", 500)],
    )
    record_keeper.add_cash_transaction(
        "some stupid electronic device",
        datetime.now(tzinfo),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Raiffeisen",
        [("Electronics", 10000)],
        "Alza",
        [],
    )
    record_keeper.add_refund(
        "refunding stupid electronic device",
        datetime.now(tzinfo) + timedelta(days=1),
        str(record_keeper.transactions[1].uuid),
        "Bank Accounts/Raiffeisen",
        [("Electronics", 10000)],
        [],
        "Alza",
    )
    record_keeper.add_cash_transfer(
        "sending money to Moneta",
        datetime.now(tzinfo),
        "Bank Accounts/Raiffeisen",
        "Bank Accounts/Moneta",
        1000,
        1000,
    )
    record_keeper.add_security_transaction(
        "buying ČSOB DPS shares",
        datetime.now(tzinfo),
        SecurityTransactionType.BUY,
        "CSOB.DYN",
        1000,
        "1.7",
        0,
        "ČSOB penzijní účet",
        "Bank Accounts/Raiffeisen",
    )
    record_keeper.add_security_transfer(
        "transfering DPS shares",
        datetime.now(tzinfo),
        "CSOB.DYN",
        10,
        "ČSOB penzijní účet",
        "ČSOB penzijní účet 2",
    )

    serialized = json.dumps(record_keeper, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, RecordKeeper)
    assert decoded.currencies == record_keeper.currencies
    assert len(decoded.exchange_rates) == len(record_keeper.exchange_rates)
    assert decoded.securities == record_keeper.securities
    assert len(decoded.tags) == len(record_keeper.tags)
    assert len(decoded.payees) == len(record_keeper.payees)
    assert len(decoded.account_groups) == len(record_keeper.account_groups)
    assert len(decoded.accounts) == len(record_keeper.accounts)
    assert len(decoded.transactions) == len(record_keeper.transactions)


def test_record_keeper_transactions_invalid_datatype() -> None:
    record_keeper = RecordKeeper()
    transaction_dict = {"datatype": "invalid type!"}
    with pytest.raises(ValueError, match="Unexpected 'datatype' value."):
        record_keeper._deserialize_transactions(
            [transaction_dict], None, None, None, None, None, None
        )
