import string
from datetime import datetime, timedelta
from decimal import Decimal
from types import NoneType
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.base_classes.account import Account
from src.models.constants import tzinfo
from src.models.model_objects.attributes import AttributeType, CategoryType
from src.models.model_objects.cash_objects import CashAccount, CashTransactionType
from src.models.model_objects.currency import CashAmount
from src.models.model_objects.security_objects import (
    SecurityAccount,
    SecurityTransactionType,
    SecurityType,
)
from src.models.record_keeper import AlreadyExistsError, DoesNotExistError, RecordKeeper
from tests.models.test_assets.composites import everything_except, valid_decimals


def test_creation() -> None:
    record_keeper = RecordKeeper()
    assert record_keeper.accounts == ()
    assert record_keeper.account_groups == ()
    assert record_keeper.transactions == ()
    assert record_keeper.tags == ()
    assert record_keeper.categories == ()
    assert record_keeper.payees == ()
    assert record_keeper.currencies == ()
    assert record_keeper.securities == ()
    assert record_keeper.__repr__() == "RecordKeeper"


@given(
    code=st.text(string.ascii_letters, min_size=3, max_size=3),
    places=st.integers(min_value=0, max_value=8),
)
def test_add_currency(code: str, places: int) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency(code, places)
    currency = record_keeper.currencies[0]
    assert currency.code == code.upper()


@given(
    name=st.text(min_size=1, max_size=32),
)
def test_add_account_group_no_parent(name: str) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group(name, None)
    account_group = record_keeper.account_groups[0]
    assert account_group.name == name
    assert account_group.parent is None


@given(
    name=st.text(min_size=1, max_size=32),
    parent_name=st.text(min_size=1, max_size=32),
)
def test_add_account_group_with_parent(name: str, parent_name: str) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group(parent_name, None)
    record_keeper.add_account_group(name, parent_name)
    account_group = record_keeper.account_groups[1]
    parent_group = record_keeper.account_groups[0]
    assert account_group.name == name
    assert account_group.parent == parent_group


@given(
    name=st.text(min_size=1, max_size=32),
    grandparent_name=st.text(min_size=1, max_size=32),
    parent_name=st.text(min_size=1, max_size=32),
)
def test_add_account_group_with_multiple_parents(
    name: str, grandparent_name: str, parent_name: str
) -> None:
    grandparent_path = grandparent_name
    parent_path = grandparent_name + "/" + parent_name
    record_keeper = RecordKeeper()
    record_keeper.add_account_group(grandparent_name, None)
    record_keeper.add_account_group(parent_name, grandparent_path)
    record_keeper.add_account_group(name, parent_path)
    account_group = record_keeper.account_groups[2]
    parent = record_keeper.account_groups[1]
    assert account_group.name == name
    assert account_group.path == f"{parent_path}/{name}"
    assert account_group.parent == parent


@given(
    name=st.text(min_size=1, max_size=32),
    currency_code=st.text(string.ascii_letters, min_size=3, max_size=3),
    places=st.integers(min_value=0, max_value=8),
    initial_balance=valid_decimals(min_value=0),
    initial_datetime=st.datetimes(),
    parent_name=st.none() | st.text(min_size=1, max_size=32),
)
def test_add_cash_account(
    name: str,
    currency_code: str,
    places: int,
    initial_balance: Decimal,
    initial_datetime: datetime,
    parent_name: str | None,
) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency(currency_code, places)
    if parent_name:
        record_keeper.add_account_group(parent_name, None)
    record_keeper.add_cash_account(
        name, currency_code, initial_balance, initial_datetime, parent_name
    )
    parent_group = record_keeper.account_groups[0] if parent_name else None
    cash_account: CashAccount = record_keeper.accounts[0]
    assert cash_account.name == name
    assert cash_account.currency.code == currency_code.upper()
    assert cash_account.initial_balance == CashAmount(
        initial_balance, cash_account.currency
    )
    assert cash_account.initial_datetime == initial_datetime
    assert cash_account.parent == parent_group


@given(
    description=st.text(min_size=0, max_size=256),
    datetime_=st.datetimes(
        min_value=datetime.now() + timedelta(days=1), timezones=st.just(tzinfo)
    ),
    transaction_type=st.sampled_from(CashTransactionType),
    payee_name=st.text(min_size=1, max_size=32),
    data=st.data(),
)
def test_add_cash_transaction(
    description: str,
    datetime_: datetime,
    transaction_type: str,
    payee_name: str,
    data: st.DataObject,
) -> None:
    record_keeper = get_preloaded_record_keeper()  # noqa: NEW100
    account_path = data.draw(
        st.sampled_from(
            [
                account.path
                for account in record_keeper.accounts
                if isinstance(account, CashAccount)
            ]
        )
    )
    valid_cat_types = (
        [CategoryType.INCOME, CategoryType.INCOME_AND_EXPENSE]
        if transaction_type == CashTransactionType.INCOME
        else [CategoryType.EXPENSE, CategoryType.INCOME_AND_EXPENSE]
    )
    valid_categories = [
        cat for cat in record_keeper.categories if cat.type_ in valid_cat_types
    ]
    category_name_amount_pairs = data.draw(
        st.lists(
            st.tuples(
                st.sampled_from([cat.path for cat in valid_categories]),
                valid_decimals(min_value=0.01),
            ),
            min_size=1,
            max_size=5,
        )
    )
    max_tag_amount = sum(amount for _, amount in category_name_amount_pairs)
    tag_name_amount_pairs = data.draw(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=32),
                valid_decimals(min_value=0.01, max_value=max_tag_amount),
            ),
            min_size=0,
            max_size=5,
        )
    )
    record_keeper.add_cash_transaction(
        description,
        datetime_,
        transaction_type,
        account_path,
        category_name_amount_pairs,
        payee_name,
        tag_name_amount_pairs,
    )
    transaction = record_keeper.transactions[0]
    assert transaction.datetime_ == datetime_
    assert transaction.description == description


@given(
    description=st.text(min_size=0, max_size=256),
    datetime_=st.datetimes(
        min_value=datetime.now() + timedelta(days=1), timezones=st.just(tzinfo)
    ),
    amount_sent=valid_decimals(min_value=0.01),
    amount_received=valid_decimals(min_value=0.01),
    data=st.data(),
)
def test_add_cash_transfer(
    description: str,
    datetime_: datetime,
    amount_sent: Decimal,
    amount_received: Decimal,
    data: st.DataObject,
) -> None:
    record_keeper = get_preloaded_record_keeper()  # noqa: NEW100
    account_sender_path = data.draw(
        st.sampled_from(
            [
                account.path
                for account in record_keeper.accounts
                if isinstance(account, CashAccount)
            ]
        )
    )
    account_recipient_path = data.draw(
        st.sampled_from(
            [
                account.path
                for account in record_keeper.accounts
                if account.path != account_sender_path
                and isinstance(account, CashAccount)
            ]
        )
    )
    record_keeper.add_cash_transfer(
        description,
        datetime_,
        account_sender_path,
        account_recipient_path,
        amount_sent,
        amount_received,
    )
    transfer = record_keeper.transactions[0]
    assert transfer.datetime_ == datetime_
    assert transfer.description == description


@given(
    code=st.text(string.ascii_letters, min_size=3, max_size=3),
    places=st.integers(min_value=0, max_value=8),
)
def test_add_currency_already_exists(code: str, places: int) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency(code, places)
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_currency(code, places)


@given(
    name=st.text(min_size=1, max_size=32),
    parent=st.text(min_size=1, max_size=32),
)
def test_add_category_parent_does_not_exist(name: str, parent: str) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(DoesNotExistError):
        record_keeper.add_category(name, parent)


@given(
    name=st.text(min_size=1, max_size=32),
)
def test_add_category_invalid_type(name: str) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="If parameter 'parent_path' is None"):
        record_keeper.add_category(name, None, None)


@given(name=st.text(min_size=1, max_size=32), type_=st.sampled_from(CategoryType))
def test_add_category_already_exists(name: str, type_: CategoryType) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_category(name, None, type_)
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_category(name, None, type_)


@given(
    name=st.text(min_size=1, max_size=32),
)
def test_add_account_group_already_exists(name: str) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group(name, None)
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_account_group(name, None)


@given(data=st.data())
def test_add_cash_account_already_exists(data: st.DataObject) -> None:
    record_keeper = get_preloaded_record_keeper()
    account = data.draw(st.sampled_from(record_keeper.accounts))
    parent_path = account.parent.path if account.parent is not None else None
    currency = data.draw(st.sampled_from(record_keeper.currencies))
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_cash_account(
            account.name, currency.code, Decimal(0), datetime.now(), parent_path
        )


def test_get_account_parent_does_not_exist() -> None:
    record_keeper = get_preloaded_record_keeper()
    with pytest.raises(DoesNotExistError):
        record_keeper.get_account_parent("does not exist")


@given(path=everything_except(str))
def test_get_account_invalid_path_type(path: Any) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="Parameter 'path' must be a string."):
        record_keeper.get_account(path, Account)


@given(type_=everything_except((Account, CashAccount, SecurityAccount)))
def test_get_account_invalid_type_type(type_: Any) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="Parameter type_ must be type"):
        record_keeper.get_account("", type_)


def test_get_account_invalid_account_type() -> None:
    record_keeper = get_preloaded_record_keeper()
    with pytest.raises(TypeError, match="Type of Account at path='"):
        record_keeper.get_account("Bank Accounts/Moneta EUR", SecurityAccount)


def test_get_account_does_not_exist() -> None:
    record_keeper = get_preloaded_record_keeper()
    with pytest.raises(DoesNotExistError):
        record_keeper.get_account("does not exist", Account)


@given(code=everything_except(str))
def test_get_currency_invalid_code_type(code: Any) -> None:
    record_keeper = get_preloaded_record_keeper()
    with pytest.raises(TypeError, match="Parameter 'code' must be a string."):
        record_keeper.get_currency(code)


def test_get_currency_does_not_exist() -> None:
    record_keeper = get_preloaded_record_keeper()
    with pytest.raises(DoesNotExistError):
        record_keeper.get_currency("does not exist")


@given(path=everything_except(str), type_=st.sampled_from(CategoryType))
def test_get_category_invalid_path_type(path: Any, type_: CategoryType) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="Parameter 'path' must be a string."):
        record_keeper.get_category(path, type_)


@given(type_=everything_except(CategoryType))
def test_get_category_invalid_type_type(type_: Any) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="Parameter 'type_' must be a CategoryType."):
        record_keeper.get_category("test", type_)


def test_get_category_does_not_exist() -> None:
    record_keeper = get_preloaded_record_keeper()
    category_path = "One/Two/Three"
    category = record_keeper.get_category(category_path, CategoryType.INCOME)
    assert category.path == category_path


def test_get_category_parent_exists() -> None:
    record_keeper = get_preloaded_record_keeper()
    parent_path = "One/Two"
    child_path = "One/Two/Three"
    parent = record_keeper.get_category(parent_path, CategoryType.INCOME)
    child = record_keeper.get_category(child_path, CategoryType.INCOME)
    assert child.path == child_path
    assert parent.path == parent_path


def test_get_attribute() -> None:
    record_keeper = get_preloaded_record_keeper()
    tag = record_keeper.get_attribute("New Tag", AttributeType.TAG)
    payee = record_keeper.get_attribute("New Payee", AttributeType.PAYEE)
    no_of_tags = len(record_keeper.tags)
    no_of_payees = len(record_keeper.payees)
    tag2 = record_keeper.get_attribute("New Tag", AttributeType.TAG)
    payee2 = record_keeper.get_attribute("New Payee", AttributeType.PAYEE)
    assert tag2 in record_keeper.tags
    assert payee2 in record_keeper.payees
    assert tag == tag2
    assert payee == payee2
    assert len(record_keeper.tags) == no_of_tags
    assert len(record_keeper.payees) == no_of_payees


@given(name=everything_except(str), type_=st.sampled_from(AttributeType))
def test_get_attribute_invalid_path_type(name: Any, type_: AttributeType) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="Parameter 'name' must be a string."):
        record_keeper.get_attribute(name, type_)


@given(type_=everything_except(AttributeType))
def test_get_attribute_invalid_type_type(type_: Any) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="Parameter 'type_' must be an AttributeType."):
        record_keeper.get_attribute("test", type_)


def test_add_refund() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper_with_expense()
    record_keeper.add_refund(
        "Refund!",
        datetime.now(tzinfo),
        0,
        "Bank Accounts/Raiffeisen CZK",
        (("Food and Drink/Groceries", Decimal(1000)),),
        (("Test Tag", Decimal(1000)),),
    )
    refunded_transaction = record_keeper.transactions[0]
    refund = record_keeper.transactions[1]
    assert refund in refunded_transaction.refunds


def test_add_security() -> None:
    record_keeper = RecordKeeper()
    name = "Security Name"
    symbol = "ABCD.EF"
    type_ = SecurityType.ETF
    currency_code = "EUR"
    places = 2
    unit = 1
    record_keeper.add_currency(currency_code, places)
    record_keeper.add_security(name, symbol, type_, currency_code, unit)
    security = record_keeper.get_security(symbol)
    assert security.name == name
    assert security.symbol == symbol
    assert security.type_ == type_
    assert security.currency.code == currency_code.upper()
    assert security in record_keeper.securities


def test_add_security_already_exists() -> None:
    record_keeper = RecordKeeper()
    name_1 = "Security Name"
    name_2 = "Another Name"
    symbol = "ABCD.EF"
    type_ = SecurityType.ETF
    type_2 = SecurityType.MUTUAL_FUND
    currency_code = "EUR"
    places = 2
    unit = 1
    record_keeper.add_currency(currency_code, places)
    record_keeper.add_security(name_1, symbol, type_, currency_code, unit)
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_security(name_2, symbol, type_2, currency_code, unit)


@given(symbol=everything_except(str))
def test_get_security_invalid_symbol_type(symbol: Any) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="Parameter 'symbol' must be a string."):
        record_keeper.get_security(symbol)


@given(symbol=st.text(min_size=1, max_size=8))
def test_get_security_does_not_exists(symbol: str) -> None:
    assume(symbol != "VWCE.DE")
    record_keeper = RecordKeeper()
    with pytest.raises(DoesNotExistError):
        record_keeper.get_security(symbol)


@given(
    description=st.text(min_size=1, max_size=256),
    type_=st.sampled_from(SecurityTransactionType),
    price_per_share=valid_decimals(min_value=0.0),
    fees=valid_decimals(min_value=0),
    data=st.data(),
)
def test_add_security_transaction(
    description: str,
    type_: SecurityTransactionType,
    price_per_share: Decimal,
    fees: Decimal,
    data: st.DataObject,
) -> None:
    record_keeper = get_preloaded_record_keeper()
    security = data.draw(st.sampled_from(record_keeper.securities))
    shares = data.draw(st.integers(min_value=1, max_value=1e10))
    security_account_path = data.draw(
        st.sampled_from(
            [
                account.path
                for account in record_keeper.accounts
                if isinstance(account, SecurityAccount)
            ]
        )
    )
    cash_account = data.draw(
        st.sampled_from(
            [
                account
                for account in record_keeper.accounts
                if isinstance(account, CashAccount)
                and security.currency == account.currency
            ]
        )
    )
    cash_account_path = cash_account.path
    datetime_ = cash_account.initial_datetime + timedelta(days=1)
    record_keeper.add_security_transaction(
        description,
        datetime_,
        type_,
        security.symbol,
        shares,
        price_per_share,
        fees,
        security_account_path,
        cash_account_path,
    )
    assert len(record_keeper.transactions) == 1


@given(
    description=st.text(min_size=1, max_size=256),
    datetime_=st.datetimes(timezones=st.just(tzinfo)),
    data=st.data(),
)
def test_add_security_transfer(
    description: str,
    datetime_: datetime,
    data: st.DataObject,
) -> None:
    record_keeper = get_preloaded_record_keeper()
    security = data.draw(st.sampled_from(record_keeper.securities))
    shares = data.draw(st.integers(min_value=1, max_value=1e10))
    account_sender_path = data.draw(
        st.sampled_from(
            [
                account.path
                for account in record_keeper.accounts
                if isinstance(account, SecurityAccount)
            ]
        )
    )
    account_recipient_path = data.draw(
        st.sampled_from(
            [
                account.path
                for account in record_keeper.accounts
                if isinstance(account, SecurityAccount)
                and account.path != account_sender_path
            ]
        )
    )
    record_keeper.add_security_transfer(
        description,
        datetime_,
        security.symbol,
        shares,
        account_sender_path,
        account_recipient_path,
    )
    assert len(record_keeper.transactions) == 1


@given(name=everything_except(str))
def test_check_account_exists_invalid_name_type(name: Any) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="Parameter 'name' must be a string."):
        record_keeper._check_account_exists(name, None)


@given(parent_path=everything_except((str, NoneType)))
def test_check_account_exists_invalid_parent_path_type(parent_path: Any) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="Parameter 'parent_path' must be a string or"):
        record_keeper._check_account_exists("test", parent_path)


def get_preloaded_record_keeper_with_expense() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper()
    record_keeper.add_cash_transaction(
        "An expense transaction",
        datetime.now(tzinfo),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Raiffeisen CZK",
        (("Food and Drink/Groceries", Decimal(1000)),),
        "Albert",
        (("Test Tag", Decimal(1000)),),
    )
    return record_keeper


def get_preloaded_record_keeper() -> RecordKeeper:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_currency("EUR", 2)
    record_keeper.add_exchange_rate("EUR", "CZK")
    record_keeper.set_exchange_rate("EUR/CZK", Decimal(25), datetime.now(tzinfo).date())
    record_keeper.add_account_group("Bank Accounts", None)
    record_keeper.add_account_group("Security Accounts", None)
    record_keeper.add_cash_account(
        name="Raiffeisen CZK",
        currency_code="CZK",
        initial_balance_value=Decimal(1500),
        initial_datetime=datetime.now(tzinfo),
        parent_path="Bank Accounts",
    )
    record_keeper.add_cash_account(
        name="Moneta EUR",
        currency_code="EUR",
        initial_balance_value=Decimal(1600),
        initial_datetime=datetime.now(tzinfo),
        parent_path="Bank Accounts",
    )
    record_keeper.add_security_account(name="Degiro", parent_path="Security Accounts")
    record_keeper.add_security_account(
        name="Interactive Brokers", parent_path="Security Accounts"
    )
    record_keeper.add_security(
        "Vanguard FTSE All-World", "VWCE.DE", SecurityType.ETF, "EUR", 1
    )
    record_keeper.add_category("Food and Drink", None, CategoryType.EXPENSE)
    record_keeper.add_category("Groceries", "Food and Drink")
    record_keeper.add_category("Eating out", "Food and Drink")
    record_keeper.add_category("Salary", None, CategoryType.INCOME)
    record_keeper.add_category("Splitting costs", None, CategoryType.INCOME_AND_EXPENSE)
    return record_keeper
