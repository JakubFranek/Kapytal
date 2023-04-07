import re
from collections.abc import Collection
from datetime import datetime, time
from enum import Enum
from typing import Any

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import (
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.security_objects import (
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
)
from src.models.user_settings import user_settings


def set_minimum_time(datetime_: datetime) -> datetime:
    time_min = time.min
    return datetime_.replace(
        hour=time_min.hour,
        minute=time_min.minute,
        second=time_min.second,
        microsecond=time_min.microsecond,
    )


def set_maximum_time(datetime_: datetime) -> datetime:
    time_max = time.max
    return datetime_.replace(
        hour=time_max.hour,
        minute=time_max.minute,
        second=time_max.second,
        microsecond=time_max.microsecond,
    )


class FilterMode(Enum):
    OFF = "Keep all transactions (filter is disabled)"
    KEEP = "Keep transactions matching the filter criteria"
    DISCARD = "Discard transactions matching the filter criteria"


class FilterModeMixin:
    def __init__(
        self, mode: FilterMode, *args: Any, **kwargs: Any  # noqa: ANN401
    ) -> None:
        super().__init__(*args, **kwargs)
        if not isinstance(mode, FilterMode):
            raise TypeError("Parameter 'mode' must be a FilterMode.")
        self._mode = mode

    @property
    def mode(self) -> FilterMode:
        return self._mode


class TypeFilter(FilterModeMixin):
    def __init__(
        self,
        types: Collection[
            type[Transaction] | CashTransactionType | SecurityTransactionType
        ],
        mode: FilterMode,
    ) -> None:
        super().__init__(mode=mode)
        self._types = tuple(types)

    @property
    def types(
        self,
    ) -> tuple[type[Transaction] | CashTransactionType | SecurityTransactionType, ...]:
        return self._types

    @property
    def types_as_strings(self) -> tuple[str, ...]:
        types = []
        for type_ in self._types:
            if isinstance(type_, Enum):
                types.append(type_.name)
            else:
                types.append(type_.__name__)
        return tuple(types)

    @property
    def members(
        self,
    ) -> tuple[
        tuple[type[Transaction] | CashTransactionType | SecurityTransactionType, ...],
        FilterMode,
    ]:
        return (self._types, self._mode)

    def __repr__(self) -> str:
        return f"TypeFilter(types={self.types_as_strings}, mode={self._mode.name})"

    def __hash__(self) -> int:
        return hash(self.members)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, TypeFilter):
            return False
        return self.members == __o.members

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction]:
        if self.mode == FilterMode.OFF:
            return tuple(transactions)
        if self.mode == FilterMode.KEEP:
            return tuple(
                transaction
                for transaction in transactions
                if self._check_transaction(transaction)
            )
        if self.mode == FilterMode.DISCARD:
            return tuple(
                transaction
                for transaction in transactions
                if not self._check_transaction(transaction)
            )
        raise ValueError("Invalid FilterMode value.")

    def _check_transaction(self, transaction: Transaction) -> bool:
        if isinstance(transaction, CashTransaction | SecurityTransaction):
            return transaction.type_ in self._types
        return isinstance(transaction, self._types)


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
        if not isinstance(__o, DateTimeFilter):
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


class DescriptionFilter(FilterModeMixin):
    def __init__(self, regex_pattern: str, mode: FilterMode) -> None:
        super().__init__(mode=mode)
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
        if self._mode == FilterMode.KEEP:
            return tuple(
                transaction
                for transaction in transactions
                if re.search(self._regex_pattern, transaction.description)
            )
        if self._mode == FilterMode.DISCARD:
            return tuple(
                transaction
                for transaction in transactions
                if not re.search(self._regex_pattern, transaction.description)
            )
        raise ValueError("Invalid FilterMode value.")


class AccountFilter(FilterModeMixin):
    def __init__(self, accounts: Collection[Account], mode: FilterMode) -> None:
        super().__init__(mode=mode)
        self._accounts = tuple(accounts)

    @property
    def accounts(self) -> tuple[Account]:
        return self._accounts

    @property
    def members(self) -> tuple[tuple[Account], FilterMode]:
        return (self._accounts, self._mode)

    def __repr__(self) -> str:
        return f"AccountFilter(accounts={self._accounts}, mode={self._mode.name})"

    def __hash__(self) -> int:
        return hash(self.members)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, AccountFilter):
            return False
        return self.members == __o.members

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction]:
        if self._mode == FilterMode.OFF:
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
        self.restore_defaults()

    @property
    def type_filter(self) -> TypeFilter:
        return self._type_filter

    @property
    def datetime_filter(self) -> DateTimeFilter:
        return self._datetime_filter

    @property
    def description_filter(self) -> DescriptionFilter:
        return self._description_filter

    @property
    def account_filter(self) -> AccountFilter:
        return self._account_filter

    @property
    def members(
        self,
    ) -> tuple[TypeFilter, DateTimeFilter, DescriptionFilter, AccountFilter]:
        return (
            self._type_filter,
            self._datetime_filter,
            self._description_filter,
            self._account_filter,
        )

    def __repr__(self) -> str:
        return "TransactionFilter"

    def __hash__(self) -> int:
        return hash(self.members)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, TransactionFilter):
            return False
        return self.members == __o.members

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction]:
        _transactions = tuple(transactions)
        _transactions = self._type_filter.filter_transactions(_transactions)
        _transactions = self._datetime_filter.filter_transactions(_transactions)
        _transactions = self._description_filter.filter_transactions(_transactions)
        _transactions = self._account_filter.filter_transactions(_transactions)
        return tuple(_transactions)

    def restore_defaults(self) -> None:
        self._type_filter = TypeFilter(
            types=(
                CashTransactionType.INCOME,
                CashTransactionType.EXPENSE,
                RefundTransaction,
                CashTransfer,
                SecurityTransfer,
                SecurityTransactionType.BUY,
                SecurityTransactionType.SELL,
            ),
            mode=FilterMode.KEEP,
        )
        self._datetime_filter = DateTimeFilter(
            start=set_minimum_time(datetime.now(user_settings.settings.time_zone)),
            end=set_maximum_time(datetime.now(user_settings.settings.time_zone)),
            mode=FilterMode.OFF,
        )
        self._description_filter = DescriptionFilter(
            regex_pattern="", mode=FilterMode.OFF
        )
        self._account_filter = AccountFilter(accounts=(), mode=FilterMode.OFF)

    def set_type_filter(
        self, types: Collection[type[Transaction]], mode: FilterMode
    ) -> None:
        self._type_filter = TypeFilter(types, mode)

    def set_datetime_filter(
        self, start: datetime, end: datetime, mode: FilterMode
    ) -> None:
        self._datetime_filter = DateTimeFilter(start, end, mode)

    def set_account_filter(
        self, accounts: Collection[Account], mode: FilterMode
    ) -> None:
        self._account_filter = AccountFilter(accounts, mode)

    def set_description_filter(self, regex_pattern: str, mode: FilterMode) -> None:
        self._description_filter = DescriptionFilter(regex_pattern, mode)
