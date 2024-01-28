from collections.abc import Collection

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
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)

TYPE_NAME_DICT = {
    CashTransactionType.INCOME: "Income",
    CashTransactionType.EXPENSE: "Expense",
    RefundTransaction: "Refund",
    CashTransfer: "Cash Transfer",
    SecurityTransactionType.BUY: "Buy",
    SecurityTransactionType.SELL: "Sell",
    SecurityTransactionType.DIVIDEND: "Dividend",
    SecurityTransfer: "Security Transfer",
}
all_types = frozenset(TYPE_NAME_DICT.keys())


class TypeFilter(BaseTransactionFilter):
    __slots__ = ("_types", "_mode", "_enum_types", "_transaction_types", "_type_names")

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
                "Parameter 'types' must be a Collection of Transaction "
                "types, CashTransactionType or SecurityTransactionType."
            )
        self._types = frozenset(types)
        self._enum_types = frozenset(
            type_
            for type_ in self._types
            if isinstance(type_, CashTransactionType | SecurityTransactionType)
        )
        self._transaction_types = tuple(
            type_ for type_ in self._types if isinstance(type_, type(Transaction))
        )
        self._type_names = tuple(TYPE_NAME_DICT[type_] for type_ in self._types)

    @property
    def types(
        self,
    ) -> frozenset[type[Transaction] | CashTransactionType | SecurityTransactionType]:
        return self._types

    @property
    def type_names(self) -> tuple[str]:
        return self._type_names

    @property
    def transaction_types(self) -> frozenset[type[Transaction]]:
        return frozenset(self._transaction_types)

    @property
    def enum_types(
        self,
    ) -> frozenset[CashTransactionType | SecurityTransactionType]:
        return self._enum_types

    @property
    def members(
        self,
    ) -> tuple[
        frozenset[type[Transaction] | CashTransactionType | SecurityTransactionType],
        FilterMode,
    ]:
        return (self._types, self._mode)

    @property
    def is_all_pass(self) -> bool:
        return self._mode == FilterMode.OFF or self._types == all_types

    def __repr__(self) -> str:
        return f"TypeFilter(types={self.type_names}, mode={self._mode.name})"

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        if self._types == all_types:
            return True
        if isinstance(transaction, CashTransaction | SecurityTransaction):
            return transaction.type_ in self._enum_types
        return isinstance(transaction, self._transaction_types)

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        if self._types == all_types:
            return False
        return not self._keep_in_keep_mode(transaction)
