from typing import Any

import pytest
from hypothesis import given
from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)
from tests.models.test_assets.composites import everything_except, transactions


class ConcreteTransactionFilter(BaseTransactionFilter):
    def __init__(self, mode: FilterMode, *args: Any, **kwargs: Any) -> None:
        super().__init__(mode, *args, **kwargs)

    @property
    def members(self) -> tuple[Any, ...]:
        return super().members

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        del transaction
        return None

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        del transaction
        return False


@given(mode=everything_except(FilterMode))
def test_invalid_mode_type(mode: Any) -> None:
    with pytest.raises(TypeError, match="Parameter 'mode' must be a FilterMode."):
        ConcreteTransactionFilter(mode)


@given(transactions_=transactions())
def test_accept_transaction_off(transactions_: tuple[Transaction]) -> None:
    filter_ = ConcreteTransactionFilter(mode=FilterMode.OFF)
    for transaction in transactions_:
        assert filter_.accept_transaction(transaction) is True


@given(transactions_=transactions())
def test_accept_transaction_keep(transactions_: tuple[Transaction]) -> None:
    filter_ = ConcreteTransactionFilter(mode=FilterMode.KEEP)
    for transaction in transactions_:
        assert filter_.accept_transaction(transaction) is None


@given(transactions_=transactions())
def test_accept_transaction_discard(transactions_: tuple[Transaction]) -> None:
    filter_ = ConcreteTransactionFilter(mode=FilterMode.DISCARD)
    for transaction in transactions_:
        assert filter_.accept_transaction(transaction) is False
