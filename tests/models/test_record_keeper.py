import string
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.base_classes.account import Account
from src.models.model_objects.attributes import AttributeType, Category, CategoryType
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
)
from src.models.model_objects.currency_objects import CashAmount, Currency
from src.models.model_objects.security_objects import (
    SecurityAccount,
    SecurityTransactionType,
)
from src.models.record_keeper import AlreadyExistsError, NotFoundError, RecordKeeper
from src.models.user_settings import user_settings
from tests.models.test_assets.composites import (
    currencies,
    everything_except,
    names,
    valid_decimals,
)


def test_creation() -> None:
    record_keeper = RecordKeeper()
    assert record_keeper.accounts == ()
    assert record_keeper.cash_accounts == ()
    assert record_keeper.security_accounts == ()
    assert record_keeper.account_groups == ()
    assert record_keeper.root_account_items == ()
    assert record_keeper.transactions == ()
    assert record_keeper.cash_transactions == ()
    assert record_keeper.refund_transactions == ()
    assert record_keeper.cash_transfers == ()
    assert record_keeper.security_transactions == ()
    assert record_keeper.security_transfers == ()
    assert record_keeper.tags == ()
    assert record_keeper.categories == ()
    assert record_keeper.income_categories == ()
    assert record_keeper.expense_categories == ()
    assert record_keeper.dual_purpose_categories == ()
    assert record_keeper.root_income_categories == ()
    assert record_keeper.root_expense_categories == ()
    assert record_keeper.root_dual_purpose_categories == ()
    assert record_keeper.payees == ()
    assert record_keeper.currencies == ()
    assert record_keeper.base_currency is None
    assert record_keeper.exchange_rates == ()
    assert record_keeper.securities == ()
    assert record_keeper.descriptions == ()
    assert record_keeper.__repr__() == "RecordKeeper"


@given(
    code=st.text(string.ascii_letters, min_size=3, max_size=3),
    decimals=st.integers(min_value=0, max_value=8),
)
def test_add_currency(code: str, decimals: int) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency(code, decimals)
    currency = record_keeper.currencies[0]
    assert currency.code == code.upper()
    assert record_keeper.base_currency == currency


def test_set_base_currency() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_currency("EUR", 2)
    record_keeper.add_currency("DKK", 2)
    record_keeper.set_base_currency("EUR")
    base_currency: Currency = record_keeper.base_currency
    assert base_currency.code == "EUR"


@given(
    currency_a=currencies(),
    currency_b=currencies(),
    decimals=st.integers(min_value=0, max_value=8),
)
def test_add_exchange_rate(
    currency_a: Currency, currency_b: Currency, decimals: int
) -> None:
    assume(currency_a != currency_b)
    record_keeper = RecordKeeper()
    record_keeper.add_currency(currency_a.code, decimals)
    record_keeper.add_currency(currency_b.code, decimals)
    record_keeper.add_exchange_rate(currency_a.code, currency_b.code)
    assert (
        str(record_keeper.exchange_rates[0]) == f"{currency_a.code}/{currency_b.code}"
    )


@given(
    currency_a=currencies(),
    currency_b=currencies(),
    decimals=st.integers(min_value=0, max_value=8),
)
def test_add_exchange_rate_already_exists(
    currency_a: Currency, currency_b: Currency, decimals: int
) -> None:
    assume(currency_a != currency_b)
    record_keeper = RecordKeeper()
    record_keeper.add_currency(currency_a.code, decimals)
    record_keeper.add_currency(currency_b.code, decimals)
    record_keeper.add_exchange_rate(currency_a.code, currency_b.code)
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_exchange_rate(currency_a.code, currency_b.code)


@given(
    currency_a=currencies(),
    currency_b=currencies(),
    decimals=st.integers(min_value=0, max_value=8),
)
def test_get_exchange_rate(
    currency_a: Currency, currency_b: Currency, decimals: int
) -> None:
    assume(currency_a != currency_b)
    record_keeper = RecordKeeper()
    record_keeper.add_currency(currency_a.code, decimals)
    record_keeper.add_currency(currency_b.code, decimals)
    record_keeper.add_exchange_rate(currency_a.code, currency_b.code)
    exchange_rate = record_keeper.get_exchange_rate(
        f"{currency_a.code}/{currency_b.code}"
    )
    assert exchange_rate is not None
    assert exchange_rate.primary_currency == currency_a
    assert exchange_rate.secondary_currency == currency_b


@given(code=everything_except(str))
def test_get_exchange_rate_invalid_type(code: Any) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="string"):
        record_keeper.get_exchange_rate(code)


@given(code=st.text(min_size=7, max_size=7))
def test_get_exchange_rate_not_found(code: str) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(NotFoundError):
        record_keeper.get_exchange_rate(code)


@given(
    name=names(),
)
def test_add_account_group_no_parent(name: str) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group(name)
    account_group = record_keeper.account_groups[0]
    assert account_group.name == name
    assert account_group.parent is None


@given(name1=names(), name2=names())
def test_add_account_group_with_index_no_parent(name1: str, name2: str) -> None:
    assume(name1 != name2)
    record_keeper = RecordKeeper()
    record_keeper.add_account_group(name1, 0)
    record_keeper.add_account_group(name2, 0)
    account_group = record_keeper.root_account_items[0]
    assert account_group.name == name2
    assert account_group.parent is None


@given(
    name=names(),
    parent_name=names(),
)
def test_add_account_group_with_parent(name: str, parent_name: str) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group(parent_name)
    record_keeper.add_account_group(parent_name + "/" + name)
    account_group = record_keeper.account_groups[1]
    parent_group = record_keeper.account_groups[0]
    assert account_group.name == name
    assert account_group.parent == parent_group


@given(
    name1=names(),
    name2=names(),
    parent_name=names(),
)
def test_add_account_group_with_index_and_parent(
    name1: str, name2: str, parent_name: str
) -> None:
    assume(name1 != name2)
    record_keeper = RecordKeeper()
    record_keeper.add_account_group(parent_name)
    record_keeper.add_account_group(parent_name + "/" + name1)
    record_keeper.add_account_group(parent_name + "/" + name2, index=0)
    parent_group = record_keeper.account_groups[0]
    first_child = parent_group.children[0]
    assert first_child.name == name2


@given(
    name=names(),
    grandparent_name=names(),
    parent_name=names(),
)
def test_add_account_group_with_multiple_parents(
    name: str, grandparent_name: str, parent_name: str
) -> None:
    grandparent_path = grandparent_name
    parent_path = grandparent_name + "/" + parent_name
    record_keeper = RecordKeeper()
    record_keeper.add_account_group(grandparent_name)
    record_keeper.add_account_group(grandparent_path + "/" + parent_name)
    record_keeper.add_account_group(parent_path + "/" + name)
    account_group = record_keeper.account_groups[2]
    parent = record_keeper.account_groups[1]
    assert account_group.name == name
    assert account_group.path == f"{parent_path}/{name}"
    assert account_group.parent == parent


@given(
    name=names(),
    currency_code=st.text(string.ascii_letters, min_size=3, max_size=3),
    decimals=st.integers(min_value=0, max_value=8),
    initial_balance=valid_decimals(min_value=0),
    parent_name=st.none() | names(),
)
def test_add_cash_account(
    name: str,
    currency_code: str,
    decimals: int,
    initial_balance: Decimal,
    parent_name: str | None,
) -> None:
    path = parent_name + "/" + name if parent_name is not None else name
    record_keeper = RecordKeeper()
    record_keeper.add_currency(currency_code, decimals)
    if parent_name:
        record_keeper.add_account_group(parent_name)
    record_keeper.add_cash_account(path, currency_code, initial_balance)
    parent_group = record_keeper.account_groups[0] if parent_name else None
    cash_account: CashAccount = record_keeper.accounts[0]
    assert cash_account.name == name
    assert cash_account in record_keeper.cash_accounts
    assert cash_account.currency.code == currency_code.upper()
    assert cash_account.initial_balance == CashAmount(
        initial_balance, cash_account.currency
    )
    assert cash_account.parent == parent_group


@given(
    name=names(),
    parent_name=st.none() | names(),
)
def test_add_security_account(
    name: str,
    parent_name: str | None,
) -> None:
    path = parent_name + "/" + name if parent_name is not None else name
    record_keeper = RecordKeeper()
    if parent_name:
        record_keeper.add_account_group(parent_name)
    record_keeper.add_security_account(path)
    parent_group = record_keeper.account_groups[0] if parent_name else None
    security_account: SecurityAccount = record_keeper.accounts[0]
    assert security_account.name == name
    assert security_account in record_keeper.security_accounts
    assert security_account.parent == parent_group


@given(
    description=st.text(min_size=0, max_size=256),
    datetime_=st.datetimes(
        min_value=datetime.now() + timedelta(days=1),  # noqa: DTZ005
        timezones=st.just(user_settings.settings.time_zone),
    ),
    transaction_type=st.sampled_from(CashTransactionType),
    payee_name=names(),
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
        [CategoryType.INCOME, CategoryType.DUAL_PURPOSE]
        if transaction_type == CashTransactionType.INCOME
        else [CategoryType.EXPENSE, CategoryType.DUAL_PURPOSE]
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
    tag_name_amount_pairs: list[tuple[str, Decimal]] = data.draw(
        st.lists(
            st.tuples(
                names(),
                valid_decimals(min_value=0.01, max_value=max_tag_amount),
            ),
            min_size=0,
            max_size=5,
            unique_by=lambda pair: pair[0],
        )
    )
    record_keeper.add_cash_transaction(
        description,
        datetime_,
        transaction_type,
        account_path,
        payee_name,
        category_name_amount_pairs,
        tag_name_amount_pairs,
    )
    transaction = record_keeper.transactions[0]
    assert transaction in record_keeper.cash_transactions
    assert transaction.datetime_ == datetime_
    assert transaction.description == description.strip()


@given(
    description=st.text(min_size=0, max_size=256),
    datetime_=st.datetimes(
        min_value=datetime.now() + timedelta(days=1),  # noqa: DTZ005
        timezones=st.just(user_settings.settings.time_zone),
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
    assert transfer in record_keeper.cash_transfers
    assert transfer.datetime_ == datetime_
    assert transfer.description == description.strip()


@given(
    code=st.text(string.ascii_letters, min_size=3, max_size=3),
    decimals=st.integers(min_value=0, max_value=8),
)
def test_add_currency_already_exists(code: str, decimals: int) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency(code, decimals)
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_currency(code, decimals)


@given(
    name_1=names(),
    name_2=names(),
    type_=st.sampled_from(CategoryType),
)
def test_add_category_to_root_with_index(
    name_1: str, name_2: str, type_: CategoryType
) -> None:
    assume(name_1 != name_2)
    record_keeper = RecordKeeper()
    record_keeper.add_category(name_1, type_)
    record_keeper.add_category(name_2, type_, 0)
    list_ref = record_keeper._get_root_category_list(record_keeper.get_category(name_2))
    assert list_ref[0].name == name_2


def test_add_category_to_parent_with_index() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_category("PARENT", CategoryType.EXPENSE)
    record_keeper.add_category("PARENT/TEST 1")
    record_keeper.add_category("PARENT/TEST 2", index=0)
    parent = record_keeper.get_category("PARENT")
    assert parent.children[0].name == "TEST 2"


@given(
    name=names(),
    parent=st.text(min_size=1, max_size=32),
    type_=st.sampled_from(CategoryType),
)
def test_add_category_parent_does_not_exist(
    name: str, parent: str, type_: CategoryType
) -> None:
    record_keeper = RecordKeeper()
    path = parent + "/" + name
    with pytest.raises(NotFoundError):
        record_keeper.add_category(path, type_)


@given(
    name=names(),
)
def test_add_category_invalid_type(name: str) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="parameter 'type_'"):
        record_keeper.add_category(name, None, None)


@given(name=names(), type_=st.sampled_from(CategoryType))
def test_add_category_already_exists(name: str, type_: CategoryType) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_category(name, type_)
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_category(name, type_)


@given(
    name=names(),
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
    path = account.path
    currency = data.draw(st.sampled_from(record_keeper.currencies))
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_cash_account(path, currency.code, Decimal(0))


def test_get_account_parent_does_not_exist() -> None:
    record_keeper = get_preloaded_record_keeper()
    with pytest.raises(NotFoundError):
        record_keeper.get_account_group_or_none("does not exist")


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
    with pytest.raises(NotFoundError):
        record_keeper.get_account("does not exist", Account)


@given(code=everything_except(str))
def test_get_currency_invalid_code_type(code: Any) -> None:
    record_keeper = get_preloaded_record_keeper()
    with pytest.raises(TypeError, match="Parameter 'code' must be a string."):
        record_keeper.get_currency(code)


def test_get_currency_does_not_exist() -> None:
    record_keeper = get_preloaded_record_keeper()
    with pytest.raises(NotFoundError):
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
    with pytest.raises(NotFoundError):
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
        datetime.now(user_settings.settings.time_zone),
        refunded_transaction.uuid,
        "Bank Accounts/Raiffeisen CZK",
        refunded_transaction.payee.name,
        (("Food and Drink/Groceries", Decimal(1000)),),
        (("Test Tag", Decimal(1000)),),
    )
    refunded_transaction = record_keeper.transactions[0]
    refund = record_keeper.transactions[1]
    assert refund in refunded_transaction.refunds


def test_add_refund_invalid_uuid_type() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper_with_expense()
    refunded_transaction: CashTransaction = record_keeper.transactions[0]
    with pytest.raises(
        TypeError, match="Parameter 'uuids' must be a Collection ofUUID objects"
    ):
        record_keeper.add_refund(
            description="Refund!",
            datetime_=datetime.now(user_settings.settings.time_zone),
            refunded_transaction_uuid="xxx",
            refunded_account_path="Bank Accounts/Raiffeisen CZK",
            category_path_amount_pairs=(("Food and Drink/Groceries", Decimal(1000)),),
            tag_name_amount_pairs=(("Test Tag", Decimal(1000)),),
            payee_name=refunded_transaction.payee.name,
        )


def test_add_refund_uuid_not_found() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper_with_expense()
    refunded_transaction: CashTransaction = record_keeper.transactions[0]
    with pytest.raises(ValueError, match="not found"):
        record_keeper.add_refund(
            description="Refund!",
            datetime_=datetime.now(user_settings.settings.time_zone),
            refunded_transaction_uuid=uuid4(),
            refunded_account_path="Bank Accounts/Raiffeisen CZK",
            category_path_amount_pairs=(("Food and Drink/Groceries", Decimal(1000)),),
            tag_name_amount_pairs=(("Test Tag", Decimal(1000)),),
            payee_name=refunded_transaction.payee.name,
        )


def test_add_security() -> None:
    record_keeper = RecordKeeper()
    name = "Security Name"
    symbol = "ABCD.EF"
    type_ = "ETF"
    currency_code = "EUR"
    decimals = 2
    unit = 1
    record_keeper.add_currency(currency_code, decimals)
    record_keeper.add_security(name, symbol, type_, currency_code, unit)
    security = record_keeper.get_security_by_name(name)
    assert security.name == name
    assert security.symbol == symbol
    assert security.type_ == type_
    assert security.currency.code == currency_code.upper()
    assert security in record_keeper.securities


def test_add_security_symbol_already_exists() -> None:
    record_keeper = RecordKeeper()
    name_1 = "Security Name"
    name_2 = "Another Name"
    symbol = "ABCD.EF"
    type_ = "ETF"
    type_2 = "Mutual Fund"
    currency_code = "EUR"
    decimals = 2
    unit = 1
    record_keeper.add_currency(currency_code, decimals)
    record_keeper.add_security(name_1, symbol, type_, currency_code, unit)
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_security(name_2, symbol, type_2, currency_code, unit)


def test_add_security_name_already_exists() -> None:
    record_keeper = RecordKeeper()
    name = "Security Name"
    symbol_1 = "ABCD.EF"
    symbol_2 = "GHIJ.KL"
    type_ = "ETF"
    type_2 = "Mutual Fund"
    currency_code = "EUR"
    decimals = 2
    unit = 1
    record_keeper.add_currency(currency_code, decimals)
    record_keeper.add_security(name, symbol_1, type_, currency_code, unit)
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_security(name, symbol_2, type_2, currency_code, unit)


@given(name=everything_except(str))
def test_get_security_by_name_invalid_type(name: Any) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="Parameter 'name' must be a string."):
        record_keeper.get_security_by_name(name)


@given(name=st.text(min_size=1, max_size=32))
def test_get_security_by_name_does_not_exist(name: str) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(NotFoundError):
        record_keeper.get_security_by_name(name)


@given(uuid=everything_except(UUID))
def test_get_security_by_uuid_invalid_type(uuid: Any) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(TypeError, match="Parameter 'uuid' must be a UUID."):
        record_keeper.get_security_by_uuid(uuid)


def test_get_security_by_uuid_does_not_exist() -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(NotFoundError):
        record_keeper.get_security_by_uuid(uuid4())


@given(
    description=st.text(min_size=1, max_size=256),
    type_=st.sampled_from(SecurityTransactionType),
    amount_per_share=valid_decimals(min_value=0.0),
    datetime_=st.datetimes(timezones=st.just(user_settings.settings.time_zone)),
    data=st.data(),
)
def test_add_security_transaction(
    description: str,
    type_: SecurityTransactionType,
    amount_per_share: Decimal,
    datetime_: datetime,
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
    record_keeper.add_security_transaction(
        description,
        datetime_,
        type_,
        security.name,
        shares,
        amount_per_share,
        security_account_path,
        cash_account_path,
    )
    assert len(record_keeper.transactions) == 1
    assert len(record_keeper.security_transactions) == 1


@given(
    description=st.text(min_size=1, max_size=256),
    datetime_=st.datetimes(timezones=st.just(user_settings.settings.time_zone)),
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
        security.name,
        shares,
        account_sender_path,
        account_recipient_path,
    )
    assert len(record_keeper.transactions) == 1
    assert len(record_keeper.security_transfers) == 1


def test_add_security_account_already_exists() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_security_account("Test path")
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_security_account("Test path")


@given(name=names())
def test_add_payee(name: str) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_payee(name)
    payee = record_keeper.get_attribute(name, AttributeType.PAYEE)
    assert len(record_keeper.payees) == 1
    assert payee.name == name


@given(name=names())
def test_add_payee_already_exists(name: str) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_payee(name)
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_payee(name)


@given(name=names())
def test_add_tag(name: str) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_tag(name)
    tag = record_keeper.get_attribute(name, AttributeType.TAG)
    assert len(record_keeper.tags) == 1
    assert tag.name == name


@given(name=names())
def test_add_tag_already_exists(name: str) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_tag(name)
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_tag(name)


def test_account_items() -> None:
    record_keeper = get_preloaded_record_keeper()
    items = record_keeper.account_items
    assert len(items) == len(record_keeper.account_groups) + len(record_keeper.accounts)


def test_save_category() -> None:
    category = Category("Test", CategoryType.DUAL_PURPOSE)
    record_keeper = RecordKeeper()
    record_keeper._save_category(category)
    assert category in record_keeper.categories
    assert category in record_keeper.root_dual_purpose_categories


def test_flatten_categories() -> None:
    cat_1 = Category("1", CategoryType.INCOME)
    cat_1_1 = Category("1.1", CategoryType.INCOME, cat_1)
    cat_1_2 = Category("1.2", CategoryType.INCOME, cat_1)
    cat_1_1_1 = Category("1.1.1", CategoryType.INCOME, cat_1_1)
    cat_2 = Category("2", CategoryType.INCOME)
    cat_2_1 = Category("1.1", CategoryType.INCOME, cat_2)
    cat_2_1_1 = Category("1.1", CategoryType.INCOME, cat_2_1)

    root_categories = [cat_1, cat_2]
    flat_categories = RecordKeeper._flatten_categories(root_categories)
    assert flat_categories == [
        cat_1,
        cat_1_1,
        cat_1_1_1,
        cat_1_2,
        cat_2,
        cat_2_1,
        cat_2_1_1,
    ]


def get_preloaded_record_keeper_with_security_transactions() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper()
    record_keeper.add_security_transaction(
        description="Monthly buy of VWCE",
        datetime_=datetime.now(user_settings.settings.time_zone) - timedelta(days=1),
        type_=SecurityTransactionType.BUY,
        security_name="Vanguard FTSE All-World",
        shares=Decimal(10),
        amount_per_share=Decimal(90),
        security_account_path="Security Accounts/Interactive Brokers",
        cash_account_path="Bank Accounts/Moneta EUR",
    )
    record_keeper.add_security_transaction(
        description="Monthly buy of VWCE",
        datetime_=datetime.now(user_settings.settings.time_zone) - timedelta(days=31),
        type_=SecurityTransactionType.BUY,
        security_name="Vanguard FTSE All-World",
        shares=Decimal(10),
        amount_per_share=Decimal(91),
        security_account_path="Security Accounts/Interactive Brokers",
        cash_account_path="Bank Accounts/Moneta EUR",
    )
    record_keeper.add_security_transaction(
        description="Monthly buy of ČSOB DPS",
        datetime_=datetime.now(user_settings.settings.time_zone) - timedelta(days=1),
        type_=SecurityTransactionType.BUY,
        security_name="ČSOB Dynamický penzijní fond",
        shares=Decimal(2750),
        amount_per_share=Decimal(1.75),
        security_account_path="Security Accounts/ČSOB Penzijní účet",
        cash_account_path="Bank Accounts/Fio CZK",
    )
    record_keeper.add_security_transaction(
        description="Monthly buy of ČSOB DPS",
        datetime_=datetime.now(user_settings.settings.time_zone) - timedelta(days=31),
        type_=SecurityTransactionType.BUY,
        security_name="ČSOB Dynamický penzijní fond",
        shares=Decimal(2850),
        amount_per_share=Decimal(1.6),
        security_account_path="Security Accounts/ČSOB Penzijní účet",
        cash_account_path="Bank Accounts/Fio CZK",
    )
    record_keeper.add_security_transfer(
        description="Security transfer to Degiro",
        datetime_=datetime.now(user_settings.settings.time_zone),
        security_name="Vanguard FTSE All-World",
        shares=Decimal(10),
        account_sender_path="Security Accounts/Interactive Brokers",
        account_recipient_path="Security Accounts/Degiro",
    )
    record_keeper.add_security_transfer(
        description="Security transfer to Degiro",
        datetime_=datetime.now(user_settings.settings.time_zone) - timedelta(days=30),
        security_name="Vanguard FTSE All-World",
        shares=Decimal(10),
        account_sender_path="Security Accounts/Interactive Brokers",
        account_recipient_path="Security Accounts/Degiro",
    )
    return record_keeper


def get_preloaded_record_keeper_with_refunds() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper()
    record_keeper.add_cash_transaction(
        "Shopping for cooking",
        datetime.now(user_settings.settings.time_zone) - timedelta(days=2),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Raiffeisen CZK",
        "Albert",
        (("Food and Drink/Groceries", Decimal(1000)),),
        (("Test Tag", Decimal(1000)),),
    )
    record_keeper.add_cash_transaction(
        "Electronic device",
        datetime.now(user_settings.settings.time_zone) - timedelta(days=2),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Moneta EUR",
        "Alza",
        (("Electronics", Decimal(400)),),
        (("Test Tag", Decimal(400)),),
    )
    transaction_cooking = record_keeper.transactions[0]
    transaction_electronics = record_keeper.transactions[1]

    record_keeper.add_refund(
        description="An expense transaction",
        datetime_=datetime.now(user_settings.settings.time_zone),
        refunded_transaction_uuid=transaction_cooking.uuid,
        refunded_account_path="Bank Accounts/Raiffeisen CZK",
        category_path_amount_pairs=(("Food and Drink/Groceries", Decimal(250)),),
        payee_name="Albert",
        tag_name_amount_pairs=(("Test Tag", Decimal(250)),),
    )
    record_keeper.add_refund(
        description="An expense transaction",
        datetime_=datetime.now(user_settings.settings.time_zone),
        refunded_transaction_uuid=transaction_cooking.uuid,
        refunded_account_path="Bank Accounts/Raiffeisen CZK",
        category_path_amount_pairs=(("Food and Drink/Groceries", Decimal(750)),),
        payee_name="Albert",
        tag_name_amount_pairs=(("Test Tag", Decimal(750)),),
    )
    record_keeper.add_refund(
        description="An expense transaction",
        datetime_=datetime.now(user_settings.settings.time_zone),
        refunded_transaction_uuid=transaction_electronics.uuid,
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
        datetime.now(user_settings.settings.time_zone),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Raiffeisen CZK",
        "Albert",
        (("Food and Drink/Groceries", Decimal(1000)),),
        (("Test Tag", Decimal(1000)),),
    )
    return record_keeper


def get_preloaded_record_keeper_with_cash_transactions() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper()
    record_keeper.add_cash_transaction(
        "Ingredients for cooking",
        datetime.now(user_settings.settings.time_zone),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Raiffeisen CZK",
        "Albert",
        (("Food and Drink/Groceries", Decimal(1000)),),
        (("Split with GF", Decimal(500)),),
    )
    record_keeper.add_cash_transaction(
        "Pizza with GF",
        datetime.now(user_settings.settings.time_zone) - timedelta(days=1),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Raiffeisen CZK",
        "Doe Boy",
        (("Food and Drink/Eating out", Decimal(500)),),
        (("Split with GF", Decimal(250)),),
    )
    record_keeper.add_cash_transaction(
        "Salary",
        datetime.now(user_settings.settings.time_zone) - timedelta(days=7),
        CashTransactionType.INCOME,
        "Bank Accounts/Raiffeisen CZK",
        "Employer",
        (("Salary", Decimal(50000)),),
        (),
    )
    record_keeper.add_cash_transaction(
        "Eating out on vacation",
        datetime.now(user_settings.settings.time_zone) - timedelta(days=180),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Moneta EUR",
        "unknown payee",
        (("Food and Drink/Eating out", Decimal(30)),),
        (("Split with GF", Decimal(15)),),
    )
    return record_keeper


def get_preloaded_record_keeper_with_cash_transfers() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper()
    record_keeper.add_cash_transfer(
        "Salary from Fio to RB",
        datetime.now(user_settings.settings.time_zone) - timedelta(days=7),
        "Bank Accounts/Fio CZK",
        "Bank Accounts/Raiffeisen CZK",
        50000,
        50000,
    )
    record_keeper.add_cash_transfer(
        "Savings from Fio to Creditas",
        datetime.now(user_settings.settings.time_zone) - timedelta(days=37),
        "Bank Accounts/Fio CZK",
        "Bank Accounts/Creditas CZK",
        100000,
        100000,
    )
    record_keeper.add_cash_transfer(
        "Conversion from RB to Moneta",
        datetime.now(user_settings.settings.time_zone) - timedelta(days=6),
        "Bank Accounts/Raiffeisen CZK",
        "Bank Accounts/Moneta EUR",
        25000,
        1000,
    )
    record_keeper.add_cash_transfer(
        "Transfer from Moneta to Revolut",
        datetime.now(user_settings.settings.time_zone) - timedelta(days=5),
        "Bank Accounts/Moneta EUR",
        "Bank Accounts/Revolut EUR",
        1000,
        1000,
    )
    record_keeper.add_cash_transfer(
        "Conversion from Revolut to Fio",
        datetime.now(user_settings.settings.time_zone) - timedelta(days=4),
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
        datetime.now(user_settings.settings.time_zone) - timedelta(days=7),
        "Bank Accounts/Fio CZK",
        "Bank Accounts/Raiffeisen CZK",
        50000,
        50000,
    )
    record_keeper.add_cash_transaction(
        "Ingredients for cooking",
        datetime.now(user_settings.settings.time_zone),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Raiffeisen CZK",
        "Albert",
        (("Food and Drink/Groceries", Decimal(1000)),),
        (("Split with GF", Decimal(500)),),
    )
    record_keeper.add_cash_transaction(
        "Electronic device",
        datetime.now(user_settings.settings.time_zone) - timedelta(days=2),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Moneta EUR",
        "Alza",
        (("Electronics", Decimal(400)),),
        (("Test Tag", Decimal(400)),),
    )
    transaction_electronics = next(
        transaction
        for transaction in record_keeper.transactions
        if transaction.description == "Electronic device"
    )
    record_keeper.add_refund(
        description="An expense transaction",
        datetime_=datetime.now(user_settings.settings.time_zone),
        refunded_transaction_uuid=transaction_electronics.uuid,
        refunded_account_path="Bank Accounts/Moneta EUR",
        category_path_amount_pairs=(("Electronics", Decimal(400)),),
        payee_name="Alza",
        tag_name_amount_pairs=(("Test Tag", Decimal(400)),),
    )
    record_keeper.add_security_transaction(
        description="Monthly buy of ČSOB DPS",
        datetime_=datetime.now(user_settings.settings.time_zone) - timedelta(days=31),
        type_=SecurityTransactionType.BUY,
        security_name="ČSOB Dynamický penzijní fond",
        shares=Decimal(2850),
        amount_per_share=Decimal(1.6),
        security_account_path="Security Accounts/ČSOB Penzijní účet",
        cash_account_path="Bank Accounts/Fio CZK",
    )
    record_keeper.add_security_transfer(
        description="Security transfer to Degiro",
        datetime_=datetime.now(user_settings.settings.time_zone),
        security_name="Vanguard FTSE All-World",
        shares=Decimal(10),
        account_sender_path="Security Accounts/Interactive Brokers",
        account_recipient_path="Security Accounts/Degiro",
    )
    return record_keeper


def get_preloaded_record_keeper() -> RecordKeeper:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_currency("EUR", 2)
    record_keeper.add_currency("BTC", 8)
    record_keeper.add_exchange_rate("EUR", "CZK")
    eur_czk = record_keeper.get_exchange_rate("EUR/CZK")
    eur_czk.set_rate(datetime.now(user_settings.settings.time_zone).date(), Decimal(25))
    record_keeper.add_exchange_rate("BTC", "CZK")
    btc_czk = record_keeper.get_exchange_rate("BTC/CZK")
    btc_czk.set_rate(
        datetime.now(user_settings.settings.time_zone).date(),
        Decimal("600000"),
    )
    record_keeper.add_account_group("Bank Accounts")
    record_keeper.add_account_group("Security Accounts")
    record_keeper.add_cash_account(
        path="Bank Accounts/Raiffeisen CZK",
        currency_code="CZK",
        initial_balance_value=Decimal(1500),
    )
    record_keeper.add_cash_account(
        path="Bank Accounts/Fio CZK",
        currency_code="CZK",
        initial_balance_value=Decimal(0),
    )
    record_keeper.add_cash_account(
        path="Bank Accounts/Creditas CZK",
        currency_code="CZK",
        initial_balance_value=Decimal(100_000),
    )
    record_keeper.add_cash_account(
        path="Bank Accounts/Moneta EUR",
        currency_code="EUR",
        initial_balance_value=Decimal(1600),
    )
    record_keeper.add_cash_account(
        path="Bank Accounts/Revolut EUR",
        currency_code="EUR",
        initial_balance_value=Decimal(0),
    )
    record_keeper.add_security_account("Security Accounts/Degiro")
    record_keeper.add_security_account("Security Accounts/Interactive Brokers")
    record_keeper.add_security_account("Security Accounts/ČSOB Penzijní účet")
    record_keeper.add_security("Vanguard FTSE All-World", "VWCE.DE", "ETF", "EUR", 1)
    record_keeper.add_security("iShares MSCI World", "IWDA.AS", "ETF", "EUR", 1)
    record_keeper.add_security(
        "ČSOB Dynamický penzijní fond", "CSOB.DYN", "Pension Fund", "CZK", 1
    )
    record_keeper.add_category("Food and Drink", CategoryType.EXPENSE)
    record_keeper.add_category("Electronics", CategoryType.EXPENSE)
    record_keeper.add_category("Food and Drink/Groceries")
    record_keeper.add_category("Food and Drink/Eating out")
    record_keeper.add_category("Salary", CategoryType.INCOME)
    record_keeper.add_category("Splitting costs", CategoryType.DUAL_PURPOSE)
    return record_keeper
