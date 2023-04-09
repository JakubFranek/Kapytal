import logging
from collections.abc import Collection

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import (
    CashTransaction,
    CashTransactionType,
)
from src.models.model_objects.security_objects import (
    SecurityTransaction,
    SecurityTransactionType,
)
from src.models.transaction_filters.filter_mode_mixin import FilterMode, FilterModeMixin


class TypeFilter(FilterModeMixin):
    def __init__(
        self,
        types: Collection[
            type[Transaction] | CashTransactionType | SecurityTransactionType
        ],
        mode: FilterMode,
    ) -> None:
        super().__init__(mode=mode)
        for type_ in types:
            if isinstance(
                type_, type(Transaction) | CashTransactionType | SecurityTransactionType
            ):
                continue
            raise TypeError(
                "Parameter 'types' must be a collection of Transaction "
                "types, CashTransactionType or SecurityTransactionType."
            )
        self._types = frozenset(types)

    @property
    def types(
        self,
    ) -> frozenset[type[Transaction] | CashTransactionType | SecurityTransactionType]:
        return self._types

    @property
    def type_names(self) -> tuple[str]:
        type_names_ = []
        for type_ in self._types:
            if isinstance(type_, CashTransactionType | SecurityTransactionType):
                type_names_.append(type_.name)
            else:
                type_names_.append(type_.__name__)
        return tuple(sorted(type_names_))

    @property
    def transaction_types(self) -> tuple[type[Transaction], ...]:
        return tuple(
            type_ for type_ in self._types if isinstance(type_, type(Transaction))
        )

    @property
    def enum_types(self) -> tuple[CashTransactionType | SecurityTransactionType, ...]:
        return tuple(
            type_
            for type_ in self._types
            if isinstance(type_, CashTransactionType | SecurityTransactionType)
        )

    @property
    def members(
        self,
    ) -> tuple[
        frozenset[type[Transaction] | CashTransactionType | SecurityTransactionType],
        FilterMode,
    ]:
        return (self._types, self._mode)

    def __repr__(self) -> str:
        return f"TypeFilter(types={self.type_names}, mode={self._mode.name})"

    def __hash__(self) -> int:
        return hash(self.members)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, TypeFilter):
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
                if self._check_transaction(transaction)
            )
        else:
            output = tuple(
                transaction
                for transaction in transactions
                if not self._check_transaction(transaction)
            )
        if len(output) != input_len:
            logging.debug(
                f"TypeFilter: mode={self._mode.name}, removed={input_len - len(output)}"
            )
        return output

    def _check_transaction(self, transaction: Transaction) -> bool:
        if isinstance(transaction, CashTransaction | SecurityTransaction):
            return transaction.type_ in self.enum_types
        return isinstance(transaction, self.transaction_types)
