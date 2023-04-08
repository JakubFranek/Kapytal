from collections.abc import Collection
from datetime import datetime

from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.filter_mode_mixin import FilterMode, FilterModeMixin


class DatetimeFilter(FilterModeMixin):
    def __init__(self, start: datetime, end: datetime, mode: FilterMode) -> None:
        super().__init__(mode=mode)
        if not isinstance(start, datetime):
            raise TypeError("Parameter 'start' must be a datetime.")
        if not isinstance(end, datetime):
            raise TypeError("Parameter 'end' must be a datetime.")
        if not isinstance(mode, FilterMode):
            raise TypeError("Parameter 'mode' must be a FilterMode.")

        if start > end:
            raise ValueError(
                "Parameter 'start' must be an earlier datetime than parameter 'end'."
            )

        self._start = start
        self._end = end

    @property
    def start(self) -> datetime:
        return self._start

    @property
    def end(self) -> datetime:
        return self._end

    @property
    def members(self) -> tuple[datetime, datetime, FilterMode]:
        return (self._start, self._end, self._mode)

    def __repr__(self) -> str:
        return (
            f"DateTimeFilter(start={self._start.strftime('%Y-%m-%d %H:%M:%S')}, "
            f"end={self._end.strftime('%Y-%m-%d %H:%M:%S')}, mode={self._mode.name})"
        )

    def __hash__(self) -> int:
        return hash(self.members)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, DatetimeFilter):
            return False
        return self.members == __o.members

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction]:
        if self._mode == FilterMode.OFF:
            return tuple(transactions)

        filtered_transactions = []
        for transaction in transactions:
            if self._start <= transaction.datetime_ <= self._end:
                if self._mode == FilterMode.KEEP:
                    filtered_transactions.append(transaction)
            elif self._mode == FilterMode.DISCARD:
                filtered_transactions.append(transaction)

        return tuple(filtered_transactions)
