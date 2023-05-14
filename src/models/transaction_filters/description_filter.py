import re

from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)


class DescriptionFilter(BaseTransactionFilter):
    def __init__(self, regex_pattern: str, mode: FilterMode) -> None:
        super().__init__(mode=mode)
        re.compile(regex_pattern)  # Raises re.error if pattern is invalid
        self._regex_pattern = regex_pattern

    @property
    def regex_pattern(self) -> str:
        return self._regex_pattern

    @property
    def members(self) -> tuple[str, FilterMode]:
        return (self._regex_pattern, self._mode)

    def __repr__(self) -> str:
        return (
            f"DescriptionFilter(pattern='{self._regex_pattern}', "
            f"mode={self._mode.name})"
        )

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        return re.search(self._regex_pattern, transaction.description, re.IGNORECASE)

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        return not self._keep_in_keep_mode(transaction)
