import typing
import unicodedata
from collections.abc import Collection

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QTableView

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import (
    CashTransaction,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.security_objects import (
    SecurityTransaction,
    SecurityTransfer,
)
from src.views.constants import TransactionTableColumns


class TransactionTableModel(QAbstractTableModel):
    COLUMN_HEADERS = {
        TransactionTableColumns.COLUMN_DATETIME: "Date & time",
        TransactionTableColumns.COLUMN_DESCRIPTION: "Description",
        TransactionTableColumns.COLUMN_TYPE: "Type",
        TransactionTableColumns.COLUMN_ACCOUNT: "Account",
        TransactionTableColumns.COLUMN_PAYEE: "Payee",
        TransactionTableColumns.COLUMN_SENDER: "Sender",
        TransactionTableColumns.COLUMN_RECIPIENT: "Recipient",
        TransactionTableColumns.COLUMN_SECURITY: "Security",
        TransactionTableColumns.COLUMN_AMOUNT: "Amount",
        TransactionTableColumns.COLUMN_AMOUNT_BASE: "Base amount",
        TransactionTableColumns.COLUMN_BALANCE: "Balance",
        TransactionTableColumns.COLUMN_CATEGORY: "Category",
        TransactionTableColumns.COLUMN_TAG: "Tags",
        TransactionTableColumns.COLUMN_UUID: "UUID",
    }

    def __init__(
        self,
        view: QTableView,
        transactions: Collection[Transaction],
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._view = view
        self.transactions = tuple(transactions)
        self._proxy = proxy

    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return self._transactions

    @transactions.setter
    def transactions(self, transactions: Collection[Transaction]) -> None:
        self._transactions = tuple(transactions)

    def rowCount(self, index: QModelIndex = ...) -> int:
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self.transactions)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: U100
        return 14

    def index(
        self, row: int, column: int, parent: QModelIndex = ...  # noqa: U100
    ) -> QModelIndex:
        if parent.isValid():
            return QModelIndex()
        if not QAbstractTableModel.hasIndex(self, row, column, QModelIndex()):
            return QModelIndex()

        item = self.transactions[row]
        return QAbstractTableModel.createIndex(self, row, column, item)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> typing.Any:
        if not index.isValid():
            return None

        column = index.column()
        transaction = self.transactions[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return "test"
        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.COLUMN_HEADERS[section]
            return str(section)
        return None

    def pre_add(self) -> None:
        self._proxy.setDynamicSortFilter(False)
        self._view.setSortingEnabled(False)
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

    def post_add(self) -> None:
        self.endInsertRows()
        self._view.setSortingEnabled(True)
        self._proxy.setDynamicSortFilter(True)

    def pre_reset_model(self) -> None:
        self._view.setSortingEnabled(False)
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()
        self._view.setSortingEnabled(True)

    def pre_remove_item(self, item: Transaction) -> None:
        index = self.get_index_from_item(item)
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())

    def post_remove_item(self) -> None:
        self.endRemoveRows()

    def get_selected_item_index(self) -> QModelIndex:
        proxy_indexes = self._view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        if len(source_indexes) == 0:
            return QModelIndex()
        return source_indexes[0]

    def get_selected_item(self) -> Transaction | None:
        proxy_indexes = self._view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        if len(source_indexes) == 0:
            return None
        return source_indexes[0].internalPointer()

    def get_index_from_item(self, item: Transaction | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        row = self.transactions.index(item)
        return QAbstractTableModel.createIndex(self, row, 0, item)
