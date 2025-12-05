from datetime import datetime

from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)


class DatetimeFilter(BaseTransactionFilter):
    __slots__ = ("_end", "_mode", "_start")

    def __init__(self, start: datetime, end: datetime, mode: FilterMode) -> None:
        super().__init__(mode=mode)
        if not isinstance(start, datetime):
            raise TypeError("Parameter 'start' must be a datetime.")
        if not isinstance(end, datetime):
            raise TypeError("Parameter 'end' must be a datetime.")

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
            f"DatetimeFilter(start={self._start.strftime('%Y-%m-%d %H:%M:%S')}, "
            f"end={self._end.strftime('%Y-%m-%d %H:%M:%S')}, mode={self._mode.name})"
        )

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        # Following line produces TypeError if one of the datetimes is offset-naive
        return self._start <= transaction.datetime_ <= self._end

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        return not self._keep_in_keep_mode(transaction)
