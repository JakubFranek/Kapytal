from collections.abc import Collection

from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.filter_mode_mixin import FilterMode, FilterModeMixin


class TaglessFilter(FilterModeMixin):
    def __init__(self, mode: FilterMode) -> None:
        super().__init__(mode=mode)

    def __repr__(self) -> str:
        return f"TaglessFilter(mode={self._mode.name})"

    def __hash__(self) -> int:
        return hash(self._mode)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, TaglessFilter):
            return False
        return self.mode == __o.mode

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction]:
        if self._mode == FilterMode.OFF:
            return tuple(transactions)
        if self._mode == FilterMode.KEEP:
            return tuple(
                transaction
                for transaction in transactions
                if len(transaction.tags) == 0
            )
        if self._mode == FilterMode.DISCARD:
            return tuple(
                transaction for transaction in transactions if len(transaction.tags) > 0
            )
        raise ValueError("Invalid FilterMode value.")  # pragma: no cover
