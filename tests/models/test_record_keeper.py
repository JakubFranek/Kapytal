import string
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.attributes import AttributeType, CategoryType
from src.models.model_objects.cash_objects import CashAccount
from src.models.record_keeper import AlreadyExistsError, DoesNotExistError, RecordKeeper
from tests.models.test_assets.composites import everything_except


def test_creation() -> None:
    record_keeper = RecordKeeper()
    assert record_keeper.accounts == ()
    assert record_keeper.account_groups == ()
    assert record_keeper.transactions == ()
    assert record_keeper.tags == ()
    assert record_keeper.categories == ()
    assert record_keeper.payees == ()
    assert record_keeper.currencies == ()
    assert record_keeper.__repr__() == "RecordKeeper"


@given(code=st.text(string.ascii_letters, min_size=3, max_size=3))
def test_add_currency(code: str) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency(code)
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
    assume(name != parent_name)
    record_keeper = RecordKeeper()
    record_keeper.add_account_group(parent_name, None)
    record_keeper.add_account_group(name, parent_name)
    account_group = record_keeper.account_groups[1]
    parent_group = record_keeper.account_groups[0]
    assert account_group.name == name
    assert account_group.parent == parent_group


@given(
    name=st.text(min_size=1, max_size=32),
    currency_code=st.text(string.ascii_letters, min_size=3, max_size=3),
    initial_balance=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
    initial_datetime=st.datetimes(),
    parent_name=st.none() | st.text(min_size=1, max_size=32),
)
def test_add_cash_account(
    name: str,
    currency_code: str,
    initial_balance: Decimal,
    initial_datetime: datetime,
    parent_name: str | None,
) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency(currency_code)
    if parent_name:
        record_keeper.add_account_group(parent_name, None)
    record_keeper.add_cash_account(
        name, currency_code, initial_balance, initial_datetime, parent_name
    )
    parent_group = record_keeper.account_groups[0] if parent_name else None
    cash_account: CashAccount = record_keeper.accounts[0]
    assert cash_account.name == name
    assert cash_account.currency.code == currency_code.upper()
    assert cash_account.initial_balance == initial_balance
    assert cash_account.initial_datetime == initial_datetime
    assert cash_account.parent == parent_group


@given(
    description=st.text(min_size=0, max_size=256),
    datetime_=st.datetimes(
        min_value=datetime.now() + timedelta(days=1), timezones=st.just(tzinfo)
    ),
    transaction_type=st.sampled_from(["income", "expense"]),
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
    account_name = data.draw(
        st.sampled_from([account.name for account in record_keeper.accounts])
    )
    valid_cat_types = (
        [CategoryType.INCOME, CategoryType.INCOME_AND_EXPENSE]
        if transaction_type == "income"
        else [CategoryType.EXPENSE, CategoryType.INCOME_AND_EXPENSE]
    )
    valid_categories = [
        cat for cat in record_keeper.categories if cat.type_ in valid_cat_types
    ]
    category_name_amount_pairs = data.draw(
        st.lists(
            st.tuples(
                st.sampled_from([str(cat) for cat in valid_categories]),
                st.decimals(min_value="0.01", allow_infinity=False, allow_nan=False),
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
                st.decimals(min_value="0.01", max_value=max_tag_amount),
            ),
            min_size=0,
            max_size=5,
        )
    )
    record_keeper.add_cash_transaction(
        description,
        datetime_,
        transaction_type,
        account_name,
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
    amount_sent=st.decimals(min_value="0.01", allow_infinity=False, allow_nan=False),
    amount_received=st.decimals(
        min_value="0.01", allow_infinity=False, allow_nan=False
    ),
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
    account_sender_name = data.draw(
        st.sampled_from([account.name for account in record_keeper.accounts])
    )
    account_recipient_name = data.draw(
        st.sampled_from(
            [
                account.name
                for account in record_keeper.accounts
                if account.name != account_sender_name
            ]
        )
    )
    record_keeper.add_cash_transfer(
        description,
        datetime_,
        account_sender_name,
        account_recipient_name,
        amount_sent,
        amount_received,
    )
    transfer = record_keeper.transactions[0]
    assert transfer.datetime_ == datetime_
    assert transfer.description == description


@given(code=st.text(string.ascii_letters, min_size=3, max_size=3))
def test_add_currency_already_exists(code: str) -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency(code)
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_currency(code)


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
    with pytest.raises(TypeError, match="If argument 'parent_path' is not provided"):
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
    currency = data.draw(st.sampled_from(record_keeper.currencies))
    with pytest.raises(AlreadyExistsError):
        record_keeper.add_cash_account(
            account.name, currency.code, Decimal(0), datetime.now(), None
        )


def test_get_account_parent_does_not_exist() -> None:
    record_keeper = get_preloaded_record_keeper()
    with pytest.raises(DoesNotExistError):
        record_keeper.get_account_parent("does not exist")


def test_get_account_does_not_exist() -> None:
    record_keeper = get_preloaded_record_keeper()
    with pytest.raises(DoesNotExistError):
        record_keeper.get_account("does not exist")


def test_get_currency_does_not_exist() -> None:
    record_keeper = get_preloaded_record_keeper()
    with pytest.raises(DoesNotExistError):
        record_keeper.get_currency("does not exist")


def test_get_category_does_not_exist() -> None:
    record_keeper = get_preloaded_record_keeper()
    category_path = "One/Two/Three"
    category = record_keeper.get_category(category_path, CategoryType.INCOME)
    assert str(category) == category_path


def test_get_category_parent_exists() -> None:
    record_keeper = get_preloaded_record_keeper()
    parent_path = "One/Two"
    child_path = "One/Two/Three"
    parent = record_keeper.get_category(parent_path, CategoryType.INCOME)
    child = record_keeper.get_category(child_path, CategoryType.INCOME)
    assert str(child) == child_path
    assert str(parent) == parent_path


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


@given(type_=everything_except(str))
def test_get_transaction_type_invalid_type(type_: Any) -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(
        TypeError,
        match="Argument 'type_' must be a string",
    ):
        record_keeper.get_cash_transaction_type(type_)


@given(type_=st.text())
def test_get_transaction_type_invalid_value(type_: str) -> None:
    assume(type_ != "income" and type_ != "expense")
    record_keeper = RecordKeeper()
    with pytest.raises(
        ValueError,
        match="A CashTransactionType can be only 'income' or 'expense'",
    ):
        record_keeper.get_cash_transaction_type(type_)


def test_add_refund() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper_with_expense()
    record_keeper.add_refund(
        "Refund!",
        datetime.now(tzinfo),
        0,
        "Raiffeisen CZK",
        (("Food and Drink/Groceries", Decimal(1000)),),
        (("Test Tag", Decimal(1000)),),
    )
    refunded_transaction = record_keeper.transactions[0]
    refund = record_keeper.transactions[1]
    assert refund in refunded_transaction.refunds


def get_preloaded_record_keeper_with_expense() -> RecordKeeper:
    record_keeper = get_preloaded_record_keeper()
    record_keeper.add_cash_transaction(
        "An expense transaction",
        datetime.now(tzinfo),
        "expense",
        "Raiffeisen CZK",
        (("Food and Drink/Groceries", Decimal(1000)),),
        "Albert",
        (("Test Tag", Decimal(1000)),),
    )
    return record_keeper


def get_preloaded_record_keeper() -> RecordKeeper:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK")
    record_keeper.add_currency("EUR")
    record_keeper.add_account_group("Bank Accounts", None)
    record_keeper.add_cash_account(
        name="Raiffeisen CZK",
        currency_code="CZK",
        initial_balance=Decimal(1500),
        initial_datetime=datetime.now(tzinfo),
        parent_name="Bank Accounts",
    )
    record_keeper.add_cash_account(
        name="Moneta EUR",
        currency_code="EUR",
        initial_balance=Decimal(1600),
        initial_datetime=datetime.now(tzinfo),
        parent_name="Bank Accounts",
    )
    record_keeper.add_category("Food and Drink", None, CategoryType.EXPENSE)
    record_keeper.add_category("Groceries", "Food and Drink")
    record_keeper.add_category("Eating out", "Food and Drink")
    record_keeper.add_category("Salary", None, CategoryType.INCOME)
    record_keeper.add_category("Splitting costs", None, CategoryType.INCOME_AND_EXPENSE)
    return record_keeper
