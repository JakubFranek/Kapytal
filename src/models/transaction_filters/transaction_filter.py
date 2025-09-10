import logging
from collections.abc import Collection
from datetime import datetime, time
from uuid import UUID

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.mixins.copyable_mixin import CopyableMixin
from src.models.model_objects.attributes import Attribute, Category
from src.models.model_objects.cash_objects import (
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import CashAmount, Currency
from src.models.model_objects.security_objects import (
    Security,
    SecurityTransactionType,
    SecurityTransfer,
)
from src.models.transaction_filters.account_filter import AccountFilter
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)
from src.models.transaction_filters.cash_amount_filter import CashAmountFilter
from src.models.transaction_filters.currency_filter import CurrencyFilter
from src.models.transaction_filters.datetime_filter import DatetimeFilter
from src.models.transaction_filters.description_filter import DescriptionFilter
from src.models.transaction_filters.multiple_categories_filter import (
    MultipleCategoriesFilter,
)
from src.models.transaction_filters.payee_filter import PayeeFilter
from src.models.transaction_filters.security_filter import SecurityFilter
from src.models.transaction_filters.specific_categories_filter import (
    SpecificCategoriesFilter,
)
from src.models.transaction_filters.specific_tags_filter import SpecificTagsFilter
from src.models.transaction_filters.split_tags_filter import SplitTagsFilter
from src.models.transaction_filters.tagless_filter import TaglessFilter
from src.models.transaction_filters.type_filter import TypeFilter
from src.models.transaction_filters.uuid_filter import UUIDFilter
from src.models.user_settings import user_settings

all_transaction_types = frozenset(
    (
        CashTransactionType.INCOME,
        CashTransactionType.EXPENSE,
        RefundTransaction,
        CashTransfer,
        SecurityTransfer,
        SecurityTransactionType.BUY,
        SecurityTransactionType.SELL,
        SecurityTransactionType.DIVIDEND,
    )
)


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


class TransactionFilter(CopyableMixin):
    __slots__ = (
        "_account_filter",
        "_all_pass",
        "_cash_amount_filter",
        "_currency_filter",
        "_datetime_filter",
        "_description_filter",
        "_multiple_categories_filter",
        "_payee_filter",
        "_security_filter",
        "_specific_categories_filter",
        "_specific_tags_filter",
        "_split_tags_filter",
        "_tagless_filter",
        "_type_filter",
        "_uuid_filter",
    )

    def __init__(self) -> None:
        self.restore_defaults()

    @property
    def uuid_filter(self) -> UUIDFilter:
        return self._uuid_filter

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
    def specific_categories_filter(self) -> SpecificCategoriesFilter:
        return self._specific_categories_filter

    @property
    def multiple_categories_filter(self) -> MultipleCategoriesFilter:
        return self._multiple_categories_filter

    @property
    def currency_filter(self) -> CurrencyFilter:
        return self._currency_filter

    @property
    def security_filter(self) -> SecurityFilter:
        return self._security_filter

    @property
    def cash_amount_filter(self) -> CashAmountFilter:
        return self._cash_amount_filter

    @property
    def members(
        self,
    ) -> tuple[BaseTransactionFilter, ...]:
        return (
            self._uuid_filter,
            self._type_filter,
            self._datetime_filter,
            self._description_filter,
            self._account_filter,
            self._specific_tags_filter,
            self._tagless_filter,
            self._split_tags_filter,
            self._payee_filter,
            self._specific_categories_filter,
            self._multiple_categories_filter,
            self._currency_filter,
            self._security_filter,
            self._cash_amount_filter,
        )

    def __repr__(self) -> str:
        return "TransactionFilter"

    def __hash__(self) -> int:
        return hash(self.members)

    def __eq__(self, /, __o: object) -> bool:
        if not isinstance(__o, TransactionFilter):
            return NotImplemented
        return self.members == __o.members

    def validate_transaction(self, transaction: Transaction) -> bool:
        if self._all_pass:
            return True
        return all(
            (
                self._uuid_filter.validate_transaction(transaction),
                self._type_filter.validate_transaction(transaction),
                self._datetime_filter.validate_transaction(transaction),
                self._description_filter.validate_transaction(transaction),
                self._account_filter.validate_transaction(transaction),
                self._currency_filter.validate_transaction(transaction),
                self._specific_tags_filter.validate_transaction(transaction),
                self._tagless_filter.validate_transaction(transaction),
                self._split_tags_filter.validate_transaction(transaction),
                self._payee_filter.validate_transaction(transaction),
                self._specific_categories_filter.validate_transaction(transaction),
                self._multiple_categories_filter.validate_transaction(transaction),
                self._security_filter.validate_transaction(transaction),
                self._cash_amount_filter.validate_transaction(transaction),
            )
        )

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction, ...]:
        if self._all_pass:
            return tuple(transactions)

        _transactions = tuple(transactions)
        _transactions = self._uuid_filter.filter_transactions(_transactions)
        _transactions = self._type_filter.filter_transactions(_transactions)
        _transactions = self._datetime_filter.filter_transactions(_transactions)
        _transactions = self._description_filter.filter_transactions(_transactions)
        _transactions = self._account_filter.filter_transactions(_transactions)
        _transactions = self._currency_filter.filter_transactions(_transactions)
        _transactions = self._specific_tags_filter.filter_transactions(_transactions)
        _transactions = self._tagless_filter.filter_transactions(_transactions)
        _transactions = self._split_tags_filter.filter_transactions(_transactions)
        _transactions = self._payee_filter.filter_transactions(_transactions)
        _transactions = self._specific_categories_filter.filter_transactions(
            _transactions
        )
        _transactions = self._multiple_categories_filter.filter_transactions(
            _transactions
        )
        _transactions = self._security_filter.filter_transactions(_transactions)
        _transactions = self._cash_amount_filter.filter_transactions(_transactions)
        logging.debug(f"Kept {len(_transactions)} / {len(transactions)} transactions")
        return _transactions

    def restore_defaults(self) -> None:
        self._uuid_filter = UUIDFilter(uuids=(), mode=FilterMode.OFF)
        self._type_filter = TypeFilter(
            types=all_transaction_types, mode=FilterMode.KEEP
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
        self._specific_categories_filter = SpecificCategoriesFilter(
            categories=(), mode=FilterMode.OFF
        )
        self._multiple_categories_filter = MultipleCategoriesFilter(mode=FilterMode.OFF)
        self._currency_filter = CurrencyFilter(currencies=(), mode=FilterMode.OFF)
        self._security_filter = SecurityFilter(securities=(), mode=FilterMode.OFF)
        self._cash_amount_filter = CashAmountFilter(None, None, FilterMode.OFF)

        self._calculate_all_pass_attribute()

    def set_uuid_filter(self, uuids: Collection[UUID], mode: FilterMode) -> None:
        self._uuid_filter = UUIDFilter(uuids, mode)
        self._calculate_all_pass_attribute()

    def set_type_filter(
        self,
        types: Collection[
            type[Transaction] | CashTransactionType | SecurityTransactionType
        ],
        mode: FilterMode,
    ) -> None:
        self._type_filter = TypeFilter(types, mode)
        self._calculate_all_pass_attribute()

    def set_datetime_filter(
        self, start: datetime, end: datetime, mode: FilterMode
    ) -> None:
        self._datetime_filter = DatetimeFilter(start, end, mode)
        self._calculate_all_pass_attribute()

    def set_account_filter(
        self, accounts: Collection[Account], mode: FilterMode
    ) -> None:
        self._account_filter = AccountFilter(accounts, mode)
        self._calculate_all_pass_attribute()

    def set_description_filter(
        self, regex_pattern: str, mode: FilterMode, *, ignore_case: bool
    ) -> None:
        self._description_filter = DescriptionFilter(
            regex_pattern, mode, ignore_case=ignore_case
        )
        self._calculate_all_pass_attribute()

    def set_specific_tags_filter(
        self, tags: Collection[Attribute], mode: FilterMode
    ) -> None:
        self._specific_tags_filter = SpecificTagsFilter(tags, mode)
        self._calculate_all_pass_attribute()

    def set_tagless_filter(self, mode: FilterMode) -> None:
        self._tagless_filter = TaglessFilter(mode)
        self._calculate_all_pass_attribute()

    def set_split_tags_filter(self, mode: FilterMode) -> None:
        self._split_tags_filter = SplitTagsFilter(mode)
        self._calculate_all_pass_attribute()

    def set_payee_filter(self, payees: Collection[Attribute], mode: FilterMode) -> None:
        self._payee_filter = PayeeFilter(payees, mode)
        self._calculate_all_pass_attribute()

    def set_specific_categories_filter(
        self, categories: Collection[Category], mode: FilterMode
    ) -> None:
        self._specific_categories_filter = SpecificCategoriesFilter(categories, mode)
        self._calculate_all_pass_attribute()

    def set_multiple_categories_filter(self, mode: FilterMode) -> None:
        self._multiple_categories_filter = MultipleCategoriesFilter(mode)
        self._calculate_all_pass_attribute()

    def set_currency_filter(
        self, currencies: Collection[Currency], mode: FilterMode
    ) -> None:
        self._currency_filter = CurrencyFilter(currencies, mode)
        self._calculate_all_pass_attribute()

    def set_security_filter(
        self, securities: Collection[Security], mode: FilterMode
    ) -> None:
        self._security_filter = SecurityFilter(securities, mode)
        self._calculate_all_pass_attribute()

    def set_cash_amount_filter(
        self, minimum: CashAmount | None, maximum: CashAmount | None, mode: FilterMode
    ) -> None:
        self._cash_amount_filter = CashAmountFilter(minimum, maximum, mode)
        self._calculate_all_pass_attribute()

    def _calculate_all_pass_attribute(self) -> None:
        self._all_pass = all(filter_.is_all_pass for filter_ in self.members)
