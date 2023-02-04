import typing

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTableView

from src.models.model_objects.currency_objects import Currency
from src.views.constants import CurrencyTableColumns


class CurrencyTableModel(QAbstractTableModel):
    COLUMN_HEADERS = {
        CurrencyTableColumns.COLUMN_CODE: "Currency code",
        CurrencyTableColumns.COLUMN_PLACES: "Decimal places",
    }

    def __init__(
        self,
        view: QTableView,
        currencies: tuple[Currency, ...],
        base_currency: Currency,
    ) -> None:
        super().__init__()
        self._tree = view
        self.currencies = currencies
        self.base_currency = base_currency

    def rowCount(self, index: QModelIndex = ...) -> int:
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self.currencies)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: U100
        return 2

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        if parent.isValid():
            return QModelIndex()
        if not QAbstractTableModel.hasIndex(self, row, column, QModelIndex()):
            return QModelIndex()
        item = self.currencies[row]
        return QAbstractTableModel.createIndex(self, row, column, item)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> typing.Any:
        if not index.isValid():
            return None
        column = index.column()
        currency = self.currencies[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if column == CurrencyTableColumns.COLUMN_CODE:
                return currency.code
            if column == CurrencyTableColumns.COLUMN_PLACES:
                return str(currency.places)
        if (
            role == Qt.ItemDataRole.DecorationRole
            and column == CurrencyTableColumns.COLUMN_CODE
            and currency == self.base_currency
        ):
            return QIcon("icons_16:star.png")
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
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

    def post_add(self) -> None:
        self.endInsertRows()

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()

    def pre_delete_item(self, index: QModelIndex) -> None:
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())

    def post_delete_item(self) -> None:
        self.endRemoveRows()

    def get_selected_item_index(self) -> QModelIndex:
        indexes = self._tree.selectedIndexes()
        if len(indexes) == 0:
            return QModelIndex()
        return indexes[0]

    def get_selected_item(self) -> Currency | None:
        indexes = self._tree.selectedIndexes()
        if len(indexes) == 0:
            return None
        return indexes[0].internalPointer()

    def get_index_from_item(self, item: Currency | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        row = self.currencies.index(item)
        return QAbstractTableModel.createIndex(self, row, 0, item)
