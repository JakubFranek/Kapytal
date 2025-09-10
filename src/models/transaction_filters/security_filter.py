from collections.abc import Collection

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.security_objects import (
    Security,
    SecurityRelatedTransaction,
)
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)


class SecurityFilter(BaseTransactionFilter):
    """Filters Transactions based on whether they are related to specific Securities.
    Ignores Transactions without a Security."""

    __slots__ = ("_mode", "_securities")

    def __init__(self, securities: Collection[Security], mode: FilterMode) -> None:
        super().__init__(mode)
        if not all(isinstance(security, Security) for security in securities):
            raise TypeError(
                "Parameter 'securities' must be a Collection of Securities."
            )
        self._securities = frozenset(securities)

    @property
    def securities(self) -> frozenset[Security]:
        return self._securities

    @property
    def security_names(self) -> tuple[str, ...]:
        return tuple(sorted(security.name for security in self._securities))

    @property
    def members(self) -> tuple[frozenset[Security], FilterMode]:
        return (self._securities, self._mode)

    def __repr__(self) -> str:
        return (
            f"SecurityFilter(securities={self.security_names}, mode={self._mode.name})"
        )

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        if not isinstance(transaction, SecurityRelatedTransaction):
            return True
        return transaction.security in self._securities

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        if not isinstance(transaction, SecurityRelatedTransaction):
            return True
        return transaction.security not in self._securities
