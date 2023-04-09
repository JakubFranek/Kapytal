import logging
from collections.abc import Collection

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import CashTransaction
from src.models.transaction_filters.filter_mode_mixin import FilterMode, FilterModeMixin


class SplitTagsFilter(FilterModeMixin):
    """Filters CashTransactions which have split Tags. Ignores other Transactions."""

    def __init__(self, mode: FilterMode) -> None:
        super().__init__(mode=mode)

    def __repr__(self) -> str:
        return f"SplitTagsFilter(mode={self._mode.name})"

    def __hash__(self) -> int:
        return hash(self._mode)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, SplitTagsFilter):
            return False
        return self.mode == __o.mode

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
                if (
                    isinstance(transaction, CashTransaction)
                    and transaction.are_tags_split
                )
                or not isinstance(transaction, CashTransaction)
            )
        else:
            output = tuple(
                transaction
                for transaction in transactions
                if (
                    isinstance(transaction, CashTransaction)
                    and not transaction.are_tags_split
                )
                or not isinstance(transaction, CashTransaction)
            )
        if len(output) != input_len:
            logging.debug(
                f"SplitTagsFilter: mode={self._mode.name}, "
                f"removed={input_len - len(output)}"
            )
        return output
