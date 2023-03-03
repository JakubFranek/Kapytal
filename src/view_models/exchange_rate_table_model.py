import typing
from collections.abc import Collection

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtWidgets import QTableView

from src.models.model_objects.currency_objects import ExchangeRate
from src.views.constants import ExchangeRateTableColumns


class ExchangeRateTableModel(QAbstractTableModel):
    COLUMN_HEADERS = {
        ExchangeRateTableColumns.COLUMN_CODE: "Exchange Rate",
        ExchangeRateTableColumns.COLUMN_RATE: "Latest rate",
        ExchangeRateTableColumns.COLUMN_LAST_DATE: "Latest date",
    }

    def __init__(
        self, view: QTableView, exchange_rates: tuple[ExchangeRate, ...]
    ) -> None:
        super().__init__()
        self._tree = view
        self.exchange_rates = exchange_rates

    @property
    def exchange_rates(self) -> tuple[ExchangeRate, ...]:
        return self._exchange_rates

    @exchange_rates.setter
    def exchange_rates(self, exchange_rates: Collection[ExchangeRate]) -> None:
        self._exchange_rates = tuple(exchange_rates)

    def rowCount(self, index: QModelIndex = ...) -> int:
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self.exchange_rates)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: U100
        return 3

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        if parent.isValid():
            return QModelIndex()
        if not QAbstractTableModel.hasIndex(self, row, column, QModelIndex()):
            return QModelIndex()
        item = self.exchange_rates[row]
        return QAbstractTableModel.createIndex(self, row, column, item)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> typing.Any:
        if not index.isValid():
            return None
        column = index.column()
        exchange_rate = self.exchange_rates[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if column == ExchangeRateTableColumns.COLUMN_CODE:
                return str(exchange_rate)
            if column == ExchangeRateTableColumns.COLUMN_RATE:
                return (
                    f"1 {exchange_rate.primary_currency.code} = "
                    f"{str(exchange_rate.latest_rate)} "
                    f"{exchange_rate.secondary_currency.code}"
                )
            if column == ExchangeRateTableColumns.COLUMN_LAST_DATE:
                latest_date = exchange_rate.latest_date
                if latest_date is None:
                    return "None"
                return latest_date.strftime("%Y-%m-%d")
        if (
            role == Qt.ItemDataRole.TextAlignmentRole
            and column == ExchangeRateTableColumns.COLUMN_RATE
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
        if role == Qt.ItemDataRole.TextAlignmentRole and (
            section == ExchangeRateTableColumns.COLUMN_LAST_DATE
            or section == ExchangeRateTableColumns.COLUMN_CODE
        ):
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

    def pre_remove_item(self, item: ExchangeRate) -> None:
        index = self.get_index_from_item(item)
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())

    def post_remove_item(self) -> None:
        self.endRemoveRows()

    def get_selected_item_index(self) -> QModelIndex:
        indexes = self._tree.selectedIndexes()
        if len(indexes) == 0:
            return QModelIndex()
        return indexes[0]

    def get_selected_item(self) -> ExchangeRate | None:
        indexes = self._tree.selectedIndexes()
        if len(indexes) == 0:
            return None
        return indexes[0].internalPointer()

    def get_index_from_item(self, item: ExchangeRate | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        row = self.exchange_rates.index(item)
        return QAbstractTableModel.createIndex(self, row, 0, item)
