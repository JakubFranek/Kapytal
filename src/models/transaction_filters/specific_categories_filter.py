import unicodedata
from collections.abc import Collection

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import (
    Category,
    CategoryType,
)
from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)


class SpecificCategoriesFilter(BaseTransactionFilter):
    """Filters CashTransactions and RefundTransactions based on whether they have
    specific Categories.Ignores other Transactions.

    KEEP: Keeps only Transactions with at least one of the specified Categories.
    DISCARD: Discards Transactions with at least one of the specified Categories."""

    __slots__ = ("_categories", "_mode")

    def __init__(self, categories: Collection[Category], mode: FilterMode) -> None:
        super().__init__(mode=mode)

        if any(not isinstance(category, Category) for category in categories):
            raise TypeError(
                "Parameter 'categories' must be a Collection of Categories."
            )
        self._categories = frozenset(categories)

    @property
    def categories(self) -> frozenset[Category]:
        return self._categories

    @property
    def income_categories(self) -> frozenset[Category]:
        return frozenset(
            category
            for category in self._categories
            if category.type_ == CategoryType.INCOME
        )

    @property
    def expense_categories(self) -> frozenset[Category]:
        return frozenset(
            category
            for category in self._categories
            if category.type_ == CategoryType.EXPENSE
        )

    @property
    def dual_purpose_categories(self) -> frozenset[Category]:
        return frozenset(
            category
            for category in self._categories
            if category.type_ == CategoryType.DUAL_PURPOSE
        )

    @property
    def category_paths(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                (category.path for category in self._categories),
                key=lambda path: unicodedata.normalize("NFD", path.lower()),
            )
        )

    @property
    def members(self) -> tuple[frozenset[Category], FilterMode]:
        return (self._categories, self._mode)

    def __repr__(self) -> str:
        return (
            f"SpecificCategoriesFilter(categories={self.category_paths}, "
            f"mode={self._mode.name})"
        )

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        return (
            isinstance(transaction, CashTransaction | RefundTransaction)
            and any(category in self._categories for category in transaction.categories)
        ) or not isinstance(transaction, CashTransaction | RefundTransaction)

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        return (
            isinstance(transaction, CashTransaction | RefundTransaction)
            and not any(
                category in self._categories for category in transaction.categories
            )
        ) or not isinstance(transaction, CashTransaction | RefundTransaction)
