from collections.abc import Collection

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTableView
from src.models.model_objects.currency_objects import Currency
from src.views.constants import CurrencyTableColumn


class CurrencyTableModel(QAbstractTableModel):
    COLUMN_HEADERS = {
        CurrencyTableColumn.COLUMN_CODE: "Currency code",
        CurrencyTableColumn.COLUMN_PLACES: "Decimal places",
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

    @property
    def currencies(self) -> tuple[Currency, ...]:
        return self._currencies

    @currencies.setter
    def currencies(self, currencies: Collection[Currency]) -> None:
        self._currencies = tuple(currencies)

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self.currencies)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        del index
        return 2

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        if parent.isValid():
            return QModelIndex()
        if not QAbstractTableModel.hasIndex(self, row, column, QModelIndex()):
            return QModelIndex()
        item = self.currencies[row]
        return QAbstractTableModel.createIndex(self, row, column, item)

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | QIcon | None:
        if not index.isValid():
            return None
        column = index.column()
        currency = self.currencies[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if column == CurrencyTableColumn.COLUMN_CODE:
                return currency.code
            if column == CurrencyTableColumn.COLUMN_PLACES:
                return str(currency.places)
        if (
            role == Qt.ItemDataRole.DecorationRole
            and column == CurrencyTableColumn.COLUMN_CODE
            and currency == self.base_currency
        ):
            return QIcon("icons_16:star.png")
        return None

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.COLUMN_HEADERS[section]
            return str(section)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        return None

    def pre_add(self) -> None:
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

    def post_add(self) -> None:
        self.endInsertRows()

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()

    def pre_remove_item(self, item: Currency) -> None:
        index = self.get_index_from_item(item)
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())

    def post_remove_item(self) -> None:
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
