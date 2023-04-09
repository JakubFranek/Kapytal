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
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)


class TypeFilter(BaseTransactionFilter):
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

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        if isinstance(transaction, CashTransaction | SecurityTransaction):
            return transaction.type_ in self.enum_types
        return isinstance(transaction, self.transaction_types)

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        return not self._keep_in_keep_mode(transaction)
