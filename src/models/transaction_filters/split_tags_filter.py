from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import CashTransaction
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)


class SplitTagsFilter(BaseTransactionFilter):
    """Filters CashTransactions which have split Tags. Ignores other Transactions."""

    __slots__ = ("_mode",)

    def __init__(self, mode: FilterMode) -> None:
        super().__init__(mode=mode)

    def __repr__(self) -> str:
        return f"SplitTagsFilter(mode={self._mode.name})"

    @property
    def members(self) -> tuple[FilterMode]:
        return (self._mode,)

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        return (
            isinstance(transaction, CashTransaction) and transaction.are_tags_split
        ) or not isinstance(transaction, CashTransaction)

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        return (
            isinstance(transaction, CashTransaction) and not transaction.are_tags_split
        ) or not isinstance(transaction, CashTransaction)
