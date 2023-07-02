from collections.abc import Collection

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QTableView
from src.models.model_objects.currency_objects import ExchangeRate
from src.views.constants import ExchangeRateTableColumn, monospace_font

ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
COLUMN_HEADERS = {
    ExchangeRateTableColumn.CODE: "Code",
    ExchangeRateTableColumn.RATE: "Latest rate",
    ExchangeRateTableColumn.LAST_DATE: "Latest date",
}


class ExchangeRateTableModel(QAbstractTableModel):
    def __init__(
        self,
        view: QTableView,
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._view = view
        self._proxy = proxy
        self._exchange_rates = ()

    @property
    def exchange_rates(self) -> tuple[ExchangeRate, ...]:
        return self._exchange_rates

    def load_exchange_rates(self, exchange_rates: Collection[ExchangeRate]) -> None:
        self._exchange_rates = tuple(exchange_rates)

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self._exchange_rates)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802, ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(COLUMN_HEADERS)
        return self._column_count

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return COLUMN_HEADERS[section]
            return str(section)
        return None

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | Qt.AlignmentFlag | None:
        if not index.isValid():
            return None
        column = index.column()
        exchange_rate = self.exchange_rates[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(column, exchange_rate)
        if role == Qt.ItemDataRole.UserRole:
            return self._get_sort_role_data(column, exchange_rate)
        if (
            role == Qt.ItemDataRole.TextAlignmentRole
            and column == ExchangeRateTableColumn.RATE
        ):
            return ALIGNMENT_RIGHT
        if role == Qt.ItemDataRole.FontRole and column == ExchangeRateTableColumn.CODE:
            return monospace_font
        return None

    def _get_display_role_data(
        self, column: int, exchange_rate: ExchangeRate
    ) -> str | None:
        if column == ExchangeRateTableColumn.CODE:
            return str(exchange_rate)
        if column == ExchangeRateTableColumn.RATE:
            return f"{exchange_rate.latest_rate:,}"
        if column == ExchangeRateTableColumn.LAST_DATE:
            latest_date = exchange_rate.latest_date
            if latest_date is None:
                return "None"
            return latest_date.strftime("%d.%m.%Y")
        return None

    def _get_sort_role_data(
        self, column: int, exchange_rate: ExchangeRate
    ) -> str | None:
        if column == ExchangeRateTableColumn.CODE:
            return str(exchange_rate)
        if column == ExchangeRateTableColumn.RATE:
            return float(exchange_rate.latest_rate)
        if column == ExchangeRateTableColumn.LAST_DATE:
            latest_date = exchange_rate.latest_date
            if latest_date is None:
                return 0
            return latest_date.toordinal()
        return None

    def pre_add(self) -> None:
        self._proxy.setDynamicSortFilter(False)  # noqa: FBT003
        self._view.setSortingEnabled(False)  # noqa: FBT003
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

    def post_add(self) -> None:
        self.endInsertRows()
        self._proxy.setDynamicSortFilter(True)  # noqa: FBT003
        self._view.setSortingEnabled(True)  # noqa: FBT003

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()

    def pre_remove_item(self, item: ExchangeRate) -> None:
        index = self.get_index_from_item(item)
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())

    def post_remove_item(self) -> None:
        self.endRemoveRows()

    def get_selected_item(self) -> ExchangeRate | None:
        proxy_indexes = self._view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        if len(source_indexes) == 0:
            return None
        return self._exchange_rates[source_indexes[0].row()]

    def get_index_from_item(self, item: ExchangeRate | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        row = self.exchange_rates.index(item)
        return QAbstractTableModel.createIndex(self, row, 0)
