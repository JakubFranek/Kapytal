import logging
from collections.abc import Collection
from datetime import datetime, time

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import Attribute
from src.models.model_objects.cash_objects import (
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import Currency
from src.models.model_objects.security_objects import (
    Security,
    SecurityTransactionType,
    SecurityTransfer,
)
from src.models.transaction_filters.account_filter import AccountFilter
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.currency_filter import CurrencyFilter
from src.models.transaction_filters.datetime_filter import DatetimeFilter
from src.models.transaction_filters.description_filter import DescriptionFilter
from src.models.transaction_filters.payee_filter import PayeeFilter
from src.models.transaction_filters.security_filter import SecurityFilter
from src.models.transaction_filters.specific_tags_filter import SpecificTagsFilter
from src.models.transaction_filters.split_tags_filter import SplitTagsFilter
from src.models.transaction_filters.tagless_filter import TaglessFilter
from src.models.transaction_filters.type_filter import TypeFilter
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


class TransactionFilter:
    def __init__(self) -> None:
        self.restore_defaults()

    @property
    def type_filter(self) -> TypeFilter:
        return self._type_filter

    @property
    def datetime_filter(self) -> DatetimeFilter:
        return self._datetime_filter

    @property
    def description_filter(self) -> DescriptionFilter:
        return self._description_filter

    @property
    def account_filter(self) -> AccountFilter:
        return self._account_filter

    @property
    def specific_tags_filter(self) -> SpecificTagsFilter:
        return self._specific_tags_filter

    @property
    def tagless_filter(self) -> TaglessFilter:
        return self._tagless_filter

    @property
    def split_tags_filter(self) -> SplitTagsFilter:
        return self._split_tags_filter

    @property
    def payee_filter(self) -> PayeeFilter:
        return self._payee_filter

    @property
    def currency_filter(self) -> CurrencyFilter:
        return self._currency_filter

    @property
    def security_filter(self) -> SecurityFilter:
        return self._security_filter

    @property
    def members(
        self,
    ) -> tuple[TypeFilter, DatetimeFilter, DescriptionFilter, AccountFilter]:
        return (
            self._type_filter,
            self._datetime_filter,
            self._description_filter,
            self._account_filter,
            self._specific_tags_filter,
            self._tagless_filter,
            self._split_tags_filter,
            self._payee_filter,
            self._currency_filter,
            self._security_filter,
        )

    def __repr__(self) -> str:
        return "TransactionFilter"

    def __hash__(self) -> int:
        return hash(self.members)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, TransactionFilter):
            return False
        return self.members == __o.members

    def accept_transaction(self, transaction: Transaction) -> bool:
        return all(
            (
                self._type_filter.accept_transaction(transaction),
                self._datetime_filter.accept_transaction(transaction),
                self._description_filter.accept_transaction(transaction),
                self._account_filter.accept_transaction(transaction),
                self._currency_filter.accept_transaction(transaction),
                self._specific_tags_filter.accept_transaction(transaction),
                self._tagless_filter.accept_transaction(transaction),
                self._split_tags_filter.accept_transaction(transaction),
                self._payee_filter.accept_transaction(transaction),
                self._security_filter.accept_transaction(transaction),
            )
        )

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction, ...]:
        logging.debug(f"Filtering {len(transactions)} transactions")
        _transactions = tuple(transactions)
        _transactions = self._type_filter.filter_transactions(_transactions)
        _transactions = self._datetime_filter.filter_transactions(_transactions)
        _transactions = self._description_filter.filter_transactions(_transactions)
        _transactions = self._account_filter.filter_transactions(_transactions)
        _transactions = self._currency_filter.filter_transactions(_transactions)
        _transactions = self._specific_tags_filter.filter_transactions(_transactions)
        _transactions = self._tagless_filter.filter_transactions(_transactions)
        _transactions = self._split_tags_filter.filter_transactions(_transactions)
        _transactions = self._payee_filter.filter_transactions(_transactions)
        _transactions = self._security_filter.filter_transactions(_transactions)
        logging.debug(f"Kept {len(_transactions)}/{len(transactions)} transactions")
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
        self._datetime_filter = DatetimeFilter(
            start=set_minimum_time(datetime.now(user_settings.settings.time_zone)),
            end=set_maximum_time(datetime.now(user_settings.settings.time_zone)),
            mode=FilterMode.OFF,
        )
        self._description_filter = DescriptionFilter(
            regex_pattern="", mode=FilterMode.OFF
        )
        self._account_filter = AccountFilter(accounts=(), mode=FilterMode.OFF)
        self._specific_tags_filter = SpecificTagsFilter(tags=(), mode=FilterMode.OFF)
        self._tagless_filter = TaglessFilter(mode=FilterMode.OFF)
        self._split_tags_filter = SplitTagsFilter(mode=FilterMode.OFF)
        self._payee_filter = PayeeFilter(payees=(), mode=FilterMode.OFF)
        self._currency_filter = CurrencyFilter(currencies=(), mode=FilterMode.OFF)
        self._security_filter = SecurityFilter(securities=(), mode=FilterMode.OFF)

    def set_type_filter(
        self, types: Collection[type[Transaction]], mode: FilterMode
    ) -> None:
        self._type_filter = TypeFilter(types, mode)

    def set_datetime_filter(
        self, start: datetime, end: datetime, mode: FilterMode
    ) -> None:
        self._datetime_filter = DatetimeFilter(start, end, mode)

    def set_account_filter(
        self, accounts: Collection[Account], mode: FilterMode
    ) -> None:
        self._account_filter = AccountFilter(accounts, mode)

    def set_description_filter(self, regex_pattern: str, mode: FilterMode) -> None:
        self._description_filter = DescriptionFilter(regex_pattern, mode)

    def set_specific_tags_filter(
        self, tags: Collection[Attribute], mode: FilterMode
    ) -> None:
        self._specific_tags_filter = SpecificTagsFilter(tags, mode)

    def set_tagless_filter(self, mode: FilterMode) -> None:
        self._tagless_filter = TaglessFilter(mode)

    def set_split_tags_filter(self, mode: FilterMode) -> None:
        self._split_tags_filter = SplitTagsFilter(mode)

    def set_payee_filter(self, payees: Collection[Attribute], mode: FilterMode) -> None:
        self._payee_filter = PayeeFilter(payees, mode)

    def set_currency_filter(
        self, currencies: Collection[Currency], mode: FilterMode
    ) -> None:
        self._currency_filter = CurrencyFilter(currencies, mode)

    def set_security_filter(
        self, securities: Collection[Security], mode: FilterMode
    ) -> None:
        self._security_filter = SecurityFilter(securities, mode)
