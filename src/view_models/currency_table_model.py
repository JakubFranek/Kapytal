from collections.abc import Collection

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTableView
from src.models.model_objects.currency_objects import Currency
from src.views import icons
from src.views.constants import CurrencyTableColumn


class CurrencyTableModel(QAbstractTableModel):
    COLUMN_HEADERS = {
        CurrencyTableColumn.CODE: "Currency code",
        CurrencyTableColumn.PLACES: "Decimal places",
    }

    def __init__(
        self,
        view: QTableView,
        currencies: tuple[Currency, ...],
        base_currency: Currency,
    ) -> None:
        super().__init__()
        self._view = view
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
        return len(self._currencies)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802, ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(self.COLUMN_HEADERS)
        return self._column_count

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | QIcon | None:
        if not index.isValid():
            return None
        column = index.column()
        currency = self._currencies[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if column == CurrencyTableColumn.CODE:
                return currency.code
            if column == CurrencyTableColumn.PLACES:
                return str(currency.places)
        if (
            role == Qt.ItemDataRole.DecorationRole
            and column == CurrencyTableColumn.CODE
            and currency == self.base_currency
        ):
            return icons.base_currency
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
        indexes = self._view.selectedIndexes()
        if len(indexes) == 0:
            return QModelIndex()
        return indexes[0]

    def get_selected_item(self) -> Currency | None:
        indexes = self._view.selectedIndexes()
        if len(indexes) == 0:
            return None
        return self._currencies[indexes[0].row()]

    def get_index_from_item(self, item: Currency | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        row = self.currencies.index(item)
        return QAbstractTableModel.createIndex(self, row, 0)
