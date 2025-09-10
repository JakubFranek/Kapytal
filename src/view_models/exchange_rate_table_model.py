from collections.abc import Collection
from decimal import Decimal

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush
from PyQt6.QtWidgets import QTableView
from src.models.model_objects.currency_objects import ExchangeRate
from src.models.user_settings import user_settings
from src.utilities.formatting import format_percentage, format_real
from src.views import colors
from src.views.constants import ExchangeRateTableColumn, monospace_font

ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
COLUMNS_ALIGNED_RIGHT = {
    ExchangeRateTableColumn.RATE,
    ExchangeRateTableColumn.LAST_DATE,
    ExchangeRateTableColumn.D1,
    ExchangeRateTableColumn.D7,
    ExchangeRateTableColumn.M1,
    ExchangeRateTableColumn.M3,
    ExchangeRateTableColumn.M6,
    ExchangeRateTableColumn.Y1,
    ExchangeRateTableColumn.Y2,
    ExchangeRateTableColumn.Y3,
    ExchangeRateTableColumn.Y5,
    ExchangeRateTableColumn.Y7,
    ExchangeRateTableColumn.Y10,
    ExchangeRateTableColumn.YTD,
    ExchangeRateTableColumn.TOTAL,
    ExchangeRateTableColumn.TOTAL_ANNUALIZED,
}

COLUMN_HEADERS = {
    ExchangeRateTableColumn.CODE: "Code",
    ExchangeRateTableColumn.RATE: "Latest Quote",
    ExchangeRateTableColumn.LAST_DATE: "Latest Date",
    ExchangeRateTableColumn.D1: "1D",
    ExchangeRateTableColumn.D7: "7D",
    ExchangeRateTableColumn.M1: "1M",
    ExchangeRateTableColumn.M3: "3M",
    ExchangeRateTableColumn.M6: "6M",
    ExchangeRateTableColumn.Y1: "1Y",
    ExchangeRateTableColumn.Y2: "2Y",
    ExchangeRateTableColumn.Y3: "3Y",
    ExchangeRateTableColumn.Y5: "5Y",
    ExchangeRateTableColumn.Y7: "7Y",
    ExchangeRateTableColumn.Y10: "10Y",
    ExchangeRateTableColumn.YTD: "YTD",
    ExchangeRateTableColumn.TOTAL: "Total",
    ExchangeRateTableColumn.TOTAL_ANNUALIZED: "Total p.a.",
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

    def load_data(
        self,
        exchange_rates: Collection[ExchangeRate],
        stats: dict[ExchangeRate, dict[str, Decimal]],
    ) -> None:
        self._exchange_rates = tuple(exchange_rates)
        self._stats = stats

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if isinstance(parent, QModelIndex) and parent.isValid():
            return 0
        return len(self._exchange_rates)

    def columnCount(self, parent: QModelIndex = ...) -> int:  # noqa: ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(COLUMN_HEADERS)
        return self._column_count

    def headerData(
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
            and column in COLUMNS_ALIGNED_RIGHT
        ):
            return ALIGNMENT_RIGHT
        if role == Qt.ItemDataRole.FontRole and column == ExchangeRateTableColumn.CODE:
            return monospace_font
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(column, exchange_rate)
        return None

    def _get_display_role_data(
        self, column: int, exchange_rate: ExchangeRate
    ) -> str | None:
        if column == ExchangeRateTableColumn.CODE:
            return str(exchange_rate)
        if column == ExchangeRateTableColumn.RATE:
            return format_real(exchange_rate.latest_rate, exchange_rate.rate_decimals)
        if column == ExchangeRateTableColumn.LAST_DATE:
            latest_date = exchange_rate.latest_date
            if latest_date is None:
                return "None"
            return latest_date.strftime(user_settings.settings.general_date_format)
        if (
            column >= ExchangeRateTableColumn.D1
            and column <= ExchangeRateTableColumn.TOTAL_ANNUALIZED
        ):
            _return = self._stats[exchange_rate][COLUMN_HEADERS[column]]
            if _return.is_nan():
                return None
            return format_percentage(_return)
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
        if (
            column >= ExchangeRateTableColumn.D1
            and column <= ExchangeRateTableColumn.TOTAL_ANNUALIZED
        ):
            _return = self._stats[exchange_rate][COLUMN_HEADERS[column]]
            if _return.is_nan():
                return float("-inf")
            return float(_return)
        return None

    def _get_foreground_role_data(
        self, column: int, exchange_rate: ExchangeRate
    ) -> QBrush | None:
        if (
            column >= ExchangeRateTableColumn.D1
            and column <= ExchangeRateTableColumn.TOTAL_ANNUALIZED
        ):
            _return = self._stats[exchange_rate][COLUMN_HEADERS[column]]
            if _return.is_nan():
                return None
            if _return == 0:
                return colors.get_gray_brush()
            if _return < 0:
                return colors.get_red_brush()
            return colors.get_green_brush()
        return None

    def pre_add(self) -> None:
        self._proxy.setDynamicSortFilter(False)
        self._view.setSortingEnabled(False)
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

    def post_add(self) -> None:
        self.endInsertRows()
        self._proxy.setDynamicSortFilter(True)
        self._view.setSortingEnabled(True)

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

    def is_column_empty(self, column: int) -> bool:
        for row in range(self.rowCount()):
            text = self.index(row, column).data(Qt.ItemDataRole.DisplayRole)
            if text is not None and text != "":
                return False
        return True
