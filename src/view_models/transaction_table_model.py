import unicodedata
from collections.abc import Collection
from typing import Any

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush, QColor, QIcon
from PyQt6.QtWidgets import QTableView

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import (
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import Currency
from src.models.model_objects.security_objects import (
    SecurityRelatedTransaction,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
)
from src.views.constants import (
    TRANSACTION_TABLE_COLUMN_HEADERS,
    TransactionTableColumns,
)


class TransactionTableModel(QAbstractTableModel):
    def __init__(
        self,
        view: QTableView,
        transactions: Collection[Transaction],
        base_currency: Currency,
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._view = view
        self.transactions = transactions
        self.base_currency = base_currency
        self._proxy = proxy

    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return self._transactions

    @transactions.setter
    def transactions(self, transactions: Collection[Transaction]) -> None:
        self._transactions = tuple(transactions)

    def rowCount(self, index: QModelIndex = ...) -> int:
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self.transactions)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: U100
        return 17

    def index(
        self, row: int, column: int, parent: QModelIndex = ...  # noqa: U100
    ) -> QModelIndex:
        if parent.isValid():
            return QModelIndex()
        if not QAbstractTableModel.hasIndex(self, row, column, QModelIndex()):
            return QModelIndex()

        item = self.transactions[row]
        return QAbstractTableModel.createIndex(self, row, column, item)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> Any:
        if not index.isValid():
            return None

        column = index.column()
        transaction = self.transactions[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return self.get_display_role_data(transaction, column)
        if role == Qt.ItemDataRole.DecorationRole:
            return self.get_decoration_role_data(transaction, column)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return TransactionTableModel.get_text_alignment_data(column)
        if role == Qt.ItemDataRole.ForegroundRole:
            return TransactionTableModel.get_foreground_data(transaction, column)
        if role == Qt.ItemDataRole.UserRole:
            return self.get_user_role_data(transaction, column)
        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return TRANSACTION_TABLE_COLUMN_HEADERS[section]
            return str(section)
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

    def pre_remove_item(self, item: Transaction) -> None:
        index = self.get_index_from_item(item)
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())

    def post_remove_item(self) -> None:
        self.endRemoveRows()

    def get_selected_item_index(self) -> QModelIndex:
        proxy_indexes = self._view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        if len(source_indexes) == 0:
            return QModelIndex()
        return source_indexes[0]

    def get_selected_item(self) -> Transaction | None:
        proxy_indexes = self._view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        if len(source_indexes) == 0:
            return None
        return source_indexes[0].internalPointer()

    def get_index_from_item(self, item: Transaction | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        row = self.transactions.index(item)
        return QAbstractTableModel.createIndex(self, row, 0, item)

    def get_display_role_data(
        self, transaction: Transaction, column: int
    ) -> str | None:
        if column == TransactionTableColumns.COLUMN_DATETIME:
            return transaction.datetime_.strftime("%d.%m.%Y %H:%M")
        if column == TransactionTableColumns.COLUMN_DESCRIPTION:
            return transaction.description
        if column == TransactionTableColumns.COLUMN_TYPE:
            return TransactionTableModel._get_transaction_type(transaction)
        if column == TransactionTableColumns.COLUMN_ACCOUNT:
            return TransactionTableModel._get_transaction_account(transaction)
        if column == TransactionTableColumns.COLUMN_SENDER:
            return TransactionTableModel._get_transfer_account(transaction, sender=True)
        if column == TransactionTableColumns.COLUMN_RECIPIENT:
            return TransactionTableModel._get_transfer_account(
                transaction, sender=False
            )
        if column == TransactionTableColumns.COLUMN_PAYEE:
            return TransactionTableModel._get_transaction_payee(transaction)
        if column == TransactionTableColumns.COLUMN_SECURITY:
            return TransactionTableModel._get_transaction_security(transaction)
        if column == TransactionTableColumns.COLUMN_SHARES:
            return TransactionTableModel._get_transaction_shares(transaction)
        if column == TransactionTableColumns.COLUMN_AMOUNT_NATIVE:
            return self._get_transaction_amount_string(transaction, base=False)
        if column == TransactionTableColumns.COLUMN_AMOUNT_BASE:
            return self._get_transaction_amount_string(transaction, base=True)
        if column == TransactionTableColumns.COLUMN_AMOUNT_SENT:
            return TransactionTableModel._get_transfer_amount_string(
                transaction, sent=True
            )
        if column == TransactionTableColumns.COLUMN_AMOUNT_RECEIVED:
            return TransactionTableModel._get_transfer_amount_string(
                transaction, sent=False
            )
        if column == TransactionTableColumns.COLUMN_BALANCE:
            return ""
        if column == TransactionTableColumns.COLUMN_CATEGORY:
            return TransactionTableModel._get_transaction_category(transaction)
        if column == TransactionTableColumns.COLUMN_TAG:
            return TransactionTableModel._get_transaction_tags(transaction)
        if column == TransactionTableColumns.COLUMN_UUID:
            return str(transaction.uuid)
        return None

    def get_decoration_role_data(
        self, transaction: Transaction, column: int
    ) -> QIcon | None:
        if column == TransactionTableColumns.COLUMN_TYPE:
            if isinstance(transaction, CashTransaction):
                if transaction.type_ == CashTransactionType.INCOME:
                    return QIcon("icons_custom:coins-plus.png")
                return QIcon("icons_custom:coins-minus.png")
            if isinstance(transaction, RefundTransaction):
                return QIcon("icons_custom:coins-arrow-back.png")
            if isinstance(transaction, CashTransfer):
                return QIcon("icons_custom:coins-arrow.png")
            if isinstance(transaction, SecurityTransaction):
                if transaction.type_ == SecurityTransactionType.BUY:
                    return QIcon("icons_custom:certificate-plus.png")
                return QIcon("icons_custom:certificate-minus.png")
            if isinstance(transaction, SecurityTransfer):
                return QIcon("icons_custom:certificate-arrow.png")
        return None

    def get_user_role_data(self, transaction: Transaction, column: int) -> Any:
        if column == TransactionTableColumns.COLUMN_DATETIME:
            return transaction.datetime_.timestamp()
        if column == TransactionTableColumns.COLUMN_SHARES:
            return TransactionTableModel._get_transaction_shares(transaction)
        if column == TransactionTableColumns.COLUMN_AMOUNT_NATIVE:
            return self._get_transaction_amount_value(transaction, base=False)
        if column == TransactionTableColumns.COLUMN_AMOUNT_BASE:
            return self._get_transaction_amount_value(transaction, base=True)
        if column == TransactionTableColumns.COLUMN_AMOUNT_SENT:
            return TransactionTableModel._get_transfer_amount_value(
                transaction, sent=True
            )
        if column == TransactionTableColumns.COLUMN_AMOUNT_RECEIVED:
            return TransactionTableModel._get_transfer_amount_value(
                transaction, sent=False
            )
        return unicodedata.normalize(
            "NFD", self.get_display_role_data(transaction, column)
        )

    @staticmethod
    def get_text_alignment_data(column: int) -> Qt.AlignmentFlag | None:
        if (
            column == TransactionTableColumns.COLUMN_AMOUNT_NATIVE
            or column == TransactionTableColumns.COLUMN_AMOUNT_BASE
            or column == TransactionTableColumns.COLUMN_AMOUNT_SENT
            or column == TransactionTableColumns.COLUMN_AMOUNT_RECEIVED
            or column == TransactionTableColumns.COLUMN_SHARES
        ):
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        return None

    @staticmethod
    def get_foreground_data(transaction: Transaction, column: int) -> QBrush | None:
        if (
            column == TransactionTableColumns.COLUMN_AMOUNT_NATIVE
            or column == TransactionTableColumns.COLUMN_AMOUNT_BASE
        ):
            if isinstance(transaction, CashTransaction):
                if transaction.type_ == CashTransactionType.INCOME:
                    return QBrush(QColor("green"))
                return QBrush(QColor("red"))
            if isinstance(transaction, RefundTransaction):
                return QBrush(QColor("green"))
            if isinstance(transaction, SecurityTransaction):
                if transaction.type_ == SecurityTransactionType.BUY:
                    return QBrush(QColor("red"))
                return QBrush(QColor("green"))
        if (
            column == TransactionTableColumns.COLUMN_AMOUNT_SENT
            or column == TransactionTableColumns.COLUMN_AMOUNT_RECEIVED
        ):
            return QBrush(QColor("blue"))
        if column == TransactionTableColumns.COLUMN_SHARES:
            if isinstance(transaction, SecurityTransaction):
                if transaction.type_ == SecurityTransactionType.BUY:
                    return QBrush(QColor("green"))
                return QBrush(QColor("red"))
            if isinstance(transaction, SecurityTransfer):
                return QBrush(QColor("blue"))
        return None

    @staticmethod
    def _get_transaction_type(transaction: Transaction) -> str:
        if isinstance(transaction, (CashTransaction, SecurityTransaction)):
            return transaction.type_.name.capitalize()
        if isinstance(transaction, CashTransfer):
            return "Cash Transfer"
        if isinstance(transaction, RefundTransaction):
            return "Refund"
        if isinstance(transaction, SecurityTransfer):
            return "Security Transfer"
        raise TypeError("Unexpected Transaction type.")

    @staticmethod
    def _get_transaction_account(transaction: Transaction) -> str:
        if isinstance(transaction, (CashTransaction, RefundTransaction)):
            return transaction.account.path
        return ""

    @staticmethod
    def _get_transfer_account(transaction: Transaction, sender: bool) -> str:
        if not isinstance(transaction, (CashTransfer, SecurityTransfer)):
            return ""
        if sender:
            return transaction.sender.path
        return transaction.recipient.path

    @staticmethod
    def _get_transaction_payee(transaction: Transaction) -> str:
        if isinstance(transaction, (CashTransaction, RefundTransaction)):
            return transaction.payee.name
        return ""

    @staticmethod
    def _get_transaction_security(transaction: Transaction) -> str:
        if isinstance(transaction, SecurityRelatedTransaction):
            if transaction.security.symbol:
                return transaction.security.symbol
            return transaction.security.name
        return ""

    @staticmethod
    def _get_transaction_shares(transaction: Transaction) -> str:
        if isinstance(transaction, SecurityTransaction):
            return str(transaction.get_shares(transaction.security_account))
        if isinstance(transaction, SecurityTransfer):
            return str(transaction.get_shares(transaction.recipient))
        return ""

    def _get_transaction_amount_string(
        self, transaction: Transaction, base: bool
    ) -> str:
        amount = None
        if isinstance(transaction, (CashTransaction, RefundTransaction)):
            amount = transaction.get_amount(transaction.account)
        if isinstance(transaction, SecurityTransaction):
            amount = transaction.get_amount(transaction.cash_account)

        if amount is None:
            return ""

        if base:
            return amount.convert(self.base_currency).to_str_rounded()
        return amount.to_str_rounded()

    def _get_transaction_amount_value(
        self, transaction: Transaction, base: bool
    ) -> float:
        amount = None
        if isinstance(transaction, (CashTransaction, RefundTransaction)):
            amount = transaction.get_amount(transaction.account)
        if isinstance(transaction, SecurityTransaction):
            amount = transaction.get_amount(transaction.cash_account)

        if amount is None:
            return float("-inf")

        if base:
            return float(amount.convert(self.base_currency).value_rounded)
        return float(amount.value_rounded)

    @staticmethod
    def _get_transfer_amount_string(transaction: Transaction, sent: bool) -> str:
        if not isinstance(transaction, CashTransfer):
            return ""

        if sent:
            return transaction.get_amount(transaction.sender).to_str_rounded()
        return transaction.get_amount(transaction.recipient).to_str_rounded()

    @staticmethod
    def _get_transfer_amount_value(transaction: Transaction, sent: bool) -> float:
        if not isinstance(transaction, CashTransfer):
            return float("-inf")

        if sent:
            return float(transaction.get_amount(transaction.sender).value_rounded)
        return float(transaction.get_amount(transaction.recipient).value_rounded)

    @staticmethod
    def _get_transaction_category(transaction: Transaction) -> str:
        if isinstance(transaction, (CashTransaction, RefundTransaction)):
            category_paths = [category.path for category in transaction.categories]
            return ", ".join(category_paths)
        return ""

    @staticmethod
    def _get_transaction_tags(transaction: Transaction) -> str:
        tag_names = [tag.name for tag in transaction.tags]
        return ", ".join(tag_names)
