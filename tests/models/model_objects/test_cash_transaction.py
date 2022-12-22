from collections.abc import Collection
from datetime import datetime
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.constants import tzinfo
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
    InvalidCategoryTypeError,
    RefundTransaction,
    UnrelatedAccountError,
)
from tests.models.test_assets.composites import (
    attributes,
    cash_accounts,
    cash_transactions,
    category_amount_pairs,
    everything_except,
    tag_amount_pairs,
)
from tests.models.test_assets.constants import min_datetime


@given(
    description=st.text(min_size=0, max_size=256),
    datetime_=st.datetimes(min_value=min_datetime),
    type_=st.sampled_from(CashTransactionType),
    account=cash_accounts(),
    payee=attributes(AttributeType.PAYEE),
    data=st.data(),
)
def test_creation(  # noqa: CFQ002,TMN001
    description: str,
    datetime_: datetime,
    type_: CashTransactionType,
    account: CashAccount,
    payee: Attribute,
    data: st.DataObject,
) -> None:
    category_amount_collection = data.draw(
        st.lists(category_amount_pairs(type_), min_size=1, max_size=5)
    )
    max_tag_amount = sum(amount for _, amount in category_amount_collection)
    tag_amount_collection = data.draw(
        st.lists(tag_amount_pairs(max_tag_amount), min_size=0, max_size=5)
    )
    account_currency = account.currency
    dt_start = datetime.now(tzinfo)
    cash_transaction = CashTransaction(
        description,
        datetime_,
        type_,
        account,
        category_amount_collection,
        payee,
        tag_amount_collection,
    )

    dt_created_diff = cash_transaction.datetime_created - dt_start
    dt_edited_diff = cash_transaction.datetime_edited - dt_start

    assert cash_transaction.description == description
    assert cash_transaction.datetime_ == datetime_
    assert cash_transaction.type_ == type_
    assert cash_transaction.account == account
    assert cash_transaction.currency == account_currency
    assert cash_transaction.category_amount_pairs == tuple(category_amount_collection)
    assert cash_transaction.payee == payee
    assert cash_transaction.tag_amount_pairs == tuple(tag_amount_collection)
    assert cash_transaction in account.transactions
    assert cash_transaction.__repr__() == (
        f"CashTransaction({cash_transaction.type_.name}, "
        f"account='{cash_transaction.account.name}', "
        f"amount={cash_transaction.amount} "
        f"{cash_transaction.account.currency.code}, "
        f"category={{{cash_transaction.category_names}}}, "
        f"{cash_transaction.datetime_.strftime('%Y-%m-%d')})"
    )
    assert dt_created_diff.seconds < 1
    assert dt_edited_diff.seconds < 1


@given(
    account=cash_accounts(),
    type_=everything_except(CashTransactionType),
)
def test_type_invalid_type(  # noqa: CFQ002,TMN001
    account: CashAccount,
    type_: Any,
) -> None:
    payee = Attribute("Test", AttributeType.PAYEE)
    category_amount_collection = [
        (Category("Test", CategoryType.INCOME_AND_EXPENSE), Decimal(1))
    ]
    tag_amount_collection = [(Attribute("Test", AttributeType.TAG), Decimal(1))]
    with pytest.raises(
        TypeError, match="CashTransaction.type_ must be a CashTransactionType."
    ):
        CashTransaction(
            "description",
            datetime.now(tzinfo),
            type_,
            account,
            category_amount_collection,
            payee,
            tag_amount_collection,
        )


@given(transaction=cash_transactions(), new_account=everything_except(CashAccount))
def test_account_invalid_type(transaction: CashTransaction, new_account: Any) -> None:
    with pytest.raises(
        TypeError, match="CashTransaction.account must be a CashAccount."
    ):
        transaction.account = new_account


@given(transaction=cash_transactions(), new_payee=everything_except(Attribute))
def test_payee_invalid_type(transaction: CashTransaction, new_payee: Any) -> None:
    with pytest.raises(TypeError, match="CashTransaction.payee must be an Attribute."):
        transaction.payee = new_payee


@given(transaction=cash_transactions(), new_payee=attributes(AttributeType.TAG))
def test_payee_invalid_attribute_type(
    transaction: CashTransaction, new_payee: Any
) -> None:
    with pytest.raises(
        ValueError, match="The type_ of CashTransaction.payee Attribute must be PAYEE."
    ):
        transaction.payee = new_payee


@given(transaction=cash_transactions(), new_tags=everything_except(Collection))
def test_tags_invalid_type(transaction: CashTransaction, new_tags: Any) -> None:
    with pytest.raises(TypeError, match="Argument 'collection' must be a Collection."):
        transaction.tag_amount_pairs = new_tags


@given(transaction=cash_transactions(), data=st.data())
def test_tags_invalid_first_member_type(
    transaction: CashTransaction, data: st.DataObject
) -> None:
    max_tag_amount = transaction.amount
    new_tags = [(data.draw(everything_except(Attribute)), Decimal(max_tag_amount))]
    with pytest.raises(
        TypeError,
        match="First element of 'collection' tuples",
    ):
        transaction.tag_amount_pairs = new_tags


@given(transaction=cash_transactions())
def test_tags_invalid_attribute_type(transaction: CashTransaction) -> None:
    max_tag_amount = transaction.amount
    new_tags = [(Attribute("Test", AttributeType.PAYEE), Decimal(max_tag_amount))]
    with pytest.raises(
        ValueError,
        match="The type_ of CashTransaction.tag_amount_pairs Attributes must be TAG.",
    ):
        transaction.tag_amount_pairs = new_tags


@given(transaction=cash_transactions(), data=st.data())
def test_tags_invalid_second_member_type(
    transaction: CashTransaction, data: st.DataObject
) -> None:
    new_tags = [
        (Attribute("Test", AttributeType.TAG), data.draw(everything_except(Decimal)))
    ]
    with pytest.raises(
        TypeError,
        match="Second element of 'collection' tuples",
    ):
        transaction.tag_amount_pairs = new_tags


@given(transaction=cash_transactions(), data=st.data())
def test_tags_invalid_second_member_value(
    transaction: CashTransaction, data: st.DataObject
) -> None:
    max_tag_amount = transaction.amount
    new_tags = [
        (
            Attribute("Test", AttributeType.TAG),
            data.draw(st.decimals(min_value=max_tag_amount + Decimal("0.01"))),
        )
    ]
    with pytest.raises(
        ValueError,
        match="Second member of CashTransaction.tag_amount_pairs",
    ):
        transaction.tag_amount_pairs = new_tags


@given(
    transaction=cash_transactions(),
    new_account=cash_accounts(),
)
def test_change_account(transaction: CashTransaction, new_account: CashAccount) -> None:
    previous_account = transaction.account
    assert transaction in previous_account.transactions
    assert transaction not in new_account.transactions
    transaction.account = new_account
    assert transaction in new_account.transactions
    assert transaction not in previous_account.transactions


@given(transaction=cash_transactions())
def test_get_amount_for_account(transaction: CashTransaction) -> None:
    account = transaction.account
    amount = transaction.amount
    if transaction.type_ == CashTransactionType.INCOME:
        expected_amount = amount
    else:
        expected_amount = -amount

    result = transaction.get_amount_for_account(account)
    assert result == expected_amount


@given(
    transaction=cash_transactions(),
    account=cash_accounts(),
)
def test_get_amount_for_account_invalid_account_value(
    transaction: CashTransaction, account: CashAccount
) -> None:
    assume(transaction.account != account)
    with pytest.raises(UnrelatedAccountError):
        transaction.get_amount_for_account(account)


@given(
    transaction=cash_transactions(), category_amount_pairs=everything_except(Collection)
)
def test_category_amount_pairs_invalid_type(
    transaction: CashTransaction, category_amount_pairs: Any
) -> None:
    with pytest.raises(TypeError, match="Argument 'collection' must be a Collection."):
        transaction.tag_amount_pairs = category_amount_pairs


@given(
    transaction=cash_transactions(),
    category_amount_pairs=st.sampled_from(["", [], {}, ()]),
)
def test_category_amount_pairs_invalid_length(
    transaction: CashTransaction, category_amount_pairs: Any
) -> None:
    with pytest.raises(
        ValueError,
        match="Length of 'collection' must be",
    ):
        transaction.category_amount_pairs = category_amount_pairs


@given(
    transaction=cash_transactions(),
    first_member=everything_except(Category),
)
def test_category_amount_pairs_invalid_first_member_type(
    transaction: CashTransaction,
    first_member: Any,
) -> None:
    tup = ((first_member, Decimal(transaction.amount)),)
    with pytest.raises(
        TypeError,
        match="First element of 'collection' tuples",
    ):
        transaction.tag_amount_pairs = tup


@given(
    transaction=cash_transactions(),
    second_member=everything_except(Decimal),
    data=st.data(),
)
def test_category_amount_pairs_invalid_second_member_type(
    transaction: CashTransaction, second_member: Any, data: st.DataObject
) -> None:
    first_member = Category(
        "Test", data.draw(st.sampled_from(transaction._valid_category_types))
    )
    tup = ((first_member, second_member),)
    with pytest.raises(
        TypeError,
        match="Second element of 'collection' tuples",
    ):
        transaction.category_amount_pairs = tup


@given(
    transaction=cash_transactions(),
)
def test_category_amount_pairs_invalid_category_type(
    transaction: CashTransaction,
) -> None:
    type_ = (
        CategoryType.INCOME
        if transaction.type_ == CashTransactionType.EXPENSE
        else CategoryType.EXPENSE
    )
    category = Category("Test", type_)
    tup = ((category, Decimal(transaction.amount)),)
    with pytest.raises(
        InvalidCategoryTypeError,
        match="Invalid Category.type_.",
    ):
        transaction.category_amount_pairs = tup


@given(
    transaction=cash_transactions(),
    amount=st.decimals(max_value=0, allow_infinity=True, allow_nan=True),
    data=st.data(),
)
def test_category_amount_pairs_invalid_amount_value(
    transaction: CashTransaction, amount: Decimal, data: st.DataObject
) -> None:
    category = Category(
        "Test", data.draw(st.sampled_from(transaction._valid_category_types))
    )
    tup = ((category, amount),)
    with pytest.raises(
        ValueError,
        match="must be a positive and finite Decimal.",
    ):
        transaction.category_amount_pairs = tup


@given(transaction=cash_transactions())
def test_category_names(transaction: CashTransaction) -> None:
    names = []
    for category, _ in transaction.category_amount_pairs:
        names.append(category.path)

    assert ", ".join(names) == transaction.category_names


@given(transaction=cash_transactions())
def test_tag_names(transaction: CashTransaction) -> None:
    names: list[str] = []
    for tag, _amount in transaction.tag_amount_pairs:
        names.append(tag.name)

    assert ", ".join(names) == transaction.tag_names


@given(transaction=cash_transactions(), refund=everything_except(RefundTransaction))
def test_invalid_refund_transaction(transaction: CashTransaction, refund: Any) -> None:
    with pytest.raises(
        TypeError, match="Argument 'refund' must be a RefundTransaction."
    ):
        transaction.add_refund(refund)
