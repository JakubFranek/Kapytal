import numbers
import unicodedata
from collections.abc import Collection
from decimal import Decimal

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush, QIcon
from PyQt6.QtWidgets import QTreeView
from src.models.model_objects.currency_objects import (
    CashAmount,
    ConversionFactorNotFoundError,
    Currency,
)
from src.models.model_objects.security_objects import Security, SecurityAccount
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
    OwnedSecuritiesTreeColumn.ABSOLUTE_RETURN: "Abs. Return",
    OwnedSecuritiesTreeColumn.IRR: "IRR p.a.",
    OwnedSecuritiesTreeColumn.AMOUNT_NATIVE: "Native Value",
    OwnedSecuritiesTreeColumn.AMOUNT_BASE: "Base Value",
}
COLUMNS_NUMBERS = {
    OwnedSecuritiesTreeColumn.SHARES,
    OwnedSecuritiesTreeColumn.PRICE_MARKET,
    OwnedSecuritiesTreeColumn.PRICE_AVERAGE,
    OwnedSecuritiesTreeColumn.GAIN_NATIVE,
    OwnedSecuritiesTreeColumn.GAIN_BASE,
    OwnedSecuritiesTreeColumn.ABSOLUTE_RETURN,
    OwnedSecuritiesTreeColumn.IRR,
    OwnedSecuritiesTreeColumn.AMOUNT_NATIVE,
    OwnedSecuritiesTreeColumn.AMOUNT_BASE,
}

# TODO: add sync_nodes function


class SecurityItem:
    def __init__(self, security: Security, irr: Decimal) -> None:
        self.security = security
        self.shares = Decimal(0)
        self.accounts: list[AccountItem] = []
        self.native_currency = security.currency
        self.irr = round(100 * irr, 2)

    def __repr__(self) -> str:
        return f"SecurityItem(security={self.security.name})"

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
            self.base_amount = "Error!"

        avg_price = CashAmount(0, self.security.currency)
        for account in self.accounts:
            avg_price += account.avg_price * account.shares
        avg_price = avg_price / self.shares
        self.avg_price = avg_price

        self.gain_native = self.native_amount - avg_price * self.shares
        self.gain_base = self.gain_native.convert(base_currency)
        self.gain_pct = round(100 * self.gain_native / (avg_price * self.shares), 2)


class AccountItem:
    def __init__(
        self,
        parent: SecurityItem,
        account: SecurityAccount,
        shares: Decimal,
        avg_price: CashAmount,
        irr: Decimal,
        base_currency: Currency | None,
    ) -> None:
        self.parent = parent
        self.account = account
        self.shares = shares
        self.avg_price = avg_price
        self.security = parent.security
        self.irr = round(100 * irr, 2)

        self.native_amount = shares * parent.security.price
        if base_currency is not None:
            try:
                self.base_amount = shares * parent.security.price.convert(base_currency)
            except ConversionFactorNotFoundError:
                self.base_amount = "Error!"
        else:
            self.base_amount = "Error!"

        self.gain_native = self.native_amount - avg_price * shares
        self.gain_base = self.gain_native.convert(base_currency)
        try:
            self.gain_pct = round(100 * self.gain_native / (avg_price * shares), 2)
        except Exception:
            pass

        self.native_currency = parent.security.currency

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
        irrs: dict[Security, dict[SecurityAccount | None, Decimal]],
        base_currency: Currency | None,
    ) -> None:
        tree_items: dict[Security, SecurityItem] = {}
        for account in accounts:
            for security, shares in account.securities.items():
                if security not in tree_items:
                    tree_items[security] = SecurityItem(security, irrs[security][None])
                tree_items[security].shares += shares
                tree_items[security].accounts.append(
                    AccountItem(
                        tree_items[security],
                        account,
                        shares,
                        account.get_average_price(security),
                        irrs[security][account],
                        base_currency,
                    )
                )
        self._tree_items = tuple(tree_items.values())
        for item in self._tree_items:
            item.calculate_amounts(base_currency)

    def rowCount(self, index: QModelIndex = ...) -> int:
        if index.isValid():
            if index.column() != 0:
                return 0
            item: SecurityItem | AccountItem = index.internalPointer()
            if isinstance(item, AccountItem):
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
        if role == Qt.ItemDataRole.UserRole:  # sort role
            return self._get_sort_data(column, item)
        if role == Qt.ItemDataRole.TextAlignmentRole and column in COLUMNS_NUMBERS:
            return ALIGNMENT_AMOUNTS
        if role == Qt.ItemDataRole.DecorationRole:
            return self._get_decoration_role_data(column, item)
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(column, item)
        return None

    def _get_display_role_data(  # noqa: PLR0911
        self, column: int, item: SecurityItem | AccountItem
    ) -> str | Decimal | None:
        if column == OwnedSecuritiesTreeColumn.NAME:
            if isinstance(item, SecurityItem):
                return item.security.name
            return item.account.path
        if column == OwnedSecuritiesTreeColumn.SHARES:
            if isinstance(item, SecurityItem):
                return f"{item.shares:,}"
            return f"{item.shares:,}"
        if column == OwnedSecuritiesTreeColumn.PRICE_MARKET:
            if isinstance(item, SecurityItem):
                return item.security.price.to_str_rounded(item.security.price_decimals)
            return None
        if column == OwnedSecuritiesTreeColumn.PRICE_AVERAGE:
            return item.avg_price.to_str_rounded(item.security.price_decimals)
        if column == OwnedSecuritiesTreeColumn.GAIN_NATIVE:
            if item.gain_native.currency != item.gain_base.currency:
                return item.gain_native.to_str_rounded()
            return None
        if column == OwnedSecuritiesTreeColumn.GAIN_BASE:
            return item.gain_base.to_str_rounded()
        if column == OwnedSecuritiesTreeColumn.ABSOLUTE_RETURN:
            return f"{item.gain_pct:,} %"
        if column == OwnedSecuritiesTreeColumn.IRR:
            return f"{item.irr:,} %"
        if column == OwnedSecuritiesTreeColumn.AMOUNT_NATIVE:
            if (
                isinstance(item.base_amount, CashAmount)
                and item.native_amount.currency == item.base_amount.currency
            ):
                return ""
            return item.native_amount.to_str_rounded()
        if column == OwnedSecuritiesTreeColumn.AMOUNT_BASE:
            if isinstance(item.base_amount, CashAmount):
                return item.base_amount.to_str_rounded()
            return item.base_amount
        return None

    def _get_sort_data(  # noqa: PLR0911
        self, column: int, item: SecurityItem | AccountItem
    ) -> str | Decimal | None:
        if column == OwnedSecuritiesTreeColumn.NAME:
            if isinstance(item, SecurityItem):
                return unicodedata.normalize("NFD", item.security.name)
            return unicodedata.normalize("NFD", item.account.path)
        if column == OwnedSecuritiesTreeColumn.SHARES:
            return float(item.shares)
        if column == OwnedSecuritiesTreeColumn.PRICE_MARKET:
            return float(item.security.price.value_rounded)
        if column == OwnedSecuritiesTreeColumn.PRICE_AVERAGE:
            return float(item.avg_price.value_rounded)
        if column == OwnedSecuritiesTreeColumn.GAIN_NATIVE:
            return float(item.gain_native.value_rounded)
        if column == OwnedSecuritiesTreeColumn.GAIN_BASE:
            return float(item.gain_base.value_rounded)
        if column == OwnedSecuritiesTreeColumn.ABSOLUTE_RETURN:
            return float(item.gain_pct)
        if column == OwnedSecuritiesTreeColumn.IRR:
            return float(item.irr)
        if column == OwnedSecuritiesTreeColumn.AMOUNT_NATIVE:
            return float(item.native_amount.value_rounded)
        if column == OwnedSecuritiesTreeColumn.AMOUNT_BASE:
            if isinstance(item.base_amount, CashAmount):
                return float(item.base_amount.value_rounded)
            return item.base_amount
        return None

    def _get_decoration_role_data(
        self, column: int, item: SecurityItem | AccountItem
    ) -> QIcon | None:
        if column != OwnedSecuritiesTreeColumn.NAME:
            return None
        if isinstance(item, SecurityItem):
            return QIcon(icons.security)
        return QIcon(icons.security_account)

    def _get_foreground_role_data(
        self, column: int, item: SecurityItem | AccountItem
    ) -> QBrush | None:
        if column == OwnedSecuritiesTreeColumn.SHARES and item.shares < 0:
            return colors.get_red_brush()
        if column in {
            OwnedSecuritiesTreeColumn.GAIN_NATIVE,
            OwnedSecuritiesTreeColumn.GAIN_BASE,
            OwnedSecuritiesTreeColumn.ABSOLUTE_RETURN,
        }:
            return _get_brush_color_from_number(item.gain_pct)
        if column == OwnedSecuritiesTreeColumn.IRR:
            return _get_brush_color_from_number(item.irr)
        if (
            column
            in {
                OwnedSecuritiesTreeColumn.AMOUNT_NATIVE,
                OwnedSecuritiesTreeColumn.AMOUNT_BASE,
            }
            and item.base_amount.value_rounded < 0
        ):
            return colors.get_red_brush()
        return None

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()


def _get_brush_color_from_number(number: numbers.Real) -> QBrush:
    if number > 0:
        return colors.get_green_brush()
    if number < 0:
        return colors.get_red_brush()
    return colors.get_gray_brush()
