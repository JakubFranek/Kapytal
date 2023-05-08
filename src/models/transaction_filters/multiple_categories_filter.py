from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)


class MultipleCategoriesFilter(BaseTransactionFilter):
    """Filters CashTransactions which have multiple Categories.
    Ignores other Transactions."""

    def __init__(self, mode: FilterMode) -> None:
        super().__init__(mode=mode)

    def __repr__(self) -> str:
        return f"MultipleCategoriesFilter(mode={self._mode.name})"

    @property
    def members(self) -> tuple[FilterMode]:
        return (self._mode,)

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        return (
            isinstance(transaction, CashTransaction | RefundTransaction)
            and len(transaction.categories) > 1
        ) or not isinstance(transaction, CashTransaction | RefundTransaction)

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        return (
            isinstance(transaction, CashTransaction | RefundTransaction)
            and len(transaction.categories) == 1
        ) or not isinstance(transaction, CashTransaction | RefundTransaction)
