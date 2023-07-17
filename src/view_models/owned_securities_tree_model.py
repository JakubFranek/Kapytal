import unicodedata
from collections.abc import Collection
from decimal import Decimal

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTreeView
from src.models.model_objects.currency_objects import (
    CashAmount,
    ConversionFactorNotFoundError,
    Currency,
)
from src.models.model_objects.security_objects import Security, SecurityAccount
from src.views import icons
from src.views.constants import OwnedSecuritiesTreeColumn

ALIGNMENT_AMOUNTS = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
COLUMN_HEADERS = {
    OwnedSecuritiesTreeColumn.NAME: "Name",
    OwnedSecuritiesTreeColumn.SHARES: "Shares",
    OwnedSecuritiesTreeColumn.AMOUNT_NATIVE: "Native total",
    OwnedSecuritiesTreeColumn.AMOUNT_BASE: "Base total",
}


class SecurityItem:
    def __init__(self, security: Security) -> None:
        self.security = security
        self.total_shares = Decimal(0)
        self.accounts: list[AccountItem] = []

    def __repr__(self) -> str:
        return f"SecurityItem(security={self.security})"

    def calculate_amounts(self, base_currency: Currency) -> None:
        self.native_amount = self.total_shares * self.security.price
        if base_currency is not None:
            try:
                self.base_amount = self.total_shares * self.security.price.convert(
                    base_currency
                )
            except ConversionFactorNotFoundError:
                self.base_amount = "Error!"
        else:
            self.base_amount = "Error!"


class AccountItem:
    def __init__(
        self,
        parent: SecurityItem,
        account: SecurityAccount,
        shares: Decimal,
        base_currency: Currency | None,
    ) -> None:
        self.parent = parent
        self.account = account
        self.shares = shares

        self.native_amount = shares * parent.security.price
        if base_currency is not None:
            try:
                self.base_amount = shares * parent.security.price.convert(base_currency)
            except ConversionFactorNotFoundError:
                self.base_amount = "Error!"
        else:
            self.base_amount = "Error!"

    def __repr__(self) -> str:
        return f"AccountItem(account={self.account.path}, shares={self.shares})"


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
        self, accounts: Collection[SecurityAccount], base_currency: Currency | None
    ) -> None:
        tree_items: dict[Security, SecurityItem] = {}
        for account in accounts:
            for security, shares in account.securities.items():
                if security not in tree_items:
                    tree_items[security] = SecurityItem(security)
                tree_items[security].total_shares += shares
                tree_items[security].accounts.append(
                    AccountItem(tree_items[security], account, shares, base_currency)
                )
        self._tree_items = tuple(tree_items.values())
        for item in self._tree_items:
            item.calculate_amounts(base_currency)

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if index.isValid():
            if index.column() != 0:
                return 0
            item: SecurityItem | AccountItem = index.internalPointer()
            if isinstance(item, AccountItem):
                return 0
            return len(item.accounts)
        return len(self._tree_items)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        return 4 if not index.isValid() or index.column() == 0 else 0

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

    def headerData(  # noqa: N802
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
        if role == Qt.ItemDataRole.TextAlignmentRole and (
            column == OwnedSecuritiesTreeColumn.SHARES
            or column == OwnedSecuritiesTreeColumn.AMOUNT_NATIVE
            or column == OwnedSecuritiesTreeColumn.AMOUNT_BASE
        ):
            return ALIGNMENT_AMOUNTS
        if role == Qt.ItemDataRole.DecorationRole:
            return self._get_decoration_role_data(column, item)
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
                return f"{item.total_shares:,}"
            return f"{item.shares:,}"
        if column == OwnedSecuritiesTreeColumn.AMOUNT_NATIVE:
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
            if isinstance(item, SecurityItem):
                return float(item.total_shares)
            return float(item.shares)
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

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()
