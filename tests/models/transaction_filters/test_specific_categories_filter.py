from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import Category, CategoryType
from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.specific_categories_filter import (
    SpecificCategoriesFilter,
)
from tests.models.test_assets.composites import (
    categories,
    everything_except,
    specific_categories_filters,
    transactions,
)
from tests.models.test_assets.transaction_list import transaction_list


def check_transaction(
    filter_: SpecificCategoriesFilter, transaction: Transaction
) -> bool:
    if filter_.mode == FilterMode.OFF:
        return True
    if not isinstance(transaction, CashTransaction | RefundTransaction):
        return True
    if filter_.mode == FilterMode.KEEP:
        return any(
            category in filter_.categories for category in transaction.categories
        )
    return not any(
        category in filter_.categories for category in transaction.categories
    )


@given(categories=st.lists(categories()), mode=st.sampled_from(FilterMode))
def test_creation(categories: list[Category], mode: FilterMode) -> None:
    filter_ = SpecificCategoriesFilter(categories, mode)
    income_categories = frozenset(
        category for category in categories if category.type_ == CategoryType.INCOME
    )
    expense_categories = frozenset(
        category for category in categories if category.type_ == CategoryType.EXPENSE
    )
    income_and_expense_categories = frozenset(
        category
        for category in categories
        if category.type_ == CategoryType.INCOME_AND_EXPENSE
    )
    assert filter_.categories == frozenset(categories)
    assert filter_.income_categories == income_categories
    assert filter_.expense_categories == expense_categories
    assert filter_.income_and_expense_categories == income_and_expense_categories
    assert filter_.category_paths == tuple(
        sorted(category.path for category in categories)
    )
    assert filter_.mode == mode
    assert filter_.__repr__() == (
        f"SpecificCategoriesFilter(categories={frozenset(categories)}, "
        f"mode={mode.name})"
    )


@given(
    categories=st.lists(everything_except(Category), min_size=1, max_size=10),
    mode=st.sampled_from(FilterMode),
)
def test_creation_invalid_type(categories: list[Any], mode: FilterMode) -> None:
    with pytest.raises(TypeError, match="must be a Collection of Categories"):
        SpecificCategoriesFilter(categories, mode)


@given(filter_1=specific_categories_filters(), filter_2=specific_categories_filters())
def test_eq_hash(
    filter_1: SpecificCategoriesFilter, filter_2: SpecificCategoriesFilter
) -> None:
    assert filter_1.__eq__(filter_2) == (
        filter_1.__hash__() == filter_2.__hash__()
    ) or (filter_1.mode == FilterMode.OFF and filter_2.mode == FilterMode.OFF)


@given(
    filter_1=specific_categories_filters(),
    filter_2=everything_except(SpecificCategoriesFilter),
)
def test_eq_different_type(filter_1: SpecificCategoriesFilter, filter_2: Any) -> None:
    assert filter_1.__eq__(filter_2) is False


@given(transactions=transactions(), filter_=specific_categories_filters())
def test_filter_off(
    transactions: list[Transaction], filter_: SpecificCategoriesFilter
) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(transactions)


@given(transactions=transactions(), filter_=specific_categories_filters())
def test_filter_keep(
    transactions: list[Transaction], filter_: SpecificCategoriesFilter
) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(transactions=transactions(), filter_=specific_categories_filters())
def test_filter_discard(
    transactions: list[Transaction], filter_: SpecificCategoriesFilter
) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(filter_=specific_categories_filters())
def test_filter_off_premade_transactions(filter_: SpecificCategoriesFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


@given(filter_=specific_categories_filters())
def test_filter_keep_premade_transactions(filter_: SpecificCategoriesFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transaction_list)
    expected = tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )
    assert filtered == expected


@given(filter_=specific_categories_filters())
def test_filter_discard_premade_transactions(filter_: SpecificCategoriesFilter) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )
