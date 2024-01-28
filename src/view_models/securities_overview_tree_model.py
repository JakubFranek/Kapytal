import math
import unicodedata
from decimal import Decimal

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush, QFont, QIcon
from PyQt6.QtWidgets import QTreeView
from src.models.model_objects.currency_objects import CashAmount
from src.models.statistics.security_stats import (
    SecurityAccountStats,
    SecurityStats,
    SecurityStatsData,
    SecurityStatsItem,
    TotalSecurityStats,
)
from src.utilities.formatting import format_percentage
from src.views import colors, icons
from src.views.constants import SecuritiesOverviewTreeColumn

ALIGNMENT_FLAGS_AMOUNTS = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

COLUMN_HEADERS = {
    SecuritiesOverviewTreeColumn.NAME: "Name",
    SecuritiesOverviewTreeColumn.SHARES_OWNED: "Shares Owned",
    SecuritiesOverviewTreeColumn.SHARES_BOUGHT: "Shares Bought",
    SecuritiesOverviewTreeColumn.SHARES_SOLD: "Shares Sold",
    SecuritiesOverviewTreeColumn.SHARES_TRANSFERRED: "Shares Transferred",
    SecuritiesOverviewTreeColumn.AMOUNT_OWNED_NATIVE: "Native Amount",
    SecuritiesOverviewTreeColumn.AMOUNT_OWNED_BASE: "Base Amount",
    SecuritiesOverviewTreeColumn.AMOUNT_BOUGHT_NATIVE: "Native Bought Amount",
    SecuritiesOverviewTreeColumn.AMOUNT_BOUGHT_BASE: "Base Bought Amount",
    SecuritiesOverviewTreeColumn.AMOUNT_SOLD_NATIVE: "Native Sold Amount",
    SecuritiesOverviewTreeColumn.AMOUNT_SOLD_BASE: "Base Sold Amount",
    SecuritiesOverviewTreeColumn.PRICE_MARKET: "Market Price",
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_BUY: "Avg. Buy Price",
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_SELL: "Avg. Sell Price",
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_NATIVE: "Native Gain (T)",
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_BASE: "Base Gain (T)",
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY: "Currency Gain (T)",
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_NATIVE: "Native Return (T)",
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_BASE: "Base Return (T)",
    SecuritiesOverviewTreeColumn.IRR_TOTAL_NATIVE: "Native IRR (T)",
    SecuritiesOverviewTreeColumn.IRR_TOTAL_BASE: "Base IRR (T)",
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_NATIVE: "Native Gain (R)",
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_BASE: "Base Gain (R)",
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_NATIVE: "Native Return (R)",
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_BASE: "Base Return (R)",
    SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_NATIVE: "Native Gain (U)",
    SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_BASE: "Base Gain (U)",
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_NATIVE: "Native Return (U)",
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_BASE: "Base Return (U)",
}

COLUMNS_NUMERICAL = {
    SecuritiesOverviewTreeColumn.SHARES_OWNED,
    SecuritiesOverviewTreeColumn.SHARES_BOUGHT,
    SecuritiesOverviewTreeColumn.SHARES_SOLD,
    SecuritiesOverviewTreeColumn.SHARES_TRANSFERRED,
    SecuritiesOverviewTreeColumn.AMOUNT_OWNED_NATIVE,
    SecuritiesOverviewTreeColumn.AMOUNT_OWNED_BASE,
    SecuritiesOverviewTreeColumn.AMOUNT_BOUGHT_NATIVE,
    SecuritiesOverviewTreeColumn.AMOUNT_BOUGHT_BASE,
    SecuritiesOverviewTreeColumn.AMOUNT_SOLD_NATIVE,
    SecuritiesOverviewTreeColumn.AMOUNT_SOLD_BASE,
    SecuritiesOverviewTreeColumn.PRICE_MARKET,
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_BUY,
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_SELL,
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_BASE,
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY,
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_BASE,
    SecuritiesOverviewTreeColumn.IRR_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.IRR_TOTAL_BASE,
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_BASE,
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_BASE,
    SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_BASE,
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_BASE,
}

COLUMNS_NATIVE = {
    SecuritiesOverviewTreeColumn.AMOUNT_OWNED_NATIVE,
    SecuritiesOverviewTreeColumn.AMOUNT_BOUGHT_NATIVE,
    SecuritiesOverviewTreeColumn.AMOUNT_SOLD_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.IRR_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_NATIVE,
}

COLUMNS_TOTAL_STATS_ITEM = {
    SecuritiesOverviewTreeColumn.AMOUNT_OWNED_NATIVE,
    SecuritiesOverviewTreeColumn.AMOUNT_OWNED_BASE,
    SecuritiesOverviewTreeColumn.AMOUNT_BOUGHT_NATIVE,
    SecuritiesOverviewTreeColumn.AMOUNT_BOUGHT_BASE,
    SecuritiesOverviewTreeColumn.AMOUNT_SOLD_NATIVE,
    SecuritiesOverviewTreeColumn.AMOUNT_SOLD_BASE,
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_BASE,
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY,
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_BASE,
    SecuritiesOverviewTreeColumn.IRR_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.IRR_TOTAL_BASE,
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_BASE,
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_BASE,
    SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_BASE,
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_BASE,
}

COLUMNS_PERCENTAGE = {
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_BASE,
    SecuritiesOverviewTreeColumn.IRR_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.IRR_TOTAL_BASE,
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_BASE,
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_BASE,
}

COLUMNS_PRICE = {
    SecuritiesOverviewTreeColumn.PRICE_MARKET,
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_BUY,
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_SELL,
}

COLUMNS_COLOURFUL = {
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_BASE,
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY,
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_BASE,
    SecuritiesOverviewTreeColumn.IRR_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.IRR_TOTAL_BASE,
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_BASE,
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_BASE,
    SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_BASE,
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_BASE,
}

COLUMNS_IRR = {
    SecuritiesOverviewTreeColumn.IRR_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.IRR_TOTAL_BASE,
}

COLUMNS_TOTAL = {
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_BASE,
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY,
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_BASE,
    SecuritiesOverviewTreeColumn.IRR_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.IRR_TOTAL_BASE,
}

COLUMNS_REALIZED = {
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_BASE,
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_BASE,
}

COLUMNS_UNREALIZED = {
    SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_BASE,
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_BASE,
}

COLUMNS_DETAILED = {
    SecuritiesOverviewTreeColumn.SHARES_BOUGHT,
    SecuritiesOverviewTreeColumn.SHARES_SOLD,
    SecuritiesOverviewTreeColumn.SHARES_TRANSFERRED,
    SecuritiesOverviewTreeColumn.AMOUNT_BOUGHT_NATIVE,
    SecuritiesOverviewTreeColumn.AMOUNT_BOUGHT_BASE,
    SecuritiesOverviewTreeColumn.AMOUNT_SOLD_NATIVE,
    SecuritiesOverviewTreeColumn.AMOUNT_SOLD_BASE,
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_SELL,
}

GAIN_TOTAL_CURRENCY_TOOLTIP = (
    "Total Currency Gain is the difference between\n"
    "the Total Base Gain and Total Native Gain\n"
    "(when converted to base Currency using the\n"
    "latest Exchange Rate)."
)

bold_font = QFont()
bold_font.setBold(True)  # noqa: FBT003


class SecuritiesOverviewTreeModel(QAbstractItemModel):
    def __init__(
        self,
        tree_view: QTreeView,
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._tree_view = tree_view
        self._proxy = proxy
        self._data = ()

    def load_data(self, data: SecurityStatsData) -> None:
        self._data = data.stats

    def rowCount(self, index: QModelIndex = ...) -> int:
        if index.isValid():
            if index.column() != 0:
                return 0
            item: SecurityStatsItem = index.internalPointer()
            if not isinstance(item, SecurityStats):
                return 0
            return len(item.account_stats)
        return len(self._data)

    def columnCount(self, index: QModelIndex = ...) -> int:
        return (
            len(SecuritiesOverviewTreeColumn)
            if not index.isValid() or index.column() == 0
            else 0
        )

    def index(self, row: int, column: int, _parent: QModelIndex = ...) -> QModelIndex:
        if _parent.isValid() and _parent.column() != 0:
            return QModelIndex()

        if not _parent or not _parent.isValid():
            parent = None
        else:
            parent: SecurityStats = _parent.internalPointer()

        child = self._data[row] if parent is None else parent.account_stats[row]
        if child:
            return QAbstractItemModel.createIndex(self, row, column, child)
        return QModelIndex()

    def parent(self, index: QModelIndex = ...) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child: SecurityStatsItem = index.internalPointer()
        parent = child.parent if isinstance(child, SecurityAccountStats) else None
        if parent is None:
            return QModelIndex()
        row = self._data.index(parent)
        return QAbstractItemModel.createIndex(self, row, 0, parent)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return COLUMN_HEADERS[section]
            return str(section)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        if (
            role == Qt.ItemDataRole.ToolTipRole
            and section == SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY
        ):
            return GAIN_TOTAL_CURRENCY_TOOLTIP
        return None

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | Qt.AlignmentFlag | None:
        if not index.isValid():
            return None

        column = index.column()
        item: SecurityStatsItem = index.internalPointer()

        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(column, item)
        if role == Qt.ItemDataRole.UserRole:
            return self._get_sort_data(column, item)
        if role == Qt.ItemDataRole.UserRole + 1:
            return self._get_filter_data(column, item)
        if role == Qt.ItemDataRole.TextAlignmentRole and column in COLUMNS_NUMERICAL:
            return ALIGNMENT_FLAGS_AMOUNTS
        if role == Qt.ItemDataRole.DecorationRole:
            return self._get_decoration_role_data(column, item)
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(column, item)
        if role == Qt.ItemDataRole.FontRole:
            return self._get_font_role_data(item)
        if role == Qt.ItemDataRole.ToolTipRole:
            return self._get_tooltip_role_data(column, item)
        return None

    def _get_display_role_data(
        self, column: int, item: SecurityStatsItem
    ) -> str | Decimal | None:
        if column == SecuritiesOverviewTreeColumn.NAME:
            return item.name

        percentage = column in COLUMNS_PERCENTAGE

        if (
            column in COLUMNS_NATIVE
            or (
                column == SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY
                and not isinstance(item, TotalSecurityStats)
            )
        ) and item.is_base:
            return None

        if column in COLUMNS_PRICE and isinstance(
            item, (SecurityStats, SecurityAccountStats)
        ):
            decimals = item.security.price_decimals
        else:
            decimals = None

        text = _convert_numerical_attribute_to_text(
            _get_numerical_attribute(item, column),
            percentage=percentage,
            decimals=decimals,
        )

        if column in COLUMNS_IRR:
            text += " p.a."
        return text

    def _get_sort_data(
        self, column: int, item: SecurityStatsItem
    ) -> str | float | None:
        if column == SecuritiesOverviewTreeColumn.NAME:
            return unicodedata.normalize("NFD", item.name)
        return _convert_numerical_attribute_to_float(
            _get_numerical_attribute(item, column)
        )

    def _get_filter_data(self, column: int, item: SecurityStatsItem) -> str | None:
        if column != SecuritiesOverviewTreeColumn.NAME:
            return None

        text = (
            item.parent.name + "/" + item.name
            if isinstance(item, SecurityAccountStats)
            else item.name
        )
        return unicodedata.normalize("NFD", text)

    def _get_decoration_role_data(
        self, column: int, item: SecurityStatsItem
    ) -> QIcon | None:
        if column != SecuritiesOverviewTreeColumn.NAME:
            return None

        if isinstance(item, TotalSecurityStats):
            return icons.sum_
        if isinstance(item, SecurityStats):
            return icons.security
        return icons.security_account

    def _get_foreground_role_data(
        self, column: int, item: SecurityStatsItem
    ) -> QBrush | None:
        if column not in COLUMNS_NUMERICAL:
            return None

        return _get_brush_color_from_number(
            _get_numerical_attribute(item, column),
            green_allowed=column in COLUMNS_COLOURFUL,
        )

    def _get_tooltip_role_data(
        self,
        column: int,
        item: SecurityStatsItem,  # noqa: ARG002
    ) -> str | None:
        if column != SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY:
            return None
        return GAIN_TOTAL_CURRENCY_TOOLTIP

    def _get_font_role_data(self, item: SecurityStatsItem) -> QFont | None:
        if isinstance(item, TotalSecurityStats):
            return bold_font
        return None

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()


def _get_brush_color_from_number(
    number: Decimal | CashAmount | None, *, green_allowed: bool
) -> QBrush | None:
    if number is None:
        return None

    _value = number.value_rounded if isinstance(number, CashAmount) else number

    if _value.is_nan():
        return colors.get_gray_brush()
    if math.isclose(_value, 0, abs_tol=1e-3):
        return colors.get_gray_brush()
    if _value < 0:
        return colors.get_red_brush()
    if _value > 0:
        return colors.get_green_brush() if green_allowed else None
    return colors.get_gray_brush()


def _convert_numerical_attribute_to_text(
    value: CashAmount | Decimal | None,
    *,
    decimals: int | None = None,
    percentage: bool = False,
) -> str | None:
    if value is None:
        return None

    if isinstance(value, CashAmount):
        return value.to_str_rounded(decimals=decimals)

    if percentage:
        return format_percentage(value)
    return f"{value:n}"


def _convert_numerical_attribute_to_float(
    value: CashAmount | Decimal | None,
) -> float | None:
    if value is None:
        return None

    if isinstance(value, CashAmount):
        return float(value.value_normalized)
    return float(value)


def _get_numerical_attribute(
    item: SecurityStatsItem, column: int
) -> CashAmount | Decimal | None:
    if not isinstance(item, (SecurityStats, SecurityAccountStats, TotalSecurityStats)):
        raise TypeError(
            "Expected SecurityStats, SecurityAccountStats, or TotalSecurityStats, "
            f"got {type(item)}"
        )

    if isinstance(item, TotalSecurityStats) and column not in COLUMNS_TOTAL_STATS_ITEM:
        return None

    match column:
        case SecuritiesOverviewTreeColumn.SHARES_OWNED:
            _value = item.shares_owned
        case SecuritiesOverviewTreeColumn.SHARES_BOUGHT:
            _value = item.shares_bought
        case SecuritiesOverviewTreeColumn.SHARES_SOLD:
            _value = item.shares_sold
        case SecuritiesOverviewTreeColumn.SHARES_TRANSFERRED:
            _value = item.shares_transferred

        case SecuritiesOverviewTreeColumn.AMOUNT_OWNED_NATIVE:
            _value = item.value_current_native
        case SecuritiesOverviewTreeColumn.AMOUNT_OWNED_BASE:
            _value = item.value_current_base
        case SecuritiesOverviewTreeColumn.AMOUNT_BOUGHT_NATIVE:
            _value = item.value_bought_native
        case SecuritiesOverviewTreeColumn.AMOUNT_BOUGHT_BASE:
            _value = item.value_bought_base
        case SecuritiesOverviewTreeColumn.AMOUNT_SOLD_NATIVE:
            _value = item.value_sold_native
        case SecuritiesOverviewTreeColumn.AMOUNT_SOLD_BASE:
            _value = item.value_sold_base

        case SecuritiesOverviewTreeColumn.PRICE_MARKET:
            _value = item.price_market_native
        case SecuritiesOverviewTreeColumn.PRICE_AVERAGE_BUY:
            _value = item.price_avg_buy_native
        case SecuritiesOverviewTreeColumn.PRICE_AVERAGE_SELL:
            _value = item.price_avg_sell_native

        case SecuritiesOverviewTreeColumn.GAIN_TOTAL_NATIVE:
            _value = item.gain_total_native
        case SecuritiesOverviewTreeColumn.GAIN_TOTAL_BASE:
            _value = item.gain_total_base
        case SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY:
            _value = item.gain_total_currency
        case SecuritiesOverviewTreeColumn.RETURN_TOTAL_NATIVE:
            _value = item.return_pct_total_native
        case SecuritiesOverviewTreeColumn.RETURN_TOTAL_BASE:
            _value = item.return_pct_total_base
        case SecuritiesOverviewTreeColumn.IRR_TOTAL_NATIVE:
            _value = item.irr_pct_total_native
        case SecuritiesOverviewTreeColumn.IRR_TOTAL_BASE:
            _value = item.irr_pct_total_base

        case SecuritiesOverviewTreeColumn.GAIN_REALIZED_NATIVE:
            _value = item.gain_realized_native
        case SecuritiesOverviewTreeColumn.GAIN_REALIZED_BASE:
            _value = item.gain_realized_base
        case SecuritiesOverviewTreeColumn.RETURN_REALIZED_NATIVE:
            _value = item.return_pct_realized_native
        case SecuritiesOverviewTreeColumn.RETURN_REALIZED_BASE:
            _value = item.return_pct_realized_base

        case SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_NATIVE:
            _value = item.gain_unrealized_native
        case SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_BASE:
            _value = item.gain_unrealized_base
        case SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_NATIVE:
            _value = item.return_pct_unrealized_native
        case SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_BASE:
            _value = item.return_pct_unrealized_base
        case _:
            _value = None

    return _value
