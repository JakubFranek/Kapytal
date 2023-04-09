import logging
import re
from collections.abc import Collection

from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.filter_mode_mixin import FilterMode, FilterModeMixin


class DescriptionFilter(FilterModeMixin):
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

    def __hash__(self) -> int:
        return hash(self.members)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, DescriptionFilter):
            return False
        return self.members == __o.members

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction]:
        if self._mode == FilterMode.OFF:
            return tuple(transactions)

        input_len = len(transactions)
        if self._mode == FilterMode.KEEP:
            output = tuple(
                transaction
                for transaction in transactions
                if re.search(self._regex_pattern, transaction.description)
            )
        else:
            output = tuple(
                transaction
                for transaction in transactions
                if not re.search(self._regex_pattern, transaction.description)
            )
        if len(output) != input_len:
            logging.debug(
                f"DescriptionFilter: mode={self._mode.name}, "
                f"removed={input_len - len(output)}"
            )
        return output
