import unicodedata
from collections.abc import Collection
from decimal import Decimal

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush
from PyQt6.QtWidgets import QTableView
from src.models.model_objects.security_objects import Security
from src.models.user_settings import user_settings
from src.utilities.formatting import format_percentage
from src.views import colors
from src.views.constants import SecurityTableColumn

ALIGNMENT_LEFT = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
COLUMN_HEADERS = {
    SecurityTableColumn.NAME: "Name",
    SecurityTableColumn.SYMBOL: "Symbol",
    SecurityTableColumn.TYPE: "Type",
    SecurityTableColumn.PRICE: "Price",
    SecurityTableColumn.LAST_DATE: "Latest Date",
    SecurityTableColumn.D1: "1D",
    SecurityTableColumn.D7: "7D",
    SecurityTableColumn.M1: "1M",
    SecurityTableColumn.M3: "3M",
    SecurityTableColumn.M6: "6M",
    SecurityTableColumn.Y1: "1Y",
    SecurityTableColumn.Y2: "2Y",
    SecurityTableColumn.Y3: "3Y",
    SecurityTableColumn.Y5: "5Y",
    SecurityTableColumn.Y7: "7Y",
    SecurityTableColumn.Y10: "10Y",
    SecurityTableColumn.YTD: "YTD",
    SecurityTableColumn.TOTAL: "Total",
    SecurityTableColumn.TOTAL_ANNUALIZED: "Total p.a.",
}
COLUMNS_ALIGNED_RIGHT = {
    SecurityTableColumn.PRICE,
    SecurityTableColumn.LAST_DATE,
    SecurityTableColumn.D1,
    SecurityTableColumn.D7,
    SecurityTableColumn.M1,
    SecurityTableColumn.M3,
    SecurityTableColumn.M6,
    SecurityTableColumn.Y1,
    SecurityTableColumn.Y2,
    SecurityTableColumn.Y3,
    SecurityTableColumn.Y5,
    SecurityTableColumn.Y7,
    SecurityTableColumn.Y10,
    SecurityTableColumn.YTD,
    SecurityTableColumn.TOTAL,
    SecurityTableColumn.TOTAL_ANNUALIZED,
}


class SecurityTableModel(QAbstractTableModel):
    def __init__(
        self,
        view: QTableView,
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._view = view
        self._securities = ()
        self._proxy = proxy

    @property
    def securities(self) -> tuple[Security, ...]:
        return self._securities

    def load_securities(
        self,
        securities: Collection[Security],
        returns: dict[Security, dict[str, Decimal]],
    ) -> None:
        self._securities = tuple(securities)
        self._returns = returns

    def rowCount(self, index: QModelIndex | None = None) -> int:
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self._securities)

    def columnCount(self, index: QModelIndex | None = None) -> int:  # noqa: ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(SecurityTableColumn)
        return self._column_count

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return COLUMN_HEADERS[section]
            return str(section)
        return None

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole
    ) -> str | Qt.AlignmentFlag | QBrush | None:
        if not index.isValid():
            return None

        column = index.column()
        security = self._securities[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(column, security)
        if role == Qt.ItemDataRole.UserRole:
            return self._get_user_role_data(column, security)
        if (
            role == Qt.ItemDataRole.TextAlignmentRole
            and column in COLUMNS_ALIGNED_RIGHT
        ):
            return ALIGNMENT_RIGHT
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(column, security)
        return None

    def _get_display_role_data(self, column: int, security: Security) -> str | None:
        if column == SecurityTableColumn.NAME:
            return security.name
        if column == SecurityTableColumn.SYMBOL:
            return security.symbol
        if column == SecurityTableColumn.TYPE:
            return security.type_
        if column == SecurityTableColumn.PRICE:
            return security.price.to_str_rounded(security.price_decimals)
        if column == SecurityTableColumn.LAST_DATE:
            latest_date = security.latest_date
            return (
                latest_date.strftime(user_settings.settings.general_date_format)
                if latest_date is not None
                else "None"
            )
        if (
            column >= SecurityTableColumn.D1
            and column <= SecurityTableColumn.TOTAL_ANNUALIZED
        ):
            _return = self._returns[security][COLUMN_HEADERS[column]]
            if _return.is_nan():
                return None
            return format_percentage(_return)
        return None

    def _get_user_role_data(  # noqa: PLR0911
        self,
        column: int,
        security: Security,
    ) -> str | float | None:
        if column == SecurityTableColumn.NAME:
            return unicodedata.normalize("NFD", security.name)
        if column == SecurityTableColumn.SYMBOL:
            return unicodedata.normalize("NFD", security.symbol)
        if column == SecurityTableColumn.TYPE:
            return unicodedata.normalize("NFD", security.type_)
        if column == SecurityTableColumn.PRICE:
            amount = security.price
            return float(amount.value_normalized)
        if column == SecurityTableColumn.LAST_DATE:
            latest_date = security.latest_date
            if latest_date is not None:
                return latest_date.toordinal()
            return None
        if (
            column >= SecurityTableColumn.D1
            and column <= SecurityTableColumn.TOTAL_ANNUALIZED
        ):
            _return = self._returns[security][COLUMN_HEADERS[column]]
            if _return.is_nan():
                return float("-inf")
            return float(_return)
        return None

    def _get_foreground_role_data(
        self, column: int, security: Security
    ) -> QBrush | None:
        if (
            column >= SecurityTableColumn.D1
            and column <= SecurityTableColumn.TOTAL_ANNUALIZED
        ):
            _return = self._returns[security][COLUMN_HEADERS[column]]
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

    def get_selected_item(self) -> Security | None:
        proxy_indexes = self._view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        if len(source_indexes) == 0:
            return None
        return self._securities[source_indexes[0].row()]

    def get_index_from_item(self, item: Security | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        row = self.securities.index(item)
        return QAbstractTableModel.createIndex(self, row, 0)

    def is_column_empty(self, column: int) -> bool:
        for row in range(self.rowCount()):
            text = self.index(row, column).data(Qt.ItemDataRole.DisplayRole)
            if text is not None and text != "":
                return False
        return True
