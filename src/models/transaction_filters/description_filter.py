import re

from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)


class DescriptionFilter(BaseTransactionFilter):
    __slots__ = ("_flags", "_mode", "_regex_pattern")

    def __init__(
        self, regex_pattern: str, mode: FilterMode, *, ignore_case: bool = True
    ) -> None:
        super().__init__(mode=mode)
        re.compile(regex_pattern)  # Raises re.error if pattern is invalid
        self._regex_pattern = regex_pattern
        self._flags = re.IGNORECASE if ignore_case else 0

    @property
    def regex_pattern(self) -> str:
        return self._regex_pattern

    @property
    def ignore_case(self) -> bool:
        return self._flags == re.IGNORECASE

    @property
    def members(self) -> tuple[str, re.RegexFlag | int, FilterMode]:
        return (self._regex_pattern, self._flags, self._mode)

    def __repr__(self) -> str:
        return (
            f"DescriptionFilter(pattern='{self._regex_pattern}', "
            f"ignore_case={self.ignore_case}, "
            f"mode={self._mode.name})"
        )

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        return bool(
            re.search(self._regex_pattern, transaction.description, flags=self._flags)
        )

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        return not self._keep_in_keep_mode(transaction)
