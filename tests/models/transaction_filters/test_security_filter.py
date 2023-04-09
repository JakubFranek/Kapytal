from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.security_objects import (
    Security,
    SecurityRelatedTransaction,
)
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.security_filter import SecurityFilter
from tests.models.test_assets.composites import (
    everything_except,
    securities,
    security_filters,
    transactions,
)
from tests.models.test_assets.transaction_list import transaction_list


def check_transaction(filter_: SecurityFilter, transaction: Transaction) -> bool:
    if filter_.mode == FilterMode.OFF:
        return True
    if not isinstance(transaction, SecurityRelatedTransaction):
        return True
    if filter_.mode == FilterMode.KEEP:
        return transaction.security in filter_.securities
    return transaction.security not in filter_.securities


@given(securities=st.lists(securities()), mode=st.sampled_from(FilterMode))
def test_creation(securities: list[Security], mode: FilterMode) -> None:
    filter_ = SecurityFilter(securities, mode)
    assert filter_.securities == frozenset(securities)
    assert filter_.security_names == tuple(
        sorted(security.name for security in securities)
    )
    assert filter_.mode == mode
    assert (
        filter_.__repr__()
        == f"SecurityFilter(securities={filter_.security_names}, mode={mode.name})"
    )


@given(
    securities=st.lists(everything_except(Security), min_size=1, max_size=10),
    mode=st.sampled_from(FilterMode),
)
def test_creation_invalid_type(securities: list[Any], mode: FilterMode) -> None:
    with pytest.raises(TypeError, match="must be a Collection of Securities"):
        SecurityFilter(securities, mode)


@given(filter_1=security_filters(), filter_2=security_filters())
def test_eq_hash(filter_1: SecurityFilter, filter_2: SecurityFilter) -> None:
    assert filter_1.__eq__(filter_2) == (
        filter_1.__hash__() == filter_2.__hash__()
    ) or (filter_1.mode == FilterMode.OFF and filter_2.mode == FilterMode.OFF)


@given(filter_1=security_filters(), filter_2=everything_except(SecurityFilter))
def test_eq_different_type(filter_1: SecurityFilter, filter_2: Any) -> None:
    assert filter_1.__eq__(filter_2) is False


@given(transactions=transactions(), filter_=security_filters())
def test_filter_off(transactions: list[Transaction], filter_: SecurityFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(transactions)


@given(transactions=transactions(), filter_=security_filters())
def test_filter_keep(transactions: list[Transaction], filter_: SecurityFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(transactions=transactions(), filter_=security_filters())
def test_filter_discard(
    transactions: list[Transaction], filter_: SecurityFilter
) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(filter_=security_filters())
def test_filter_off_premade_transactions(filter_: SecurityFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


@given(filter_=security_filters())
def test_filter_keep_premade_transactions(filter_: SecurityFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )


@given(filter_=security_filters())
def test_filter_discard_premade_transactions(filter_: SecurityFilter) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )
