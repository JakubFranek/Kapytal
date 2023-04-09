from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    InvalidAttributeError,
)
from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.payee_filter import PayeeFilter
from tests.models.test_assets.composites import (
    attributes,
    everything_except,
    payee_filters,
    transactions,
)
from tests.models.test_assets.transaction_list import transaction_list


def check_transaction(filter_: PayeeFilter, transaction: Transaction) -> bool:
    if filter_.mode == FilterMode.OFF:
        return True
    if not isinstance(transaction, CashTransaction | RefundTransaction):
        return True
    if filter_.mode == FilterMode.KEEP:
        return transaction.payee in filter_.payees
    return transaction.payee not in filter_.payees


@given(
    payees=st.lists(attributes(AttributeType.PAYEE)), mode=st.sampled_from(FilterMode)
)
def test_creation(payees: list[Attribute], mode: FilterMode) -> None:
    filter_ = PayeeFilter(payees, mode)
    assert filter_.payees == frozenset(payees)
    assert filter_.payee_names == tuple(sorted(payee.name for payee in payees))
    assert filter_.mode == mode
    assert (
        filter_.__repr__()
        == f"PayeeFilter(payees={frozenset(payees)}, mode={mode.name})"
    )


@given(
    payees=st.lists(everything_except(Attribute), min_size=1, max_size=10),
    mode=st.sampled_from(FilterMode),
)
def test_creation_invalid_type(payees: list[Any], mode: FilterMode) -> None:
    with pytest.raises(TypeError, match="must be a collection of Attributes"):
        PayeeFilter(payees, mode)


@given(
    payees=st.lists(attributes(AttributeType.TAG), min_size=1, max_size=10),
    mode=st.sampled_from(FilterMode),
)
def test_creation_invalid_attribute_type(
    payees: list[Attribute], mode: FilterMode
) -> None:
    with pytest.raises(InvalidAttributeError, match="only Attributes with type_=PAYEE"):
        PayeeFilter(payees, mode)


@given(filter_1=payee_filters(), filter_2=payee_filters())
def test_eq_hash(filter_1: PayeeFilter, filter_2: PayeeFilter) -> None:
    assert filter_1.__eq__(filter_2) == (
        filter_1.__hash__() == filter_2.__hash__()
    ) or (filter_1.mode == FilterMode.OFF and filter_2.mode == FilterMode.OFF)


@given(filter_1=payee_filters(), filter_2=everything_except(PayeeFilter))
def test_eq_different_type(filter_1: PayeeFilter, filter_2: Any) -> None:
    assert filter_1.__eq__(filter_2) is False


@given(transactions=transactions(), filter_=payee_filters())
def test_filter_off(transactions: list[Transaction], filter_: PayeeFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(transactions)


@given(transactions=transactions(), filter_=payee_filters())
def test_filter_keep(transactions: list[Transaction], filter_: PayeeFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(transactions=transactions(), filter_=payee_filters())
def test_filter_discard(transactions: list[Transaction], filter_: PayeeFilter) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(filter_=payee_filters())
def test_filter_off_premade_transactions(filter_: PayeeFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


@given(filter_=payee_filters())
def test_filter_keep_premade_transactions(filter_: PayeeFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )


@given(filter_=payee_filters())
def test_filter_discard_premade_transactions(filter_: PayeeFilter) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )
