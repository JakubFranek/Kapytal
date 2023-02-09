import typing
import unicodedata
from collections.abc import Sequence

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QTableView

from src.models.model_objects.security_objects import Security
from src.views.constants import SecurityTableColumns


class SecurityTableModel(QAbstractTableModel):
    COLUMN_HEADERS = {
        SecurityTableColumns.COLUMN_NAME: "Name",
        SecurityTableColumns.COLUMN_SYMBOL: "Symbol",
        SecurityTableColumns.COLUMN_TYPE: "Type",
        SecurityTableColumns.COLUMN_PRICE: "Latest price",
        SecurityTableColumns.COLUMN_LAST_DATE: "Latest date",
    }

    def __init__(
        self,
        view: QTableView,
        securities: Sequence[Security],
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._view = view
        self.securities = securities
        self._proxy = proxy

    def rowCount(self, index: QModelIndex = ...) -> int:
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self.securities)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: U100
        return 5

    def index(
        self, row: int, column: int, parent: QModelIndex = ...  # noqa: U100
    ) -> QModelIndex:
        if parent.isValid():
            return QModelIndex()
        if not QAbstractTableModel.hasIndex(self, row, column, QModelIndex()):
            return QModelIndex()

        item = self.securities[row]
        return QAbstractTableModel.createIndex(self, row, column, item)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> typing.Any:
        if not index.isValid():
            return None

        column = index.column()
        security = self.securities[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            if column == SecurityTableColumns.COLUMN_NAME:
                return security.name
            if column == SecurityTableColumns.COLUMN_SYMBOL:
                return security.symbol
            if column == SecurityTableColumns.COLUMN_TYPE:
                return security.type_
            if column == SecurityTableColumns.COLUMN_PRICE:
                return str(security.price.convert(security.currency))
            if column == SecurityTableColumns.COLUMN_LAST_DATE:
                latest_date = security.latest_date
                if latest_date is None:
                    return "None"
                return latest_date.strftime("%Y-%m-%d")
        if (
            role == Qt.ItemDataRole.UserRole
            and column == SecurityTableColumns.COLUMN_NAME
        ):
            return unicodedata.normalize("NFD", security.name)
        if (
            role == Qt.ItemDataRole.TextAlignmentRole
            and column == SecurityTableColumns.COLUMN_PRICE
        ):
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

    def pre_remove_item(self, item: Security) -> None:
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

    def get_selected_item(self) -> Security | None:
        proxy_indexes = self._view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        if len(source_indexes) == 0:
            return None
        return source_indexes[0].internalPointer()

    def get_index_from_item(self, item: Security | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        row = self.securities.index(item)
        return QAbstractTableModel.createIndex(self, row, 0, item)
