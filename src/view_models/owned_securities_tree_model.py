import contextlib
import unicodedata
from collections.abc import Collection
from decimal import Decimal

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush, QFont, QIcon
from PyQt6.QtWidgets import QTreeView
from src.models.model_objects.currency_objects import (
    CashAmount,
    ConversionFactorNotFoundError,
    Currency,
)
from src.models.model_objects.security_objects import Security, SecurityAccount
from src.utilities.formatting import get_short_percentage_string
from src.views import colors, icons
from src.views.constants import OwnedSecuritiesTreeColumn

ALIGNMENT_AMOUNTS = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
COLUMN_HEADERS = {
    OwnedSecuritiesTreeColumn.NAME: "Name",
    OwnedSecuritiesTreeColumn.SHARES: "Shares",
    OwnedSecuritiesTreeColumn.PRICE_MARKET: "Price",
    OwnedSecuritiesTreeColumn.PRICE_AVERAGE: "Avg. Price",
    OwnedSecuritiesTreeColumn.GAIN_NATIVE: "Native Gain",
    OwnedSecuritiesTreeColumn.GAIN_BASE: "Base Gain",
    OwnedSecuritiesTreeColumn.RETURN_NATIVE: "Native Return",
    OwnedSecuritiesTreeColumn.RETURN_BASE: "Base Return",
    OwnedSecuritiesTreeColumn.IRR_NATIVE: "Native IRR p.a.",
    OwnedSecuritiesTreeColumn.IRR_BASE: "Base IRR p.a.",
    OwnedSecuritiesTreeColumn.AMOUNT_NATIVE: "Native Value",
    OwnedSecuritiesTreeColumn.AMOUNT_BASE: "Base Value",
}
COLUMNS_NUMBERS = {
    OwnedSecuritiesTreeColumn.SHARES,
    OwnedSecuritiesTreeColumn.PRICE_MARKET,
    OwnedSecuritiesTreeColumn.PRICE_AVERAGE,
    OwnedSecuritiesTreeColumn.GAIN_NATIVE,
    OwnedSecuritiesTreeColumn.GAIN_BASE,
    OwnedSecuritiesTreeColumn.RETURN_NATIVE,
    OwnedSecuritiesTreeColumn.RETURN_BASE,
    OwnedSecuritiesTreeColumn.IRR_NATIVE,
    OwnedSecuritiesTreeColumn.IRR_BASE,
    OwnedSecuritiesTreeColumn.AMOUNT_NATIVE,
    OwnedSecuritiesTreeColumn.AMOUNT_BASE,
}

# TODO: add sync_nodes function

bold_font = QFont()
bold_font.setBold(True)  # noqa: FBT003


class TotalItem:
    def __init__(
        self, base_amount: CashAmount, gain_base: CashAmount, irr: Decimal
    ) -> None:
        self.base_amount = base_amount

        self.gain_base = gain_base
        self.return_base = round(
            100 * gain_base.value_normalized / base_amount.value_normalized, 2
        )
        self.irr_base = round(100 * irr, 2)

    @property
    def name(self) -> str:
        return "Σ Total"


class SecurityItem:
    def __init__(
        self, security: Security, irr_native: Decimal, irr_base: Decimal
    ) -> None:
        self.security = security
        self.shares = Decimal(0)
        self.accounts: list[AccountItem] = []
        self.native_currency = security.currency
        self.irr_native = round(100 * irr_native, 2)
        self.irr_base = round(100 * irr_base, 2)

    def __repr__(self) -> str:
        return f"SecurityItem(security={self.security.name})"

    @property
    def name(self) -> str:
        return self.security.name

    @property
    def is_base_currency(self) -> bool:
        return self.base_amount.currency == self.native_amount.currency

    def calculate_amounts(self, base_currency: Currency) -> None:
        self.native_amount = self.shares * self.security.price
        if base_currency is not None:
            try:
                self.base_amount = self.shares * self.security.price.convert(
                    base_currency
                )
            except ConversionFactorNotFoundError:
                self.base_amount = "Error!"
        else:
            self.base_amount = "N/A"

        avg_price_native = self.security.currency.zero_amount
        avg_price_base = base_currency.zero_amount
        for account in self.accounts:
            avg_price_native += account.avg_price_native * account.shares
            avg_price_base += account.avg_price_base * account.shares
        avg_price_native /= self.shares
        avg_price_base /= self.shares
        self.avg_price_native = avg_price_native

        self.gain_native = self.native_amount - avg_price_native * self.shares
        self.gain_base = self.base_amount - avg_price_base * self.shares
        self.return_native = round(
            100 * self.gain_native / (avg_price_native * self.shares), 2
        )
        self.return_base = round(
            100 * self.gain_base / (avg_price_base * self.shares), 2
        )


class AccountItem:
    def __init__(
        self,
        parent: SecurityItem,
        account: SecurityAccount,
        shares: Decimal,
        avg_price_native: CashAmount,
        avg_price_base: CashAmount,
        irr_native: Decimal,
        irr_base: Decimal,
        base_currency: Currency | None,
    ) -> None:
        self.parent = parent
        self.account = account
        self.shares = shares
        self.avg_price_native = avg_price_native
        self.avg_price_base = avg_price_base
        self.security = parent.security
        self.irr_native = round(100 * irr_native, 2)
        self.irr_base = round(100 * irr_base, 2)

        self.native_amount = shares * parent.security.price
        if base_currency is not None:
            try:
                self.base_amount = shares * parent.security.price.convert(base_currency)
            except ConversionFactorNotFoundError:
                self.base_amount = "Error!"
        else:
            self.base_amount = "N/A"

        self.gain_native = self.native_amount - avg_price_native * shares
        self.gain_base = self.base_amount - avg_price_base * shares
        with contextlib.suppress(Exception):
            self.return_native = round(
                100 * self.gain_native / (avg_price_native * shares), 2
            )
        self.return_base = round(100 * self.gain_base / (avg_price_base * shares), 2)

        self.native_currency = parent.security.currency

    @property
    def name(self) -> str:
        return self.account.path

    @property
    def is_base_currency(self) -> bool:
        return self.base_amount.currency == self.native_amount.currency

    def __repr__(self) -> str:
        return (
            f"AccountItem(account={self.account.path}, "
            f"security={self.security.name}, shares={self.shares})"
        )


class OwnedSecuritiesTreeModel(QAbstractItemModel):
    def __init__(
        self,
        tree_view: QTreeView,
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._tree_view = tree_view
        self._proxy = proxy
        self._tree_items = ()

    def load_data(
        self,
        accounts: Collection[SecurityAccount],
        irrs: dict[Security, dict[SecurityAccount | None, tuple[Decimal, Decimal]]],
        total_irr: Decimal,
        base_currency: Currency | None,
    ) -> None:
        tree_items: dict[Security, SecurityItem | TotalItem] = {}
        for account in accounts:
            for security, shares in account.securities.items():
                if security not in tree_items:
                    tree_items[security] = SecurityItem(
                        security, irrs[security][None][0], irrs[security][None][1]
                    )
                tree_items[security].shares += shares
                tree_items[security].accounts.append(
                    AccountItem(
                        tree_items[security],
                        account,
                        shares,
                        account.get_average_price(security),
                        account.get_average_price(security, None, base_currency),
                        irrs[security][account][0],
                        irrs[security][account][1],
                        base_currency,
                    )
                )

        total_gain = base_currency.zero_amount
        total_amount = base_currency.zero_amount
        for item in tree_items.values():
            item.calculate_amounts(base_currency)
            total_gain += item.gain_base
            total_amount += item.base_amount
        total_item = TotalItem(total_amount, total_gain, total_irr)
        tree_items["Total"] = total_item
        self._tree_items = tuple(tree_items.values())

    def rowCount(self, index: QModelIndex = ...) -> int:
        if index.isValid():
            if index.column() != 0:
                return 0
            item: SecurityItem | AccountItem | TotalItem = index.internalPointer()
            if isinstance(item, (AccountItem, TotalItem)):
                return 0
            return len(item.accounts)
        return len(self._tree_items)

    def columnCount(self, index: QModelIndex = ...) -> int:
        return (
            len(OwnedSecuritiesTreeColumn)
            if not index.isValid() or index.column() == 0
            else 0
        )

    def index(self, row: int, column: int, _parent: QModelIndex = ...) -> QModelIndex:
        if _parent.isValid() and _parent.column() != 0:
            return QModelIndex()

        if not _parent or not _parent.isValid():
            parent = None
        else:
            parent: SecurityItem = _parent.internalPointer()

        child = self._tree_items[row] if parent is None else parent.accounts[row]
        if child:
            return QAbstractItemModel.createIndex(self, row, column, child)
        return QModelIndex()

    def parent(self, index: QModelIndex = ...) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child: SecurityItem | AccountItem = index.internalPointer()
        parent = child.parent if isinstance(child, AccountItem) else None
        if parent is None:
            return QModelIndex()
        row = self._tree_items.index(parent)
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
        return None

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | Qt.AlignmentFlag | None:
        if not index.isValid():
            return None
        column = index.column()
        item: SecurityItem | AccountItem = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(column, item)
        if role == Qt.ItemDataRole.UserRole:
            return self._get_sort_data(column, item)
        if role == Qt.ItemDataRole.TextAlignmentRole and column in COLUMNS_NUMBERS:
            return ALIGNMENT_AMOUNTS
        if role == Qt.ItemDataRole.DecorationRole:
            return self._get_decoration_role_data(column, item)
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(column, item)
        if role == Qt.ItemDataRole.FontRole:
            return self._get_font_role_data(item)
        return None

    def _get_display_role_data(  # noqa: PLR0911
        self, column: int, item: SecurityItem | AccountItem | TotalItem
    ) -> str | Decimal | None:
        if column == OwnedSecuritiesTreeColumn.NAME:
            return item.name
        if column == OwnedSecuritiesTreeColumn.SHARES:
            if isinstance(item, TotalItem):
                return None
            return f"{item.shares:,}"
        if column == OwnedSecuritiesTreeColumn.PRICE_MARKET:
            if isinstance(item, SecurityItem):
                return item.security.price.to_str_rounded(item.security.price_decimals)
            return None
        if column == OwnedSecuritiesTreeColumn.PRICE_AVERAGE:
            if isinstance(item, TotalItem):
                return None
            return item.avg_price_native.to_str_rounded(item.security.price_decimals)
        if column == OwnedSecuritiesTreeColumn.GAIN_NATIVE:
            if isinstance(item, TotalItem) or item.is_base_currency:
                return None
            return item.gain_native.to_str_rounded()
        if column == OwnedSecuritiesTreeColumn.GAIN_BASE:
            return item.gain_base.to_str_rounded()
        if column == OwnedSecuritiesTreeColumn.RETURN_NATIVE:
            if isinstance(item, TotalItem) or item.is_base_currency:
                return None
            return get_short_percentage_string(item.return_native)
        if column == OwnedSecuritiesTreeColumn.RETURN_BASE:
            return get_short_percentage_string(item.return_base)
        if column == OwnedSecuritiesTreeColumn.IRR_NATIVE:
            if isinstance(item, TotalItem) or item.is_base_currency:
                return None
            return get_short_percentage_string(item.irr_native)
        if column == OwnedSecuritiesTreeColumn.IRR_BASE:
            return get_short_percentage_string(item.irr_base)
        if column == OwnedSecuritiesTreeColumn.AMOUNT_NATIVE:
            if isinstance(item, TotalItem) or item.is_base_currency:
                return None
            return item.native_amount.to_str_rounded()
        if column == OwnedSecuritiesTreeColumn.AMOUNT_BASE:
            if isinstance(item.base_amount, CashAmount):
                return item.base_amount.to_str_rounded()
            return item.base_amount
        return None

    def _get_sort_data(  # noqa: PLR0911
        self, column: int, item: SecurityItem | AccountItem | TotalItem
    ) -> str | Decimal | None:
        if column == OwnedSecuritiesTreeColumn.NAME:
            return unicodedata.normalize("NFD", item.name)
        if column == OwnedSecuritiesTreeColumn.SHARES:
            if isinstance(item, TotalItem):
                return None
            return float(item.shares)
        if column == OwnedSecuritiesTreeColumn.PRICE_MARKET:
            if isinstance(item, TotalItem):
                return None
            return float(item.security.price.value_rounded)
        if column == OwnedSecuritiesTreeColumn.PRICE_AVERAGE:
            if isinstance(item, TotalItem):
                return None
            return float(item.avg_price_native.value_rounded)
        if column == OwnedSecuritiesTreeColumn.GAIN_NATIVE:
            if isinstance(item, TotalItem) or item.is_base_currency:
                return None
            return float(item.gain_native.value_rounded)
        if column == OwnedSecuritiesTreeColumn.GAIN_BASE:
            return float(item.gain_base.value_rounded)
        if column == OwnedSecuritiesTreeColumn.RETURN_NATIVE:
            if isinstance(item, TotalItem) or item.is_base_currency:
                return None
            return float(item.return_native)
        if column == OwnedSecuritiesTreeColumn.RETURN_BASE:
            return float(item.return_base)
        if column == OwnedSecuritiesTreeColumn.IRR_NATIVE:
            if isinstance(item, TotalItem) or item.is_base_currency:
                return None
            return float(item.irr_native)
        if column == OwnedSecuritiesTreeColumn.IRR_BASE:
            return float(item.irr_base)
        if column == OwnedSecuritiesTreeColumn.AMOUNT_NATIVE:
            if isinstance(item, TotalItem) or item.is_base_currency:
                return None
            return float(item.native_amount.value_rounded)
        if column == OwnedSecuritiesTreeColumn.AMOUNT_BASE:
            if isinstance(item.base_amount, CashAmount):
                return float(item.base_amount.value_rounded)
            return item.base_amount
        return None

    def _get_decoration_role_data(
        self, column: int, item: SecurityItem | AccountItem | TotalItem
    ) -> QIcon | None:
        if column != OwnedSecuritiesTreeColumn.NAME or isinstance(item, TotalItem):
            return None
        if isinstance(item, SecurityItem):
            return QIcon(icons.security)
        return QIcon(icons.security_account)

    def _get_foreground_role_data(
        self, column: int, item: SecurityItem | AccountItem | TotalItem
    ) -> QBrush | None:
        if column == OwnedSecuritiesTreeColumn.SHARES:
            if isinstance(item, TotalItem):
                return None
            if item.shares < 0:
                return colors.get_red_brush()
        if column in {
            OwnedSecuritiesTreeColumn.GAIN_NATIVE,
            OwnedSecuritiesTreeColumn.RETURN_NATIVE,
        }:
            if isinstance(item, TotalItem) or item.is_base_currency:
                return None
            return _get_brush_color_from_number(item.return_native)
        if column in {
            OwnedSecuritiesTreeColumn.GAIN_BASE,
            OwnedSecuritiesTreeColumn.RETURN_BASE,
        }:
            return _get_brush_color_from_number(item.return_base)
        if column == OwnedSecuritiesTreeColumn.IRR_NATIVE:
            if isinstance(item, TotalItem) or item.is_base_currency:
                return None
            return _get_brush_color_from_number(item.irr_native)
        if column == OwnedSecuritiesTreeColumn.IRR_BASE:
            return _get_brush_color_from_number(item.irr_base)
        if (
            column
            in {
                OwnedSecuritiesTreeColumn.AMOUNT_NATIVE,
                OwnedSecuritiesTreeColumn.AMOUNT_BASE,
            }
            and not item.base_amount.is_nan()
            and item.base_amount.value_rounded < 0
        ):
            return colors.get_red_brush()
        return None

    def _get_font_role_data(
        self, item: SecurityItem | AccountItem | TotalItem
    ) -> QFont | None:
        if isinstance(item, TotalItem):
            return bold_font
        return None

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()


def _get_brush_color_from_number(number: Decimal) -> QBrush:
    if number.is_nan():
        return colors.get_red_brush()
    if number > 0:
        return colors.get_green_brush()
    if number < 0:
        return colors.get_red_brush()
    return colors.get_gray_brush()
