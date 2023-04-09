from collections.abc import Collection

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    InvalidAttributeError,
)
from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)


class PayeeFilter(BaseTransactionFilter):
    """Filters transactions based on whether they have specific Payees.
    Ignores Payee-less transactions."""

    def __init__(self, payees: Collection[Attribute], mode: FilterMode) -> None:
        super().__init__(mode=mode)

        if any(not isinstance(payee, Attribute) for payee in payees):
            raise TypeError("Parameter 'payees' must be a collection of Attributes.")
        if any(tag.type_ != AttributeType.PAYEE for tag in payees):
            raise InvalidAttributeError(
                "Parameter 'payees' must contain only Attributes with type_=PAYEE."
            )
        self._payees = frozenset(payees)

    @property
    def payees(self) -> frozenset[Attribute]:
        return self._payees

    @property
    def payee_names(self) -> tuple[str]:
        return tuple(sorted(tag.name for tag in self._payees))

    @property
    def members(self) -> tuple[frozenset[Attribute], FilterMode]:
        return (self._payees, self._mode)

    def __repr__(self) -> str:
        return f"PayeeFilter(payees={self._payees}, mode={self._mode.name})"

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        if not isinstance(transaction, CashTransaction | RefundTransaction):
            return True
        return transaction.payee in self._payees

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        if not isinstance(transaction, CashTransaction | RefundTransaction):
            return True
        return transaction.payee not in self._payees
