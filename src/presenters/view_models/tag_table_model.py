import typing
import unicodedata
from collections.abc import Sequence

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QTableView

from src.models.model_objects.attributes import Attribute
from src.models.utilities.calculation import AttributeStats
from src.views.constants import TagTableColumns


class TagTableModel(QAbstractTableModel):
    COLUMN_HEADERS = {
        TagTableColumns.COLUMN_NAME: "Name",
        TagTableColumns.COLUMN_TRANSACTIONS: "Transactions",
        TagTableColumns.COLUMN_BALANCE: "Total balance",
    }

    def __init__(
        self,
        view: QTableView,
        tag_stats: Sequence[AttributeStats],
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._view = view
        self.tag_stats = tag_stats
        self._proxy = proxy

    def rowCount(self, index: QModelIndex = ...) -> int:
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self.tag_stats)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: U100
        return 3

    def index(
        self, row: int, column: int, parent: QModelIndex = ...  # noqa: U100
    ) -> QModelIndex:
        if parent.isValid():
            return QModelIndex()
        if not QAbstractTableModel.hasIndex(self, row, column, QModelIndex()):
            return QModelIndex()

        item = self.tag_stats[row].attribute
        return QAbstractTableModel.createIndex(self, row, column, item)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> typing.Any:
        if not index.isValid():
            return None

        column = index.column()
        payee_stats = self.tag_stats[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            if column == TagTableColumns.COLUMN_NAME:
                return payee_stats.attribute.name
            if column == TagTableColumns.COLUMN_TRANSACTIONS:
                return payee_stats.no_of_transactions
            if column == TagTableColumns.COLUMN_BALANCE:
                return str(payee_stats.balance)
        if role == Qt.ItemDataRole.UserRole and column == TagTableColumns.COLUMN_NAME:
            return unicodedata.normalize("NFD", payee_stats.attribute.name)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column == TagTableColumns.COLUMN_TRANSACTIONS:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            if column == TagTableColumns.COLUMN_BALANCE:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
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

    def pre_remove_item(self, item: Attribute) -> None:
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

    def get_selected_item(self) -> Attribute | None:
        proxy_indexes = self._view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        if len(source_indexes) == 0:
            return None
        return source_indexes[0].internalPointer()

    def get_index_from_item(self, item: Attribute | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        for index, payee_stats in enumerate(self.tag_stats):
            if payee_stats.attribute == item:
                row = index
                break
        else:
            raise ValueError(f"Parameter {item=} not in PayeeTableModel.payee_stats.")
        return QAbstractTableModel.createIndex(self, row, 0, item)
