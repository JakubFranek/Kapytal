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
    SecuritiesOverviewTreeColumn.PRICE_MARKET_NATIVE: "Market Price",
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_BUY_NATIVE: "Avg. Buy Price",
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_SELL_NATIVE: "Avg. Sell Price",
    SecuritiesOverviewTreeColumn.DIVIDEND_AVERAGE_NATIVE: "Avg. Dividend",
    SecuritiesOverviewTreeColumn.PRICE_MARKET_BASE: "Base Market Price",
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_BUY_BASE: "Base Avg. Buy Price",
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_SELL_BASE: "Base Avg. Sell Price",
    SecuritiesOverviewTreeColumn.DIVIDEND_AVERAGE_BASE: "Base Avg. Dividend",
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_NATIVE: "Native Gain (T)",
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_BASE: "Base Gain (T)",
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY_BASE: "Currency Gain (T)",
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_NATIVE: "Native Return (T)",
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_BASE: "Base Return (T)",
    SecuritiesOverviewTreeColumn.IRR_TOTAL_NATIVE: "Native IRR (T)",
    SecuritiesOverviewTreeColumn.IRR_TOTAL_BASE: "Base IRR (T)",
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_NATIVE: "Native Gain (R)",
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_BASE: "Base Gain (R)",
    SecuritiesOverviewTreeColumn.GAIN_DIVIDEND_NATIVE: "Native Dividends (R)",
    SecuritiesOverviewTreeColumn.GAIN_DIVIDEND_BASE: "Base Dividends (R)",
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_NATIVE: "Native Return (R)",
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_BASE: "Base Return (R)",
    SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_NATIVE: "Native Gain (U)",
    SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_BASE: "Base Gain (U)",
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_NATIVE: "Native Return (U)",
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_BASE: "Base Return (U)",
}

COLUMN_HEADER_TOOLTIPS = {
    SecuritiesOverviewTreeColumn.SHARES_OWNED: "Number of currently owned Shares",
    SecuritiesOverviewTreeColumn.SHARES_BOUGHT: "Number of bought Shares",
    SecuritiesOverviewTreeColumn.SHARES_SOLD: "Number of sold Shares",
    SecuritiesOverviewTreeColumn.SHARES_TRANSFERRED: (
        "Number of Shares transferred to (+) or from (-) Security Account"
    ),
    SecuritiesOverviewTreeColumn.AMOUNT_OWNED_NATIVE: (
        "Total market value of owned Shares in native Currency"
    ),
    SecuritiesOverviewTreeColumn.AMOUNT_OWNED_BASE: (
        "Total market value of owned Shares in base Currency"
    ),
    SecuritiesOverviewTreeColumn.AMOUNT_BOUGHT_NATIVE: (
        "Total amount spent on buying Shares in native Currency"
    ),
    SecuritiesOverviewTreeColumn.AMOUNT_BOUGHT_BASE: (
        "Total amount spent on buying Shares in base Currency"
    ),
    SecuritiesOverviewTreeColumn.AMOUNT_SOLD_NATIVE: (
        "Total amount received by selling Shares in native Currency"
    ),
    SecuritiesOverviewTreeColumn.AMOUNT_SOLD_BASE: (
        "Total amount received by selling Shares in base Currency"
    ),
    SecuritiesOverviewTreeColumn.PRICE_MARKET_NATIVE: (
        "Market Price of single Share in native Currency"
    ),
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_BUY_NATIVE: (
        "Average Buy Price in native Currency for a single Share"
    ),
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_SELL_NATIVE: (
        "Average Sell Price in native Currency for a single Share"
    ),
    SecuritiesOverviewTreeColumn.DIVIDEND_AVERAGE_NATIVE: (
        "Average Dividend per Share in native Currency"
    ),
    SecuritiesOverviewTreeColumn.PRICE_MARKET_BASE: (
        "Market Price of single Share in base Currency"
    ),
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_BUY_BASE: (
        "Average Buy Price in base Currency for a single Share"
    ),
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_SELL_BASE: (
        "Average Sell Price in base Currency for a single Share"
    ),
    SecuritiesOverviewTreeColumn.DIVIDEND_AVERAGE_BASE: (
        "Average Dividend per Share in base Currency"
    ),
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_NATIVE: (
        "Total Gain in native Currency\n[Native Gain (R) + Native Gain (U)]"
    ),
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_BASE: (
        "Total Gain in base Currency\n[Base Gain (R) + Base Gain (U)]"
    ),
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY_BASE: (
        "Total Currency Gain is the difference between\n"
        "the Total Base Gain and Total Native Gain\n"
        "(when converted to base Currency using the\n"
        "latest Exchange Rate)."
    ),
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_NATIVE: (
        "Total Return in native Currency\n[Native Gain (T) / Native Amount Bought]"
    ),
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_BASE: (
        "Total Return in base Currency\n[Base Gain (T) / Base Amount Bought]"
    ),
    SecuritiesOverviewTreeColumn.IRR_TOTAL_NATIVE: (
        "Total annualized Internal Rate of Return in native Currency"
    ),
    SecuritiesOverviewTreeColumn.IRR_TOTAL_BASE: (
        "Total annualized Internal Rate of Return in base Currency"
    ),
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_NATIVE: (
        "Realized Gain in native Currency\n"
        "[Shares Sold * (Avg. Sell Price - Avg. Buy Price) + Native Dividends (R)]"
    ),
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_BASE: (
        "Realized Gain in base Currency\n"
        "[Shares Sold * (Base Avg. Sell Price - Base Avg. Buy Price)"
        "+ Base Dividends (R)]"
    ),
    SecuritiesOverviewTreeColumn.GAIN_DIVIDEND_NATIVE: (
        "Total Dividends in native Currency"
    ),
    SecuritiesOverviewTreeColumn.GAIN_DIVIDEND_BASE: (
        "Total Dividends in base Currency"
    ),
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_NATIVE: (
        "Realized Return in native Currency\n"
        "[Shares Sold * (Avg. Sell Price - Avg. Buy Price)"
        "/ (Shares Sold * Avg. Buy Price)\n"
        "+ Native Dividends (R) / (Shares Bought * Avg. Buy Price)]"
    ),
    SecuritiesOverviewTreeColumn.RETURN_REALIZED_BASE: (
        "Realized Return in base Currency\n"
        "[Shares Sold * (Base Avg. Sell Price - Base Avg. Buy Price)"
        "/ (Shares Sold * Base Avg. Buy Price)\n"
        "+ Base Dividends (R) / (Shares Bought * Base Avg. Buy Price)]"
    ),
    SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_NATIVE: (
        "Unrealized Gain in native Currency\n"
        "[Shares Owned * (Market Price - Avg. Buy Price)]"
    ),
    SecuritiesOverviewTreeColumn.GAIN_UNREALIZED_BASE: (
        "Unrealized Gain in base Currency\n"
        "[Shares Owned * (Base Market Price - Base Avg. Buy Price)]"
    ),
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_NATIVE: (
        "Unrealized Return in native Currency\n"
        "[Native Gain (U) / (Shares Owned * Avg. Buy Price)]"
    ),
    SecuritiesOverviewTreeColumn.RETURN_UNREALIZED_BASE: (
        "Unrealized Return in base Currency\n"
        "[Base Gain (U) / (Shares Owned * Base Avg. Buy Price)]"
    ),
}

COLUMNS_TEXT = {SecuritiesOverviewTreeColumn.NAME}


COLUMNS_NATIVE = {
    SecuritiesOverviewTreeColumn.AMOUNT_OWNED_NATIVE,
    SecuritiesOverviewTreeColumn.AMOUNT_BOUGHT_NATIVE,
    SecuritiesOverviewTreeColumn.AMOUNT_SOLD_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_DIVIDEND_NATIVE,
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
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY_BASE,
    SecuritiesOverviewTreeColumn.GAIN_DIVIDEND_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_DIVIDEND_BASE,
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
    SecuritiesOverviewTreeColumn.PRICE_MARKET_NATIVE,
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_BUY_NATIVE,
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_SELL_NATIVE,
    SecuritiesOverviewTreeColumn.DIVIDEND_AVERAGE_NATIVE,
    SecuritiesOverviewTreeColumn.PRICE_MARKET_BASE,
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_BUY_BASE,
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_SELL_BASE,
    SecuritiesOverviewTreeColumn.DIVIDEND_AVERAGE_BASE,
}

COLUMNS_DIVIDEND = {
    SecuritiesOverviewTreeColumn.DIVIDEND_AVERAGE_NATIVE,
    SecuritiesOverviewTreeColumn.DIVIDEND_AVERAGE_BASE,
    SecuritiesOverviewTreeColumn.GAIN_DIVIDEND_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_DIVIDEND_BASE,
}

COLUMNS_COLOURFUL = {
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_BASE,
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY_BASE,
    SecuritiesOverviewTreeColumn.GAIN_DIVIDEND_BASE,
    SecuritiesOverviewTreeColumn.GAIN_DIVIDEND_NATIVE,
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
    SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY_BASE,
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.RETURN_TOTAL_BASE,
    SecuritiesOverviewTreeColumn.IRR_TOTAL_NATIVE,
    SecuritiesOverviewTreeColumn.IRR_TOTAL_BASE,
}
COLUMNS_REALIZED = {
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_NATIVE,
    SecuritiesOverviewTreeColumn.GAIN_REALIZED_BASE,
    SecuritiesOverviewTreeColumn.GAIN_DIVIDEND_BASE,
    SecuritiesOverviewTreeColumn.GAIN_DIVIDEND_NATIVE,
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
    SecuritiesOverviewTreeColumn.PRICE_MARKET_BASE,
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_SELL_NATIVE,
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_BUY_BASE,
    SecuritiesOverviewTreeColumn.PRICE_AVERAGE_SELL_BASE,
    SecuritiesOverviewTreeColumn.DIVIDEND_AVERAGE_BASE,
}


bold_font = QFont()
bold_font.setBold(True)


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

    def rowCount(self, index: QModelIndex | None = None) -> int:
        if index.isValid():
            if index.column() != 0:
                return 0
            item: SecurityStatsItem = index.internalPointer()
            if not isinstance(item, SecurityStats):
                return 0
            return len(item.account_stats)
        return len(self._data)

    def columnCount(self, index: QModelIndex | None = None) -> int:
        return (
            len(SecuritiesOverviewTreeColumn)
            if not index.isValid() or index.column() == 0
            else 0
        )

    def index(
        self, row: int, column: int, _parent: QModelIndex | None = None
    ) -> QModelIndex:
        if _parent.isValid() and _parent.column() != 0:
            return QModelIndex()

        parent: SecurityStats | None
        if not _parent or not _parent.isValid():
            parent = None
        else:
            parent = _parent.internalPointer()

        child = self._data[row] if parent is None else parent.account_stats[row]
        if child:
            return QAbstractItemModel.createIndex(self, row, column, child)
        return QModelIndex()

    def parent(self, index: QModelIndex | None = None) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child: SecurityStatsItem = index.internalPointer()
        parent = child.parent if isinstance(child, SecurityAccountStats) else None
        if parent is None:
            return QModelIndex()
        row = self._data.index(parent)
        return QAbstractItemModel.createIndex(self, row, 0, parent)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return COLUMN_HEADERS[section]
            return str(section)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        if role == Qt.ItemDataRole.ToolTipRole:
            return self._get_tooltip_role_header_data(section, None)
        return None

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole
    ) -> str | Qt.AlignmentFlag | float | None:
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
        if role == Qt.ItemDataRole.TextAlignmentRole and column not in COLUMNS_TEXT:
            return ALIGNMENT_FLAGS_AMOUNTS
        if role == Qt.ItemDataRole.DecorationRole:
            return self._get_decoration_role_data(column, item)
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(column, item)
        if role == Qt.ItemDataRole.FontRole:
            return self._get_font_role_data(item)
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
                column == SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY_BASE
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

        if column in COLUMNS_IRR and isinstance(text, str):
            text += " p.a."
        return text

    def _get_sort_data(
        self, column: int, item: SecurityStatsItem
    ) -> str | float | None:
        if column == SecuritiesOverviewTreeColumn.NAME:
            return unicodedata.normalize("NFD", item.name)
        if (
            self._get_display_role_data(column, item) is None
            or self._get_display_role_data(column, item) == ""
        ):
            return float("-inf")
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
        if column in COLUMNS_TEXT:
            return None

        return _get_brush_color_from_number(
            _get_numerical_attribute(item, column),
            green_allowed=column in COLUMNS_COLOURFUL,
        )

    def _get_font_role_data(self, item: SecurityStatsItem) -> QFont | None:
        if isinstance(item, TotalSecurityStats):
            return bold_font
        return None

    def _get_tooltip_role_header_data(
        self,
        column: int,
        item: SecurityStatsItem | None,  # noqa: ARG002
    ) -> str | None:
        if column in COLUMN_HEADER_TOOLTIPS:
            return COLUMN_HEADER_TOOLTIPS[column]
        return None

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()

    def show_dividend_amounts(self) -> bool:
        for stats in self._data:
            if (
                isinstance(stats, SecurityStats)
                and stats.amount_avg_dividend_native is not None
                and stats.amount_avg_dividend_native.value_normalized != 0
            ):
                return True
        return False


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
        return float("-inf")

    if isinstance(value, CashAmount):
        if value.is_nan():
            return float("-inf")
        return float(value.value_normalized)
    if value.is_nan():
        return float("-inf")
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

        case SecuritiesOverviewTreeColumn.PRICE_MARKET_NATIVE:
            _value = item.price_market_native
        case SecuritiesOverviewTreeColumn.PRICE_AVERAGE_BUY_NATIVE:
            _value = item.price_avg_buy_native
        case SecuritiesOverviewTreeColumn.PRICE_AVERAGE_SELL_NATIVE:
            _value = item.price_avg_sell_native
        case SecuritiesOverviewTreeColumn.DIVIDEND_AVERAGE_NATIVE:
            _value = item.amount_avg_dividend_native
        case SecuritiesOverviewTreeColumn.PRICE_MARKET_BASE:
            _value = item.price_market_base
        case SecuritiesOverviewTreeColumn.PRICE_AVERAGE_BUY_BASE:
            _value = item.price_avg_buy_base
        case SecuritiesOverviewTreeColumn.PRICE_AVERAGE_SELL_BASE:
            _value = item.price_avg_sell_base
        case SecuritiesOverviewTreeColumn.DIVIDEND_AVERAGE_BASE:
            _value = item.amount_avg_dividend_base

        case SecuritiesOverviewTreeColumn.GAIN_TOTAL_NATIVE:
            _value = item.gain_total_native
        case SecuritiesOverviewTreeColumn.GAIN_TOTAL_BASE:
            _value = item.gain_total_base
        case SecuritiesOverviewTreeColumn.GAIN_TOTAL_CURRENCY_BASE:
            _value = item.gain_total_currency
        case SecuritiesOverviewTreeColumn.GAIN_DIVIDEND_NATIVE:
            _value = item.value_dividend_native
        case SecuritiesOverviewTreeColumn.GAIN_DIVIDEND_BASE:
            _value = item.value_dividend_base
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
