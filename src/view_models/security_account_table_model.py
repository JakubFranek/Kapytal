import unicodedata
from decimal import Decimal

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QTableView
from src.models.model_objects.currency_objects import (
    ConversionFactorNotFoundError,
    Currency,
)
from src.models.model_objects.security_objects import Security, SecurityAccount
from src.views.constants import SecurityAccountTableColumn

ALIGNMENT_AMOUNTS = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


class SecurityAccountTableModel(QAbstractTableModel):
    COLUMN_HEADERS = {
        SecurityAccountTableColumn.SECURITY_NAME: "Security",
        SecurityAccountTableColumn.SYMBOL: "Symbol",
        SecurityAccountTableColumn.TYPE: "Type",
        SecurityAccountTableColumn.SHARES: "Shares",
        SecurityAccountTableColumn.PRICE: "Price",
        SecurityAccountTableColumn.AMOUNT_NATIVE: "Native Total",
        SecurityAccountTableColumn.AMOUNT_BASE: "Base Total",
    }

    def __init__(
        self,
        view: QTableView,
        security_account: SecurityAccount | None,
        base_currency: Currency | None,
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._view = view
        self.security_account = security_account
        self.base_currency = base_currency
        self._proxy = proxy
        self._securities = ()

    @property
    def security_account(self) -> SecurityAccount | None:
        return self._security_account

    @security_account.setter
    def security_account(self, value: SecurityAccount | None) -> None:
        self._security_account = value
        if isinstance(self._security_account, SecurityAccount):
            self._securities: tuple[tuple[Security, Decimal], ...] = tuple(
                (security, shares)
                for security, shares in self._security_account.securities.items()
            )
        else:
            self._securities = ()

    @property
    def base_currency(self) -> Currency | None:
        return self._base_currency

    @base_currency.setter
    def base_currency(self, value: Currency | None) -> None:
        self._base_currency = value

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self._securities)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802, ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(self.COLUMN_HEADERS)
        return self._column_count

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        if parent.isValid():
            return QModelIndex()
        if row < 0 or column < 0:
            return QModelIndex()
        if row >= len(self._securities) or column >= self._column_count:
            return QModelIndex()

        return QAbstractTableModel.createIndex(self, row, column)

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return self.COLUMN_HEADERS[section]
        return None

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | Qt.AlignmentFlag | None:
        if not index.isValid():
            return None

        column = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            security = self._securities[row][0]
            shares = self._securities[row][1]
            return self._get_display_role_data(column, security, shares)
        if role == Qt.ItemDataRole.UserRole:
            row = index.row()
            security = self._securities[row][0]
            shares = self._securities[row][1]
            return self._get_user_role_data(column, security, shares)
        if role == Qt.ItemDataRole.TextAlignmentRole and (
            column == SecurityAccountTableColumn.PRICE
            or column == SecurityAccountTableColumn.AMOUNT_NATIVE
            or column == SecurityAccountTableColumn.AMOUNT_BASE
        ):
            return ALIGNMENT_AMOUNTS
        return None

    def _get_display_role_data(  # noqa: PLR0911
        self, column: int, security: Security, shares: Decimal
    ) -> str | None:
        if column == SecurityAccountTableColumn.SECURITY_NAME:
            return security.name
        if column == SecurityAccountTableColumn.SYMBOL:
            return security.symbol
        if column == SecurityAccountTableColumn.TYPE:
            return security.type_
        if column == SecurityAccountTableColumn.SHARES:
            return str(shares)
        if column == SecurityAccountTableColumn.PRICE:
            return security.price.to_str_normalized()
        if column == SecurityAccountTableColumn.AMOUNT_NATIVE:
            amount = security.price * shares
            return amount.to_str_rounded()
        if column == SecurityAccountTableColumn.AMOUNT_BASE:
            try:
                amount = security.price.convert(self.base_currency) * shares
                return amount.to_str_rounded()
            except ConversionFactorNotFoundError:
                return "Error!"
        return None

    def _get_user_role_data(  # noqa: PLR0911
        self, column: int, security: Security, shares: Decimal
    ) -> str | None:
        if column == SecurityAccountTableColumn.SECURITY_NAME:
            return unicodedata.normalize("NFD", security.name)
        if column == SecurityAccountTableColumn.SYMBOL:
            return unicodedata.normalize("NFD", security.symbol)
        if column == SecurityAccountTableColumn.TYPE:
            return unicodedata.normalize("NFD", security.type_)
        if column == SecurityAccountTableColumn.SHARES:
            return float(shares)
        if column == SecurityAccountTableColumn.PRICE:
            amount = security.price
            return float(amount.value_normalized)
        if column == SecurityAccountTableColumn.AMOUNT_NATIVE:
            amount = security.price * shares
            return float(amount.value_normalized)
        if column == SecurityAccountTableColumn.AMOUNT_BASE:
            try:
                amount = security.price.convert(self.base_currency) * shares
                return float(amount.value_normalized)
            except ConversionFactorNotFoundError:
                return None
        return None

    def pre_reset_model(self) -> None:
        self._view.setSortingEnabled(False)  # noqa: FBT003
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()
        self._view.setSortingEnabled(True)  # noqa: FBT003
