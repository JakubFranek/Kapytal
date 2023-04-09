from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)


class TaglessFilter(BaseTransactionFilter):
    """Filters Transactions which have no Tags.

    KEEP: Keeps only Tag-less Transactions.
    DISCARD: Discards Tag-less Transactions."""

    def __init__(self, mode: FilterMode) -> None:
        super().__init__(mode=mode)

    def __repr__(self) -> str:
        return f"TaglessFilter(mode={self._mode.name})"

    @property
    def members(self) -> tuple[FilterMode]:
        return (self._mode,)

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        return len(transaction.tags) == 0

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        return not self._keep_in_keep_mode(transaction)
