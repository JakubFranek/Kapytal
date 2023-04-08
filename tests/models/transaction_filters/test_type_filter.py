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
from src.models.transaction_filters.filter_mode_mixin import FilterMode
from src.models.transaction_filters.type_filter import TypeFilter
from tests.models.test_assets.composites import (
    everything_except,
    transactions,
    type_filters,
)

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
    assert filter_.type_names == frozenset(type_names)
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
    assert filter_1.__eq__(filter_2) == (filter_1.__hash__() == filter_2.__hash__())


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
def test_filtering(transactions: list[Transaction], filter_: TypeFilter) -> None:
    filtered = filter_.filter_transactions(transactions)
    if filter_.mode == FilterMode.OFF:
        assert filtered == tuple(transactions)
    elif filter_.mode == FilterMode.KEEP:
        assert filtered == tuple(
            transaction
            for transaction in transactions
            if check_transaction(filter_, transaction)
        )
    else:
        assert filtered == tuple(
            transaction
            for transaction in transactions
            if not check_transaction(filter_, transaction)
        )
