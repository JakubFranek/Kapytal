from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.account_filter import AccountFilter
from src.models.transaction_filters.filter_mode_mixin import FilterMode
from tests.models.test_assets.composites import (
    account_filters,
    cash_accounts,
    everything_except,
    security_accounts,
    transactions,
)
from tests.models.test_assets.transaction_list import transaction_list


def check_transaction(filter_: AccountFilter, transaction: Transaction) -> bool:
    if filter_.mode == FilterMode.OFF:
        return True
    return transaction.is_accounts_related(filter_.accounts)


@given(
    accounts=st.lists(
        st.one_of(cash_accounts(), security_accounts()), min_size=0, max_size=10
    ),
    mode=st.sampled_from(FilterMode),
)
def test_creation(accounts: list[Account], mode: FilterMode) -> None:
    filter_ = AccountFilter(accounts, mode)
    assert filter_.accounts == tuple(accounts)
    assert filter_.mode == mode
    assert (
        filter_.__repr__()
        == f"AccountFilter(accounts={tuple(accounts)}, mode={mode.name})"
    )


@given(
    accounts=st.lists(everything_except(Account), min_size=1, max_size=10),
    mode=st.sampled_from(FilterMode),
)
def test_creation_invalid_type(accounts: list[Account], mode: FilterMode) -> None:
    with pytest.raises(TypeError, match="must be a collection of Accounts"):
        AccountFilter(accounts, mode)


@given(filter_1=account_filters(), filter_2=account_filters())
def test_eq_hash(filter_1: AccountFilter, filter_2: AccountFilter) -> None:
    assert filter_1.__eq__(filter_2) == (filter_1.__hash__() == filter_2.__hash__())


@given(filter_1=account_filters(), filter_2=everything_except(AccountFilter))
def test_eq_different_type(filter_1: AccountFilter, filter_2: Any) -> None:
    assert filter_1.__eq__(filter_2) is False


@given(transactions=transactions(), filter_=account_filters())
def test_filter_off(transactions: list[Transaction], filter_: AccountFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(transactions)


@given(transactions=transactions(), filter_=account_filters())
def test_filter_keep(transactions: list[Transaction], filter_: AccountFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(transactions=transactions(), filter_=account_filters())
def test_filter_discard(
    transactions: list[Transaction], filter_: AccountFilter
) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if not check_transaction(filter_, transaction)
    )


@given(filter_=account_filters())
def test_filter_off_premade_transactions(filter_: AccountFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


@given(filter_=account_filters())
def test_filter_keep_premade_transactions(filter_: AccountFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )


@given(filter_=account_filters())
def test_filter_discard_premade_transactions(filter_: AccountFilter) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if not check_transaction(filter_, transaction)
    )
