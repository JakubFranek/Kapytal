from typing import TYPE_CHECKING

from PyQt6.QtCore import QModelIndex, QObject, QSortFilterProxyModel
from src.models.transaction_filters.transaction_filter import TransactionFilter

if TYPE_CHECKING:
    from src.view_models.transaction_table_model import TransactionTableModel


class TransactionTableProxyModel(QSortFilterProxyModel):
    def __init__(self, parent: QObject, transaction_filter: TransactionFilter) -> None:
        super().__init__(parent)
        self.transaction_filter = transaction_filter

    @property
    def transaction_filter(self) -> TransactionFilter:
        return self._transaction_filter

    @transaction_filter.setter
    def transaction_filter(self, transaction_filter: TransactionFilter) -> None:
        self._transaction_filter = transaction_filter
        self.invalidateFilter()

    def filterAcceptsRow(  # noqa: N802
        self, source_row: int, source_parent: QModelIndex
    ) -> bool:
        del source_parent
        # TODO: the line below could be optimized (source model does not change)
        source_model: TransactionTableModel = self.sourceModel()
        transaction = source_model.transactions[source_row]

        return self._transaction_filter.validate_transaction(transaction)
