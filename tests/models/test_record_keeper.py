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
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    CategoryType,
    InvalidCategoryTypeError,
)
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency import CashAmount, Currency, CurrencyError
from src.models.model_objects.security_objects import (
    SecurityAccount,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
    SecurityType,
)
from src.models.record_keeper import AlreadyExistsError, DoesNotExistError, RecordKeeper
from tests.models.test_assets.composites import (
    attributes,
    currencies,
    everything_except,
    valid_decimals,
)

# TODO: maybe move edit tests to different file?


def test_creation() -> None:
    record_keeper = RecordKeeper()
    assert record_keeper.accounts == ()
    assert record_keeper.account_groups == ()
    assert record_keeper.transactions == ()
    assert record_keeper.tags == ()
    assert record_keeper.categories == ()
    assert record_keeper.payees == ()
    assert record_keeper.currencies == ()
    assert record_keeper.exchange_rates == ()
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
    currency_A=currencies(),
    currency_B=currencies(),
    places=st.integers(min_value=0, max_value=8),
)
def test_add_exchange_rate(
    currency_A: Currency, currency_B: Currency, places: int
) -> None:
    assume(currency_A != currency_B)
    record_keeper = RecordKeeper()
    record_keeper.add_currency(currency_A.code, places)
    record_keeper.add_currency(currency_B.code, places)
    record_keeper.add_exchange_rate(currency_A.code, currency_B.code)
    assert (
        str(record_keeper.exchange_rates[0]) == f"{currency_A.code}/{currency_B.code}"
    )


@given(
    currency_A=currencies(),
    currency_B=currencies(),
    places=st.integers(min_value=0, max_value=8),
)
def test_add_exchange_rate_already_exists(
    currency_A: Currency, currency_B: Currency, places: int
) -> None:
    assume(currency_A != currency_B)
    record_keeper = RecordKeeper()
    record_keeper.add_currency(currency_A.code, places)
    record_keeper.add_currency(currency_B.code, places)
    record_keeper.add_exchange_rate(currency_A.code, currency_B.code)
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_exchange_rate(currency_A.code, currency_B.code)


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
    record_keeper = get_preloaded_record_keeper()
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
                valid_decimals(min_value=0.1),
            ),
            min_size=1,
            max_size=5,
            unique=True,
        )
    )
    paths = [path for path, _ in category_name_amount_pairs]
    assume(len(paths) == len(set(paths)))
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
    record_keeper = get_preloaded_record_keeper()
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
        record_keeper.get_account_parent_or_none("does not exist")


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
def test_get_or_make_category_invalid_path_type(path: Any, type_: CategoryType) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="Parameter 'path' must be a string."):
        record_keeper.get_or_make_category(path, type_)


@given(type_=everything_except(CategoryType))
def test_get_or_make_category_invalid_type_type(type_: Any) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="Parameter 'type_' must be a CategoryType."):
        record_keeper.get_or_make_category("test", type_)


def test_get_or_make_category_parent_exists() -> None:
    record_keeper = get_preloaded_record_keeper()
    parent_path = "One/Two"
    child_path = "One/Two/Three"
    parent = record_keeper.get_or_make_category(parent_path, CategoryType.INCOME)
    child = record_keeper.get_or_make_category(child_path, CategoryType.INCOME)
    assert child.path == child_path
    assert parent.path == parent_path


def test_get_or_make_category_does_not_exist() -> None:
    record_keeper = get_preloaded_record_keeper()
    category_path = "One/Two/Three"
    category = record_keeper.get_or_make_category(category_path, CategoryType.INCOME)
    assert category.path == category_path


def test_get_category_does_not_exist() -> None:
    record_keeper = get_preloaded_record_keeper()
    category_path = "One/Two/Three"
    with pytest.raises(DoesNotExistError):
        record_keeper.get_category(category_path)


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
    refunded_transaction: CashTransaction = record_keeper.transactions[0]
    record_keeper.add_refund(
        "Refund!",
        datetime.now(tzinfo),
        str(refunded_transaction.uuid),
        "Bank Accounts/Raiffeisen CZK",
        (("Food and Drink/Groceries", Decimal(1000)),),
        (("Test Tag", Decimal(1000)),),
        refunded_transaction.payee.name,
    )
    refunded_transaction = record_keeper.transactions[0]
    refund = record_keeper.transactions[1]
    assert refund in refunded_transaction.refunds


def test_add_refund_wrong_uuid() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper_with_expense()
    refunded_transaction: CashTransaction = record_keeper.transactions[0]
    with pytest.raises(ValueError, match="Transaction with UUID 'xxx' not found."):
        record_keeper.add_refund(
            description="Refund!",
            datetime_=datetime.now(tzinfo),
            refunded_transaction_uuid="xxx",
            refunded_account_path="Bank Accounts/Raiffeisen CZK",
            category_path_amount_pairs=(("Food and Drink/Groceries", Decimal(1000)),),
            tag_name_amount_pairs=(("Test Tag", Decimal(1000)),),
            payee_name=refunded_transaction.payee.name,
        )


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


def test_set_exchange() -> None:
    record_keeper = get_preloaded_record_keeper()
    yesterday = datetime.now(tzinfo).date() - timedelta(days=1)
    assert record_keeper.exchange_rates[0].latest_rate == Decimal(25)
    record_keeper.set_exchange_rate("EUR/CZK", Decimal(1), yesterday)
    assert record_keeper.exchange_rates[0].rate_history[yesterday] == Decimal(1)


@given(exchange_rate_str=everything_except(str))
def test_set_exchange_rate_invalid_type(exchange_rate_str: Any) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(
        TypeError, match="Parameter 'exchange_rate_str' must be a string."
    ):
        record_keeper.set_exchange_rate(
            exchange_rate_str, Decimal(1), datetime.now(tzinfo).date()
        )


def test_set_exchange_rate_does_not_exist() -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(DoesNotExistError):
        record_keeper.set_exchange_rate("N/A", Decimal(1), datetime.now(tzinfo).date())


def test_edit_cash_transactions_descriptions() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        if transaction.currency.code == "CZK"
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
        if transaction.currency.code == "CZK"
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    edit_datetime = datetime.now(tzinfo)
    record_keeper.edit_cash_transactions(uuids, datetime_=edit_datetime)
    for transaction in cash_transactions:
        assert transaction.datetime_ == edit_datetime


def test_edit_cash_transactions_payees() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        if transaction.currency.code == "CZK"
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
        if transaction.currency.code == "CZK"
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
        if transaction.currency.code == "CZK"
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    edit_tag = "TEST TAG"
    edit_tag_amount_pair = [(edit_tag, Decimal(1))]
    record_keeper.edit_cash_transactions(
        uuids, tag_name_amount_pairs=edit_tag_amount_pair
    )
    for transaction in cash_transactions:
        assert transaction.tag_amount_pairs[0][0].name == edit_tag


def test_edit_cash_transactions_type_wrong_category() -> None:
    """This test attempts to set all CashTransaction types to Expense, although
    there is one income CashTransaction with Income type Category, which fails."""

    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        if transaction.currency.code == "CZK"
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    edit_type = CashTransactionType.EXPENSE
    with pytest.raises(InvalidCategoryTypeError):
        record_keeper.edit_cash_transactions(
            uuids,
            transaction_type=edit_type,
        )


def test_edit_cash_transactions_type() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        if transaction.currency.code == "CZK"
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    edit_type = CashTransactionType.EXPENSE
    edit_category = "TEST EXPENSE CAT"
    edit_category_amount_pair = [(edit_category, None)]
    record_keeper.edit_cash_transactions(
        uuids,
        category_path_amount_pairs=edit_category_amount_pair,
        transaction_type=edit_type,
    )
    for transaction in cash_transactions:
        assert transaction.category_amount_pairs[0][0].name == edit_category


def test_edit_cash_transactions_currency_not_same() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    with pytest.raises(CurrencyError):
        record_keeper.edit_cash_transactions(uuids)


def test_edit_cash_transactions_account_pass() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    cash_transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, CashTransaction)
        if transaction.currency.code == "CZK"
    ]
    uuids = [str(transaction.uuid) for transaction in cash_transactions]
    edit_account = "Test Account CZK"
    record_keeper.add_cash_account(
        name="Test Account CZK",
        currency_code="CZK",
        initial_balance_value=Decimal(0),
        initial_datetime=datetime.now(tzinfo) - timedelta(days=700),
        parent_path=None,
    )
    record_keeper.edit_cash_transactions(uuids, account_path=edit_account)
    for transaction in cash_transactions:
        assert transaction.account.path == edit_account


def test_edit_cash_transactions_invalid_indexes() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    record_keeper.add_cash_transfer(
        "",
        datetime.now(tzinfo),
        "Bank Accounts/Raiffeisen CZK",
        "Bank Accounts/Moneta EUR",
        1,
        1,
    )
    transactions = list(record_keeper.transactions)
    uuids = [str(transaction.uuid) for transaction in transactions]
    with pytest.raises(
        TypeError, match="All edited transactions must be CashTransactions."
    ):
        record_keeper.edit_cash_transactions(uuids)


def test_edit_cash_transfer_invalid_types() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if not isinstance(transaction, CashTransfer)
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    with pytest.raises(
        TypeError, match="All edited transactions must be CashTransfers."
    ):
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
    edit_datetime = datetime.now(tzinfo)
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
        assert transfer.amount_sent.value == edit_amount_sent


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
        assert transfer.amount_received.value == edit_amount_received


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


def test_edit_refunds_wrong_transaction_types() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    transactions = record_keeper.transactions
    uuids = [str(transfer.uuid) for transfer in transactions]
    with pytest.raises(
        TypeError, match="All edited transactions must be RefundTransactions."
    ):
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


def test_edit_refunds_change_category_amounts() -> None:
    record_keeper = get_preloaded_record_keeper_with_refunds()
    edit_category_amount_pairs = [("Food and Drink/Groceries", Decimal(250))]
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, RefundTransaction)
        and transaction.currency.code == "CZK"
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    record_keeper.edit_refunds(
        uuids, category_path_amount_pairs=edit_category_amount_pairs
    )
    for transaction in transactions:
        assert transaction.category_amount_pairs == (
            (
                (
                    transaction.category_amount_pairs[0][0],
                    CashAmount(250, transaction.currency),
                )
            ),
        )


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


def test_edit_security_transactions_wrong_transaction_types() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    transactions = record_keeper.transactions
    uuids = [str(transfer.uuid) for transfer in transactions]
    with pytest.raises(
        TypeError, match="All edited transactions must be SecurityTransactions."
    ):
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
    edit_symbol = "IWDA.AS"
    record_keeper = get_preloaded_record_keeper_with_security_transactions()
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, SecurityTransaction)
        and transaction.security.symbol == "VWCE.DE"
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    record_keeper.edit_security_transactions(uuids, security_symbol=edit_symbol)
    for transaction in transactions:
        assert transaction.security.symbol == edit_symbol


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
        assert transaction.price_per_share.value == edit_price


def test_edit_security_transactions_change_fees() -> None:
    edit_fees = Decimal("0.1")
    record_keeper = get_preloaded_record_keeper_with_security_transactions()
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, SecurityTransaction)
        and transaction.security.symbol == "VWCE.DE"
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    record_keeper.edit_security_transactions(uuids, fees=edit_fees)
    for transaction in transactions:
        assert transaction.fees.value == edit_fees


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


def test_edit_security_transfers_wrong_transaction_types() -> None:
    record_keeper = get_preloaded_record_keeper_with_cash_transactions()
    transactions = record_keeper.transactions
    uuids = [str(transfer.uuid) for transfer in transactions]
    with pytest.raises(
        TypeError, match="All edited transactions must be SecurityTransfers."
    ):
        record_keeper.edit_security_transfers(uuids)


def test_edit_security_transfers_change_symbol() -> None:
    edit_symbol = "IWDA.AS"
    record_keeper = get_preloaded_record_keeper_with_security_transactions()
    transactions = [
        transaction
        for transaction in record_keeper.transactions
        if isinstance(transaction, SecurityTransfer)
        and transaction.security.symbol == "VWCE.DE"
    ]
    uuids = [str(transfer.uuid) for transfer in transactions]
    record_keeper.edit_security_transfers(uuids, security_symbol=edit_symbol)
    for transaction in transactions:
        assert transaction.security.symbol == edit_symbol


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


def get_preloaded_record_keeper_with_security_transactions() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper()
    record_keeper.add_security_transaction(
        description="Monthly buy of VWCE",
        datetime_=datetime.now(tzinfo) - timedelta(days=1),
        type_=SecurityTransactionType.BUY,
        security_symbol="VWCE.DE",
        shares=Decimal(10),
        price_per_share=Decimal(90),
        fees=Decimal(1.25),
        security_account_path="Security Accounts/Interactive Brokers",
        cash_account_path="Bank Accounts/Moneta EUR",
    )
    record_keeper.add_security_transaction(
        description="Monthly buy of VWCE",
        datetime_=datetime.now(tzinfo) - timedelta(days=31),
        type_=SecurityTransactionType.BUY,
        security_symbol="VWCE.DE",
        shares=Decimal(10),
        price_per_share=Decimal(91),
        fees=Decimal(1.25),
        security_account_path="Security Accounts/Interactive Brokers",
        cash_account_path="Bank Accounts/Moneta EUR",
    )
    record_keeper.add_security_transaction(
        description="Monthly buy of ČSOB DPS",
        datetime_=datetime.now(tzinfo) - timedelta(days=1),
        type_=SecurityTransactionType.BUY,
        security_symbol="CSOB.DYN",
        shares=Decimal(2750),
        price_per_share=Decimal(1.75),
        fees=Decimal(0),
        security_account_path="Security Accounts/ČSOB Penzijní účet",
        cash_account_path="Bank Accounts/Fio CZK",
    )
    record_keeper.add_security_transaction(
        description="Monthly buy of ČSOB DPS",
        datetime_=datetime.now(tzinfo) - timedelta(days=31),
        type_=SecurityTransactionType.BUY,
        security_symbol="CSOB.DYN",
        shares=Decimal(2850),
        price_per_share=Decimal(1.6),
        fees=Decimal(0),
        security_account_path="Security Accounts/ČSOB Penzijní účet",
        cash_account_path="Bank Accounts/Fio CZK",
    )
    record_keeper.add_security_transfer(
        description="Security transfer to Degiro",
        datetime_=datetime.now(tzinfo),
        security_symbol="VWCE.DE",
        shares=Decimal(10),
        account_sender_path="Security Accounts/Interactive Brokers",
        account_recipient_path="Security Accounts/Degiro",
    )
    record_keeper.add_security_transfer(
        description="Security transfer to Degiro",
        datetime_=datetime.now(tzinfo) - timedelta(days=30),
        security_symbol="VWCE.DE",
        shares=Decimal(10),
        account_sender_path="Security Accounts/Interactive Brokers",
        account_recipient_path="Security Accounts/Degiro",
    )
    return record_keeper


def get_preloaded_record_keeper_with_refunds() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper()
    record_keeper.add_cash_transaction(
        "Shopping for cooking",
        datetime.now(tzinfo) - timedelta(days=2),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Raiffeisen CZK",
        (("Food and Drink/Groceries", Decimal(1000)),),
        "Albert",
        (("Test Tag", Decimal(1000)),),
    )
    record_keeper.add_cash_transaction(
        "Electronic device",
        datetime.now(tzinfo) - timedelta(days=2),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Moneta EUR",
        (("Electronics", Decimal(400)),),
        "Alza",
        (("Test Tag", Decimal(400)),),
    )
    transaction_cooking = record_keeper.transactions[0]
    transaction_electronics = record_keeper.transactions[1]

    record_keeper.add_refund(
        description="An expense transaction",
        datetime_=datetime.now(tzinfo),
        refunded_transaction_uuid=str(transaction_cooking.uuid),
        refunded_account_path="Bank Accounts/Raiffeisen CZK",
        category_path_amount_pairs=(("Food and Drink/Groceries", Decimal(250)),),
        payee_name="Albert",
        tag_name_amount_pairs=(("Test Tag", Decimal(250)),),
    )
    record_keeper.add_refund(
        description="An expense transaction",
        datetime_=datetime.now(tzinfo),
        refunded_transaction_uuid=str(transaction_cooking.uuid),
        refunded_account_path="Bank Accounts/Raiffeisen CZK",
        category_path_amount_pairs=(("Food and Drink/Groceries", Decimal(750)),),
        payee_name="Albert",
        tag_name_amount_pairs=(("Test Tag", Decimal(750)),),
    )
    record_keeper.add_refund(
        description="An expense transaction",
        datetime_=datetime.now(tzinfo),
        refunded_transaction_uuid=str(transaction_electronics.uuid),
        refunded_account_path="Bank Accounts/Moneta EUR",
        category_path_amount_pairs=(("Electronics", Decimal(400)),),
        payee_name="Alza",
        tag_name_amount_pairs=(("Test Tag", Decimal(400)),),
    )
    return record_keeper


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


def get_preloaded_record_keeper_with_cash_transactions() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper()
    record_keeper.add_cash_transaction(
        "Ingredients for cooking",
        datetime.now(tzinfo),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Raiffeisen CZK",
        (("Food and Drink/Groceries", Decimal(1000)),),
        "Albert",
        (("Split with GF", Decimal(500)),),
    )
    record_keeper.add_cash_transaction(
        "Pizza with GF",
        datetime.now(tzinfo) - timedelta(days=1),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Raiffeisen CZK",
        (("Food and Drink/Eating out", Decimal(500)),),
        "Doe Boy",
        (("Split with GF", Decimal(250)),),
    )
    record_keeper.add_cash_transaction(
        "Salary",
        datetime.now(tzinfo) - timedelta(days=7),
        CashTransactionType.INCOME,
        "Bank Accounts/Raiffeisen CZK",
        (("Salary", Decimal(50000)),),
        "Employer",
        (),
    )
    record_keeper.add_cash_transaction(
        "Eating out on vacation",
        datetime.now(tzinfo) - timedelta(days=180),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Moneta EUR",
        (("Food and Drink/Eating out", Decimal(30)),),
        "unknown payee",
        (("Split with GF", Decimal(15)),),
    )
    return record_keeper


def get_preloaded_record_keeper_with_cash_transfers() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper()
    record_keeper.add_cash_transfer(
        "Salary from Fio to RB",
        datetime.now(tzinfo) - timedelta(days=7),
        "Bank Accounts/Fio CZK",
        "Bank Accounts/Raiffeisen CZK",
        50000,
        50000,
    )
    record_keeper.add_cash_transfer(
        "Savings from Fio to Creditas",
        datetime.now(tzinfo) - timedelta(days=37),
        "Bank Accounts/Fio CZK",
        "Bank Accounts/Creditas CZK",
        100000,
        100000,
    )
    record_keeper.add_cash_transfer(
        "Conversion from RB to Moneta",
        datetime.now(tzinfo) - timedelta(days=6),
        "Bank Accounts/Raiffeisen CZK",
        "Bank Accounts/Moneta EUR",
        25000,
        1000,
    )
    record_keeper.add_cash_transfer(
        "Transfer from Moneta to Revolut",
        datetime.now(tzinfo) - timedelta(days=5),
        "Bank Accounts/Moneta EUR",
        "Bank Accounts/Revolut EUR",
        1000,
        1000,
    )
    record_keeper.add_cash_transfer(
        "Conversion from Revolut to Fio",
        datetime.now(tzinfo) - timedelta(days=4),
        "Bank Accounts/Moneta EUR",
        "Bank Accounts/Fio CZK",
        1000,
        25000,
    )
    return record_keeper


def get_preloaded_record_keeper_with_various_transactions() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper()
    record_keeper.add_cash_transfer(
        "Salary from Fio to RB",
        datetime.now(tzinfo) - timedelta(days=7),
        "Bank Accounts/Fio CZK",
        "Bank Accounts/Raiffeisen CZK",
        50000,
        50000,
    )
    record_keeper.add_cash_transaction(
        "Ingredients for cooking",
        datetime.now(tzinfo),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Raiffeisen CZK",
        (("Food and Drink/Groceries", Decimal(1000)),),
        "Albert",
        (("Split with GF", Decimal(500)),),
    )
    record_keeper.add_cash_transaction(
        "Electronic device",
        datetime.now(tzinfo) - timedelta(days=2),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Moneta EUR",
        (("Electronics", Decimal(400)),),
        "Alza",
        (("Test Tag", Decimal(400)),),
    )
    transaction_electronics = next(
        transaction
        for transaction in record_keeper.transactions
        if transaction.description == "Electronic device"
    )
    record_keeper.add_refund(
        description="An expense transaction",
        datetime_=datetime.now(tzinfo),
        refunded_transaction_uuid=str(transaction_electronics.uuid),
        refunded_account_path="Bank Accounts/Moneta EUR",
        category_path_amount_pairs=(("Electronics", Decimal(400)),),
        payee_name="Alza",
        tag_name_amount_pairs=(("Test Tag", Decimal(400)),),
    )
    record_keeper.add_security_transaction(
        description="Monthly buy of ČSOB DPS",
        datetime_=datetime.now(tzinfo) - timedelta(days=31),
        type_=SecurityTransactionType.BUY,
        security_symbol="CSOB.DYN",
        shares=Decimal(2850),
        price_per_share=Decimal(1.6),
        fees=Decimal(0),
        security_account_path="Security Accounts/ČSOB Penzijní účet",
        cash_account_path="Bank Accounts/Fio CZK",
    )
    record_keeper.add_security_transfer(
        description="Security transfer to Degiro",
        datetime_=datetime.now(tzinfo),
        security_symbol="VWCE.DE",
        shares=Decimal(10),
        account_sender_path="Security Accounts/Interactive Brokers",
        account_recipient_path="Security Accounts/Degiro",
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
        initial_datetime=datetime.now(tzinfo) - timedelta(days=365),
        parent_path="Bank Accounts",
    )
    record_keeper.add_cash_account(
        name="Fio CZK",
        currency_code="CZK",
        initial_balance_value=Decimal(0),
        initial_datetime=datetime.now(tzinfo) - timedelta(days=365),
        parent_path="Bank Accounts",
    )
    record_keeper.add_cash_account(
        name="Creditas CZK",
        currency_code="CZK",
        initial_balance_value=Decimal(100_000),
        initial_datetime=datetime.now(tzinfo) - timedelta(days=365),
        parent_path="Bank Accounts",
    )
    record_keeper.add_cash_account(
        name="Moneta EUR",
        currency_code="EUR",
        initial_balance_value=Decimal(1600),
        initial_datetime=datetime.now(tzinfo) - timedelta(days=365),
        parent_path="Bank Accounts",
    )
    record_keeper.add_cash_account(
        name="Revolut EUR",
        currency_code="EUR",
        initial_balance_value=Decimal(0),
        initial_datetime=datetime.now(tzinfo) - timedelta(days=365),
        parent_path="Bank Accounts",
    )
    record_keeper.add_security_account(name="Degiro", parent_path="Security Accounts")
    record_keeper.add_security_account(
        name="Interactive Brokers", parent_path="Security Accounts"
    )
    record_keeper.add_security_account(
        name="ČSOB Penzijní účet", parent_path="Security Accounts"
    )
    record_keeper.add_security(
        "Vanguard FTSE All-World", "VWCE.DE", SecurityType.ETF, "EUR", 1
    )
    record_keeper.add_security(
        "iShares MSCI World", "IWDA.AS", SecurityType.ETF, "EUR", 1
    )
    record_keeper.add_security(
        "ČSOB Dynamický penzijní fond", "CSOB.DYN", SecurityType.MUTUAL_FUND, "CZK", 1
    )
    record_keeper.add_category("Food and Drink", None, CategoryType.EXPENSE)
    record_keeper.add_category("Electronics", None, CategoryType.EXPENSE)
    record_keeper.add_category("Groceries", "Food and Drink")
    record_keeper.add_category("Eating out", "Food and Drink")
    record_keeper.add_category("Salary", None, CategoryType.INCOME)
    record_keeper.add_category("Splitting costs", None, CategoryType.INCOME_AND_EXPENSE)
    return record_keeper
