from collections.abc import Collection
from datetime import datetime
from decimal import Decimal
from types import NoneType
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
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
from src.models.model_objects.currency_objects import (
    CashAmount,
    Currency,
    CurrencyError,
)
from src.models.user_settings import user_settings
from tests.models.test_assets.composites import (
    attributes,
    cash_accounts,
    cash_amounts,
    cash_transactions,
    categories,
    category_amount_pairs,
    currencies,
    everything_except,
    tag_amount_pairs,
)
from tests.models.test_assets.constants import MIN_DATETIME


@given(
    description=st.text(min_size=0, max_size=256),
    datetime_=st.datetimes(
        min_value=MIN_DATETIME, timezones=st.just(user_settings.settings.time_zone)
    ),
    type_=st.sampled_from(CashTransactionType),
    account=cash_accounts(),
    payee=attributes(AttributeType.PAYEE),
    data=st.data(),
)
def test_creation(  # noqa: PLR0913
    description: str,
    datetime_: datetime,
    type_: CashTransactionType,
    account: CashAccount,
    payee: Attribute,
    data: st.DataObject,
) -> None:
    currency = account.currency
    category_amount_collection = data.draw(
        st.lists(
            category_amount_pairs(transaction_type=type_, currency=currency),
            min_size=1,
            max_size=5,
        )
    )
    max_tag_amount = sum(
        (amount for _, amount in category_amount_collection),
        start=CashAmount(0, currency),
    )
    tag_amount_collection = data.draw(
        st.lists(
            tag_amount_pairs(currency=currency, max_value=max_tag_amount.value_rounded),
            min_size=0,
            max_size=5,
        )
    )
    account_currency = account.currency
    dt_start = datetime.now(user_settings.settings.time_zone).replace(microsecond=0)
    cash_transaction = CashTransaction(
        description,
        datetime_,
        type_,
        account,
        payee,
        category_amount_collection,
        tag_amount_collection,
    )

    categories = tuple(category for category, _ in category_amount_collection)

    dt_created_diff = cash_transaction.datetime_created - dt_start

    assert cash_transaction.description == description
    assert cash_transaction.datetime_ == datetime_
    assert cash_transaction.type_ == type_
    assert cash_transaction.account == account
    assert cash_transaction.currency == account_currency
    assert cash_transaction.currencies == (account_currency,)
    assert cash_transaction.category_amount_pairs == tuple(category_amount_collection)
    assert cash_transaction.categories == categories
    assert cash_transaction.payee == payee
    assert cash_transaction.tag_amount_pairs == tuple(tag_amount_collection)
    assert cash_transaction in account.transactions
    assert cash_transaction.__repr__() == (
        f"CashTransaction({cash_transaction.type_.name}, "
        f"account='{cash_transaction.account.name}', "
        f"amount={cash_transaction.amount}, "
        f"category={{{cash_transaction.category_names}}}, "
        f"{cash_transaction.datetime_.strftime('%Y-%m-%d')})"
    )
    assert dt_created_diff.seconds < 1


@given(
    account=cash_accounts(),
    type_=everything_except((CashTransactionType, NoneType)),
)
def test_type_invalid_type(
    account: CashAccount,
    type_: Any,
) -> None:
    payee = Attribute("Test", AttributeType.PAYEE)
    category_amount_collection = [
        (
            Category("Test", CategoryType.INCOME_AND_EXPENSE),
            CashAmount(1, account.currency),
        )
    ]
    tag_amount_collection = [
        (Attribute("Test", AttributeType.TAG), CashAmount(1, account.currency))
    ]
    with pytest.raises(
        TypeError, match="CashTransaction.type_ must be a CashTransactionType."
    ):
        CashTransaction(
            "description",
            datetime.now(user_settings.settings.time_zone),
            type_,
            account,
            payee,
            category_amount_collection,
            tag_amount_collection,
        )


@given(
    transaction=cash_transactions(),
    new_account=everything_except((CashAccount, NoneType)),
)
def test_account_invalid_type(transaction: CashTransaction, new_account: Any) -> None:
    with pytest.raises(
        TypeError, match="CashTransaction.account must be a CashAccount."
    ):
        transaction.set_attributes(account=new_account)


@given(
    transaction=cash_transactions(), new_payee=everything_except((Attribute, NoneType))
)
def test_payee_invalid_type(transaction: CashTransaction, new_payee: Any) -> None:
    with pytest.raises(TypeError, match="Payee must be an Attribute."):
        transaction.set_attributes(payee=new_payee)


@given(transaction=cash_transactions(), new_payee=attributes(AttributeType.TAG))
def test_payee_invalid_attribute_type(
    transaction: CashTransaction, new_payee: Any
) -> None:
    with pytest.raises(ValueError, match="The type_ of payee Attribute must be PAYEE."):
        transaction.set_attributes(payee=new_payee)


@given(
    transaction=cash_transactions(), new_tags=everything_except((Collection, NoneType))
)
def test_tags_invalid_type(transaction: CashTransaction, new_tags: Any) -> None:
    with pytest.raises(TypeError, match="Parameter 'collection' must be a Collection."):
        transaction.set_attributes(tag_amount_pairs=new_tags)


@given(transaction=cash_transactions(), data=st.data())
def test_tags_invalid_first_member_type(
    transaction: CashTransaction, data: st.DataObject
) -> None:
    max_tag_amount = transaction.amount
    new_tags = [(data.draw(everything_except(Attribute)), max_tag_amount)]
    with pytest.raises(
        TypeError,
        match="First element of 'collection' tuples",
    ):
        transaction.set_attributes(tag_amount_pairs=new_tags)


@given(transaction=cash_transactions())
def test_tags_invalid_attribute_type(transaction: CashTransaction) -> None:
    max_tag_amount = transaction.amount
    new_tags = [(Attribute("Test", AttributeType.PAYEE), max_tag_amount)]
    with pytest.raises(
        ValueError,
        match="The type_ of CashTransaction.tag_amount_pairs Attributes must be TAG.",
    ):
        transaction.set_attributes(tag_amount_pairs=new_tags)


@given(transaction=cash_transactions(), data=st.data())
def test_tags_invalid_second_member_type(
    transaction: CashTransaction, data: st.DataObject
) -> None:
    new_tags = [
        (Attribute("Test", AttributeType.TAG), data.draw(everything_except(CashAmount)))
    ]
    with pytest.raises(
        TypeError,
        match="Second element of 'collection' tuples",
    ):
        transaction.set_attributes(tag_amount_pairs=new_tags)


@given(transaction=cash_transactions(), data=st.data())
def test_tags_invalid_second_member_value(
    transaction: CashTransaction, data: st.DataObject
) -> None:
    max_tag_amount = transaction.amount
    currency = transaction.currency
    new_tags = [
        (
            Attribute("Test", AttributeType.TAG),
            data.draw(
                cash_amounts(
                    currency=currency,
                    min_value=max_tag_amount.value_rounded + Decimal("0.01"),
                    max_value=max_tag_amount.value_rounded + Decimal("1e3"),
                )
            ),
        )
    ]
    with pytest.raises(
        ValueError,
        match="Second member of CashTransaction.tag_amount_pairs",
    ):
        transaction.set_attributes(tag_amount_pairs=new_tags)


@given(
    transaction=cash_transactions(),
    invalid_currency=currencies(),
    data=st.data(),
)
def test_tag_amount_pairs_invalid_amount_currency(
    transaction: CashTransaction, invalid_currency: Currency, data: st.DataObject
) -> None:
    assume(invalid_currency != transaction.currency)
    max_amount = transaction.amount
    amount = data.draw(
        cash_amounts(
            min_value="0.01",
            max_value=max_amount.value_rounded,
            currency=invalid_currency,
        ),
    )
    tag = data.draw(attributes(type_=AttributeType.TAG))
    tup = ((tag, amount),)
    with pytest.raises(
        CurrencyError, match="Currency of CashAmounts in tag_amount_pairs"
    ):
        transaction.set_attributes(tag_amount_pairs=tup)


@given(
    transaction=cash_transactions(),
    data=st.data(),
)
def test_tag_amount_pairs_not_unique(
    transaction: CashTransaction, data: st.DataObject
) -> None:
    max_amount = transaction.amount
    amount = data.draw(
        cash_amounts(
            min_value="0.01",
            max_value=max_amount.value_rounded,
            currency=transaction.currency,
        ),
    )
    tag = data.draw(attributes(type_=AttributeType.TAG))
    tup = (
        (tag, amount),
        (tag, amount),
    )
    with pytest.raises(
        ValueError, match="Categories or Tags in tuple pairs must be unique."
    ):
        transaction.set_attributes(tag_amount_pairs=tup)


@given(transaction=cash_transactions(), data=st.data())
def test_change_account(transaction: CashTransaction, data: st.DataObject) -> None:
    new_account = data.draw(cash_accounts(currency=transaction.currency))
    previous_account = transaction.account
    assert transaction in previous_account.transactions
    assert transaction not in new_account.transactions
    transaction.set_attributes(account=new_account)
    assert transaction in new_account.transactions
    assert transaction not in previous_account.transactions


@given(transaction=cash_transactions())
def test_get_amount(transaction: CashTransaction) -> None:
    account = transaction.account
    amount = transaction.amount
    if transaction.type_ == CashTransactionType.INCOME:
        expected_amount = amount
    else:
        expected_amount = -amount

    result = transaction.get_amount(account)
    assert result == expected_amount


@given(
    transaction=cash_transactions(),
    account=everything_except(CashAccount),
)
def test_get_amount_invalid_account_type(
    transaction: CashTransaction, account: Any
) -> None:
    with pytest.raises(TypeError, match="Parameter 'account' must be a CashAccount."):
        transaction.get_amount(account)


@given(
    transaction=cash_transactions(),
    account=cash_accounts(),
)
def test_get_amount_invalid_account_value(
    transaction: CashTransaction, account: CashAccount
) -> None:
    assume(transaction.account != account)
    with pytest.raises(UnrelatedAccountError):
        transaction.get_amount(account)


@given(
    transaction=cash_transactions(),
    category_amount_pairs=everything_except((Collection, NoneType)),
)
def test_category_amount_pairs_invalid_type(
    transaction: CashTransaction, category_amount_pairs: Any
) -> None:
    with pytest.raises(TypeError, match="Parameter 'collection' must be a Collection."):
        transaction.set_attributes(category_amount_pairs=category_amount_pairs)


@given(
    transaction=cash_transactions(),
    category_amount_pairs=st.lists(everything_except(tuple), min_size=1, max_size=5),
)
def test_category_amount_pairs_invalid_member_type(
    transaction: CashTransaction, category_amount_pairs: Collection[Any]
) -> None:
    with pytest.raises(TypeError, match="Elements of 'collection' must be tuples."):
        transaction.set_attributes(category_amount_pairs=category_amount_pairs)


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
        transaction.set_attributes(category_amount_pairs=category_amount_pairs)


@given(
    transaction=cash_transactions(),
    first_member=everything_except(Category),
)
def test_category_amount_pairs_invalid_first_member_type(
    transaction: CashTransaction,
    first_member: Any,
) -> None:
    tup = ((first_member, transaction.amount),)
    with pytest.raises(
        TypeError,
        match="First element of 'collection' tuples",
    ):
        transaction.set_attributes(category_amount_pairs=tup)


@given(
    transaction=cash_transactions(),
    second_member=everything_except((CashAmount, NoneType)),
    data=st.data(),
)
def test_category_amount_pairs_invalid_second_member_type(
    transaction: CashTransaction, second_member: Any, data: st.DataObject
) -> None:
    first_member = Category(
        "Test",
        data.draw(st.sampled_from(transaction._get_valid_category_types())),
    )
    tup = ((first_member, second_member),)
    with pytest.raises(
        TypeError,
        match="Second element of 'collection' tuples",
    ):
        transaction.set_attributes(category_amount_pairs=tup)


@given(
    transaction=cash_transactions(),
    second_member=everything_except((CashAmount, NoneType)),
    data=st.data(),
)
def test_category_amount_pairs_invalid_second_member_type_multiple(
    transaction: CashTransaction, second_member: Any, data: st.DataObject
) -> None:
    first_member = Category(
        "Test",
        data.draw(st.sampled_from(transaction._get_valid_category_types())),
    )
    first_member2 = Category(
        "Test2",
        data.draw(st.sampled_from(transaction._get_valid_category_types())),
    )
    tup = [(first_member, second_member), (first_member2, second_member)]
    with pytest.raises(
        TypeError,
        match="Second element of 'collection' tuples",
    ):
        transaction.set_attributes(category_amount_pairs=tup)


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
    tup = ((category, transaction.amount),)
    with pytest.raises(
        InvalidCategoryTypeError,
        match="Invalid Category.type_.",
    ):
        transaction.set_attributes(category_amount_pairs=tup)


@given(
    transaction=cash_transactions(),
    data=st.data(),
)
def test_category_amount_pairs_invalid_amount_value(
    transaction: CashTransaction, data: st.DataObject
) -> None:
    amount = data.draw(
        cash_amounts(max_value=0, currency=transaction.currency),
    )
    category = Category(
        "Test",
        data.draw(st.sampled_from(transaction._get_valid_category_types())),
    )
    tup = ((category, amount),)
    with pytest.raises(
        ValueError,
        match="must be a positive CashAmount.",
    ):
        transaction.set_attributes(category_amount_pairs=tup)


@given(
    transaction=cash_transactions(),
    data=st.data(),
)
def test_category_amount_pairs_not_unique(
    transaction: CashTransaction, data: st.DataObject
) -> None:
    amount = data.draw(
        cash_amounts(max_value=0, currency=transaction.currency),
    )
    category = Category(
        "Test",
        data.draw(st.sampled_from(transaction._get_valid_category_types())),
    )
    tup = (
        (category, amount),
        (category, 2 * amount),
    )
    with pytest.raises(
        ValueError,
        match="Categories in category_amount_pairs must be unique.",
    ):
        transaction.set_attributes(category_amount_pairs=tup)


@given(
    transaction=cash_transactions(),
    invalid_currency=currencies(),
    data=st.data(),
)
def test_category_amount_pairs_invalid_amount_currency(
    transaction: CashTransaction, invalid_currency: Currency, data: st.DataObject
) -> None:
    assume(invalid_currency != transaction.currency)
    amount = data.draw(
        cash_amounts(min_value=0.01, currency=invalid_currency),
    )
    category = Category(
        "Test",
        data.draw(st.sampled_from(transaction._get_valid_category_types())),
    )
    tup = ((category, amount),)
    with pytest.raises(CurrencyError):
        transaction.set_attributes(category_amount_pairs=tup)


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
def test_invalid_refund_type(transaction: CashTransaction, refund: Any) -> None:
    with pytest.raises(
        TypeError, match="Parameter 'refund' must be a RefundTransaction."
    ):
        transaction.add_refund(refund)


@given(
    transaction=cash_transactions(),
)
def test_validate_attributes_same_values(
    transaction: CashTransaction,
) -> None:
    transaction.validate_attributes()


@given(
    transaction=cash_transactions(),
)
def test_set_attributes_same_values(
    transaction: CashTransaction,
) -> None:
    prev_description = transaction.description
    prev_datetime = transaction.datetime_
    prev_payee = transaction.payee
    prev_type = transaction.type_
    prev_account = transaction.account
    prev_category_amount_pairs = transaction.category_amount_pairs
    prev_tag_amount_pairs = transaction.tag_amount_pairs
    transaction.set_attributes()
    assert prev_description == transaction.description
    assert prev_datetime == transaction.datetime_
    assert prev_payee == transaction.payee
    assert prev_type == transaction.type_
    assert prev_account == transaction.account
    assert prev_category_amount_pairs == transaction.category_amount_pairs
    assert prev_tag_amount_pairs == transaction.tag_amount_pairs


@given(
    transaction=cash_transactions(),
    tags=st.lists(attributes(AttributeType.TAG), min_size=1, max_size=5),
)
def test_add_remove_tags(transaction: CashTransaction, tags: list[Attribute]) -> None:
    transaction.add_tags(tags)
    for tag in tags:
        assert tag in transaction.tags
        transaction.remove_tags([tag])
        assert tag not in transaction.tags


@given(transaction=cash_transactions(), category=categories(), total=st.booleans())
def test_get_amount_for_category_not_related(
    transaction: CashTransaction, category: Category, total: bool  # noqa: FBT001
) -> None:
    assume(category not in transaction.categories)
    assert transaction.get_amount_for_category(category, total) == CashAmount(
        0, transaction.currency
    )


@given(transaction=cash_transactions(), tag=attributes(type_=AttributeType.TAG))
def test_get_amount_for_tag_not_related(
    transaction: CashTransaction, tag: Attribute
) -> None:
    assume(tag not in transaction.tags)
    assert transaction.get_amount_for_tag(tag) == CashAmount(0, transaction.currency)


@given(transaction=cash_transactions(), unrelated_account=cash_accounts())
def test_is_accounts_related(
    transaction: CashTransaction, unrelated_account: CashAccount
) -> None:
    related_accounts = (transaction.account, unrelated_account)
    assert transaction.is_accounts_related(related_accounts)
    unrelated_accounts = (unrelated_account,)
    assert not transaction.is_accounts_related(unrelated_accounts)
