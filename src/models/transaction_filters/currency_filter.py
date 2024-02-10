from collections.abc import Collection

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import CashRelatedTransaction
from src.models.model_objects.currency_objects import Currency
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)


class CurrencyFilter(BaseTransactionFilter):
    """Filters Transactions based on whether they are related to specific Currencies.
    Ignores Transactions without a Currency."""

    __slots__ = ("_currencies", "_mode")

    def __init__(self, currencies: Collection[Currency], mode: FilterMode) -> None:
        super().__init__(mode)
        if not all(isinstance(currency, Currency) for currency in currencies):
            raise TypeError(
                "Parameter 'currencies' must be a Collection of Currencies."
            )
        self._currencies = frozenset(currencies)

    @property
    def currencies(self) -> frozenset[Currency]:
        return self._currencies

    @property
    def currency_codes(self) -> tuple[str, ...]:
        return tuple(sorted(currency.code for currency in self._currencies))

    @property
    def members(self) -> tuple[frozenset[Currency], FilterMode]:
        return (self._currencies, self._mode)

    def __repr__(self) -> str:
        return (
            f"CurrencyFilter(currencies={self.currency_codes}, mode={self._mode.name})"
        )

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        if not isinstance(transaction, CashRelatedTransaction):
            return True
        return any(currency in transaction.currencies for currency in self._currencies)

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        if not isinstance(transaction, CashRelatedTransaction):
            return True
        return not any(
            currency in transaction.currencies for currency in self._currencies
        )
