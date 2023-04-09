from enum import Enum
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import (
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.security_objects import (
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
)
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.type_filter import TypeFilter
from tests.models.test_assets.composites import (
    everything_except,
    transactions,
    type_filters,
)
from tests.models.test_assets.transaction_list import transaction_list

valid_types = (
    CashTransactionType.INCOME,
    CashTransactionType.EXPENSE,
    RefundTransaction,
    CashTransfer,
    SecurityTransfer,
    SecurityTransactionType.BUY,
    SecurityTransactionType.SELL,
)


def check_transaction(filter_: TypeFilter, transaction: Transaction) -> bool:
    if isinstance(transaction, CashTransaction | SecurityTransaction):
        return transaction.type_ in filter_.enum_types
    return isinstance(transaction, filter_.transaction_types)


@given(
    filter_mode=st.sampled_from(FilterMode),
    types=st.lists(
        st.sampled_from(valid_types),
        min_size=0,
        unique=True,
    ),
)
def test_creation(
    filter_mode: FilterMode,
    types: list[type[Transaction] | CashTransactionType | SecurityTransactionType],
) -> None:
    filter_ = TypeFilter(types, filter_mode)

    type_names = []
    for type_ in types:
        if isinstance(type_, Enum):
            type_names.append(type_.name)
        else:
            type_names.append(type_.__name__)

    assert filter_.mode == filter_mode
    assert filter_.types == frozenset(types)
    assert filter_.type_names == tuple(sorted(type_names))
    assert frozenset(filter_.transaction_types) == frozenset(
        type_ for type_ in types if isinstance(type_, type(Transaction))
    )
    assert frozenset(filter_.enum_types) == frozenset(
        type_
        for type_ in types
        if isinstance(type_, CashTransactionType | SecurityTransactionType)
    )
    assert filter_.__repr__() == (
        f"TypeFilter(types={filter_.type_names}, mode={filter_.mode.name})"
    )


@given(
    types=st.lists(
        everything_except(
            (type(Transaction), CashTransactionType, SecurityTransactionType)
        ),
        min_size=1,
    )
)
def test_invalid_types(types: Any) -> None:
    with pytest.raises(
        TypeError,
        match="Transaction types, CashTransactionType or SecurityTransactionType.",
    ):
        TypeFilter(types, FilterMode.OFF)


@given(
    filter_1=type_filters(),
    filter_2=type_filters(),
)
def test_eq_hash(filter_1: TypeFilter, filter_2: TypeFilter) -> None:
    assert filter_1.__eq__(filter_2) == (
        filter_1.__hash__() == filter_2.__hash__()
    ) or (filter_1.mode == FilterMode.OFF and filter_2.mode == FilterMode.OFF)


@given(
    filter_1=type_filters(),
    filter_2=everything_except(TypeFilter),
)
def test_eq_different_type(filter_1: TypeFilter, filter_2: Any) -> None:
    assert filter_1.__eq__(filter_2) is False


@given(
    transactions=transactions(),
    filter_=type_filters(),
)
def test_filter_off(transactions: list[Transaction], filter_: TypeFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(transactions)


@given(
    transactions=transactions(),
    filter_=type_filters(),
)
def test_filter_keep(transactions: list[Transaction], filter_: TypeFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(
    transactions=transactions(),
    filter_=type_filters(),
)
def test_filter_discard(transactions: list[Transaction], filter_: TypeFilter) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if not check_transaction(filter_, transaction)
    )


@given(filter_=type_filters())
def test_filter_off_premade_transactions(filter_: TypeFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


@given(filter_=type_filters())
def test_filter_keep_premade_transactions(filter_: TypeFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )


@given(filter_=type_filters())
def test_filter_discard_premade_transactions(filter_: TypeFilter) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if not check_transaction(filter_, transaction)
    )


def test_filter_type_names_custom() -> None:
    filter_ = TypeFilter(valid_types, FilterMode.KEEP)

    type_names = []
    for type_ in valid_types:
        if isinstance(type_, Enum):
            type_names.append(type_.name)
        else:
            type_names.append(type_.__name__)

    assert filter_.type_names == tuple(sorted(type_names))
