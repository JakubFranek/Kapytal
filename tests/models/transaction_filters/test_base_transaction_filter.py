from typing import Any

import pytest
from hypothesis import given
from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)
from tests.models.test_assets.composites import everything_except


class ConcreteTransactionFilter(BaseTransactionFilter):
    def __init__(self, mode: FilterMode, *args: Any, **kwargs: Any) -> None:
        super().__init__(mode, *args, **kwargs)

    @property
    def members(self) -> tuple[Any, ...]:
        return super().members

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        return super()._keep_in_keep_mode(transaction)

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        return super()._keep_in_discard_mode(transaction)


@given(mode=everything_except(FilterMode))
def test_invalid_mode_type(mode: Any) -> None:
    with pytest.raises(TypeError, match="Parameter 'mode' must be a FilterMode."):
        ConcreteTransactionFilter(mode)
