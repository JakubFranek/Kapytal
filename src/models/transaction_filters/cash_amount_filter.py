from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import (
    CashRelatedTransaction,
    CashTransaction,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import (
    CashAmount,
    ConversionFactorNotFoundError,
    CurrencyError,
)
from src.models.model_objects.security_objects import SecurityTransaction
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)


class CashAmountFilter(BaseTransactionFilter):
    """Filters CashRelatedTransactions based on CashAmounts.

    For CashTransfers, if either amount_sent or amount_received is within (KEEP)
    or outside the range (DISCARD), the CashTransfer is accepted.

    If no path to the currency of the CashAmountFilter is found, the filter accepts
    CashRelatedTransactions by default."""

    def __init__(
        self, minimum: CashAmount, maximum: CashAmount, mode: FilterMode
    ) -> None:
        super().__init__(mode)

        if not isinstance(minimum, CashAmount):
            raise TypeError("Parameter 'minimum' must be a CashAmount.")
        if not isinstance(maximum, CashAmount):
            raise TypeError("Parameter 'maximum' must be a CashAmount.")

        if minimum.currency != maximum.currency:
            raise CurrencyError(
                "Parameters 'minimum' and 'maximum' must have the same currency."
            )

        if minimum > maximum:
            raise ValueError(
                "Parameter 'minimum' must be less than or equal to 'maximum'."
            )

        if minimum.is_negative():
            # It is enough to check minimum since we know that minimum <= maximum
            raise ValueError("Parameter 'minimum' must not be negative.")

        self._minimum = minimum
        self._maximum = maximum
        self._currency = minimum.currency

    @property
    def minimum(self) -> CashAmount:
        return self._minimum

    @property
    def maximum(self) -> CashAmount:
        return self._maximum

    @property
    def members(self) -> tuple[CashAmount, CashAmount, FilterMode]:
        return (self._minimum, self._maximum, self._mode)

    def __repr__(self) -> str:
        return (
            f"CashAmountFilter(min={self._minimum.to_str_rounded()}, "
            f"max={self._maximum.to_str_rounded()}, mode={self._mode.name})"
        )

    def __eq__(self, __o: object) -> bool:
        if __o is None and self.mode == FilterMode.OFF:
            return True
        if not isinstance(__o, type(self)):
            return False
        if self._mode == FilterMode.OFF and __o.mode == FilterMode.OFF:
            return True
        try:
            return self.members == __o.members
        except CurrencyError:
            return False

    def __hash__(self) -> int:
        return hash(self.members)

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        if not isinstance(transaction, CashRelatedTransaction):
            return True
        amounts = self._get_amounts(transaction)
        try:
            amounts = self._convert_amounts(amounts)
        except ConversionFactorNotFoundError:
            return True
        return any(self._minimum <= amount <= self._maximum for amount in amounts)

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        if not isinstance(transaction, CashRelatedTransaction):
            return True
        amounts = self._get_amounts(transaction)
        try:
            amounts = self._convert_amounts(amounts)
        except ConversionFactorNotFoundError:
            return True
        return any(
            amount < self._minimum or amount > self._maximum for amount in amounts
        )

    def _get_amounts(
        self, transaction: CashRelatedTransaction
    ) -> tuple[CashAmount, ...]:
        if isinstance(
            transaction, CashTransaction | SecurityTransaction | RefundTransaction
        ):
            return (transaction.amount,)
        if isinstance(transaction, CashTransfer):
            return (transaction.amount_sent, transaction.amount_received)
        raise TypeError(  # pragma: no cover
            f"Unexpected transaction type: {type(transaction)}"
        )

    def _convert_amounts(
        self, amounts: tuple[CashAmount, ...]
    ) -> tuple[CashAmount, ...]:
        return tuple(amount.convert(self._currency) for amount in amounts)
