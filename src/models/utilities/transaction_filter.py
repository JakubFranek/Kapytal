import re
from collections.abc import Collection
from datetime import datetime
from enum import Enum
from typing import Any

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction


class FilterMode(Enum):
    KEEP = "Keep values matching the filter criteria"
    DISCARD = "Discard values matching the filter criteria"
    ALL = "Keep all values (filter is disabled)"


class FilterModeMixin:
    def __init__(
        self, mode: FilterMode, *args: Any, **kwargs: Any  # noqa: ANN401
    ) -> None:
        super().__init__(*args, **kwargs)
        self._mode = mode

    @property
    def mode(self) -> FilterMode:
        return self._mode

    @mode.setter
    def mode(self, mode: FilterMode) -> None:
        if not isinstance(mode, FilterMode):
            raise TypeError("Parameter 'mode' must be a FilterMode.")
        self._mode = mode


class TypeFilter(FilterModeMixin):
    def __init__(self, types: Collection[type[Transaction]], mode: FilterMode) -> None:
        super().__init__(mode=mode)
        self._types = tuple(types)

    def __repr__(self) -> str:
        return f"TypeFilter(types={self._types}, mode={self._mode.name})"

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction]:
        if self.mode == FilterMode.ALL:
            return tuple(transactions)
        if self.mode == FilterMode.KEEP:
            return tuple(
                transaction
                for transaction in transactions
                if isinstance(transaction, self._types)
            )
        if self.mode == FilterMode.DISCARD:
            return tuple(
                transaction
                for transaction in transactions
                if not isinstance(transaction, self._types)
            )
        raise ValueError("Invalid FilterMode value.")


class DateTimeFilter(FilterModeMixin):
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
        self._mode = mode

    def __repr__(self) -> str:
        return (
            f"DateTimeFilter(start={self._start.strftime('%Y-%m-%d %H:%M:%S')}, "
            f"end={self._end.strftime('%Y-%m-%d %H:%M:%S')}, mode={self._mode.name})"
        )

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction]:
        if self._mode == FilterMode.ALL:
            return tuple(transactions)

        filtered_transactions = []
        for transaction in transactions:
            if self._start <= transaction.datetime_ <= self._end:
                if self._mode == FilterMode.KEEP:
                    filtered_transactions.append(transaction)
            elif self._mode == FilterMode.DISCARD:
                filtered_transactions.append(transaction)

        return tuple(filtered_transactions)


class DescriptionFilter(FilterModeMixin):
    def __init__(self, regex_pattern: str, mode: FilterMode) -> None:
        super().__init__(mode=mode)
        self._pattern = regex_pattern

    def __repr__(self) -> str:
        return f"DescriptionFilter(pattern={self._pattern}, mode={self._mode.name})"

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction]:
        if self._mode == FilterMode.ALL:
            return tuple(transactions)
        if self._mode == FilterMode.KEEP:
            return tuple(
                transaction
                for transaction in transactions
                if re.search(self._pattern, transaction.description)
            )
        if self._mode == FilterMode.DISCARD:
            return tuple(
                transaction
                for transaction in transactions
                if not re.search(self._pattern, transaction.description)
            )
        raise ValueError("Invalid FilterMode value.")


class AccountFilter(FilterModeMixin):
    def __init__(self, accounts: Collection[Account], mode: FilterMode) -> None:
        super().__init__(mode=mode)
        self._accounts = tuple(accounts)

    def __repr__(self) -> str:
        return f"AccountFilter(accounts={self._accounts}, mode={self._mode.name})"

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction]:
        if self._mode == FilterMode.ALL:
            return tuple(transactions)
        if self._mode == FilterMode.KEEP:
            return tuple(
                transaction
                for transaction in transactions
                if transaction.is_accounts_related(self._accounts)
            )
        if self._mode == FilterMode.DISCARD:
            return tuple(
                transaction
                for transaction in transactions
                if not transaction.is_accounts_related(self._accounts)
            )
        raise ValueError("Invalid FilterMode value.")


class TransactionFilter:
    def __init__(self) -> None:
        pass

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction]:
        _transactions = tuple(transactions)
        _transactions = self._type_filter.filter_transactions(_transactions)
        _transactions = self._datetime_filter.filter_transactions(_transactions)
        _transactions = self._accounts_filter.filter_transactions(_transactions)
        _transactions = self._description_filter.filter_transactions(_transactions)
        return tuple(_transactions)

    def set_type_filter(
        self, types: Collection[type[Transaction]], mode: FilterMode
    ) -> None:
        self._type_filter = TypeFilter(types, mode)

    def set_datetime_filter(
        self, start: datetime, end: datetime, mode: FilterMode
    ) -> None:
        self._datetime_filter = DateTimeFilter(start, end, mode)

    def set_accounts_filter(
        self, accounts: Collection[Account], mode: FilterMode
    ) -> None:
        self._accounts_filter = AccountFilter(accounts, mode)

    def set_description_filter(self, regex_pattern: str, mode: FilterMode) -> None:
        self._description_filter = DescriptionFilter(regex_pattern, mode)
