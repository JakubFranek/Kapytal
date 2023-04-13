import unicodedata
from collections.abc import Collection

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush, QColor, QIcon
from PyQt6.QtWidgets import QTableView
from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashRelatedTransaction,
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import (
    ConversionFactorNotFoundError,
    Currency,
)
from src.models.model_objects.security_objects import (
    SecurityRelatedTransaction,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
)
from src.views.constants import TRANSACTION_TABLE_COLUMN_HEADERS, TransactionTableColumn

# TODO: look into overriding "multidata" method to improve performance


class TransactionTableModel(QAbstractTableModel):
    def __init__(  # noqa: PLR0913
        self,
        view: QTableView,
        transactions: Collection[Transaction],
        base_currency: Currency,
        valid_accounts: Collection[Account],
        proxy_viewside: QSortFilterProxyModel,
        proxy_sourceside: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._view = view
        self.transactions = transactions
        self.base_currency = base_currency
        self.valid_accounts = valid_accounts
        self._proxy_viewside = proxy_viewside
        self._proxy_sourceside = proxy_sourceside

    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return self._transactions

    @transactions.setter
    def transactions(self, transactions: Collection[Transaction]) -> None:
        self._transactions = tuple(transactions)

    @property
    def valid_accounts(self) -> tuple[Account]:
        return self._valid_accounts

    @valid_accounts.setter
    def valid_accounts(self, accounts: Collection[Account]) -> None:
        self._valid_accounts = tuple(accounts)

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self.transactions)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        del index
        return 15

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        if parent.isValid():
            return QModelIndex()
        if not QAbstractTableModel.hasIndex(self, row, column, QModelIndex()):
            return QModelIndex()

        item = self.transactions[row]
        return QAbstractTableModel.createIndex(self, row, column, item)

    def data(  # noqa: PLR0911
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | float | QIcon | Qt.AlignmentFlag | QBrush | None:
        if not index.isValid():
            return None

        column = index.column()
        transaction = self.transactions[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(transaction, column)
        if role == Qt.ItemDataRole.DecorationRole:
            return self._get_decoration_role_data(transaction, column)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return TransactionTableModel.get_text_alignment_data(column)
        if role == Qt.ItemDataRole.ForegroundRole:
            return TransactionTableModel._get_foreground_data(transaction, column)
        if role == Qt.ItemDataRole.UserRole:
            return self._get_user_role_data(transaction, column)
        return None

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return TRANSACTION_TABLE_COLUMN_HEADERS[section]
            return str(section)
        return None

    def pre_add(self) -> None:
        self._proxy_viewside.setDynamicSortFilter(False)  # noqa: FBT003
        self._view.setSortingEnabled(False)  # noqa: FBT003
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

    def post_add(self) -> None:
        self.endInsertRows()
        self._view.setSortingEnabled(True)  # noqa: FBT003
        self._proxy_viewside.setDynamicSortFilter(True)  # noqa: FBT003

    def pre_reset_model(self) -> None:
        self._view.setSortingEnabled(False)  # noqa: FBT003
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()
        self._view.setSortingEnabled(True)  # noqa: FBT003

    def pre_remove_item(self, item: Transaction) -> None:
        index = self.get_index_from_item(item)
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())

    def post_remove_item(self) -> None:
        self.endRemoveRows()

    def get_selected_items(self) -> tuple[Transaction, ...]:
        proxy_viewside_indexes = self._view.selectedIndexes()
        proxy_sourceside_indexes = [
            self._proxy_viewside.mapToSource(index) for index in proxy_viewside_indexes
        ]
        source_indexes = [
            self._proxy_sourceside.mapToSource(index)
            for index in proxy_sourceside_indexes
        ]
        return tuple(
            index.internalPointer() for index in source_indexes if index.column() == 0
        )

    def get_visible_items(self) -> tuple[Transaction, ...]:
        viewside_rows = self._proxy_viewside.rowCount()
        proxy_viewside_indexes = [
            self._proxy_viewside.index(row, 0) for row in range(viewside_rows)
        ]
        proxy_sourceside_indexes = [
            self._proxy_viewside.mapToSource(index) for index in proxy_viewside_indexes
        ]
        source_indexes = [
            self._proxy_sourceside.mapToSource(index)
            for index in proxy_sourceside_indexes
        ]
        return tuple(index.internalPointer() for index in source_indexes)

    def get_index_from_item(self, item: Transaction | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        row = self.transactions.index(item)
        return QAbstractTableModel.createIndex(self, row, 0, item)

    def _get_display_role_data(  # noqa: PLR0911, PLR0912, C901
        self, transaction: Transaction, column: int
    ) -> str | None:
        if column == TransactionTableColumn.DATETIME:
            return transaction.datetime_.strftime("%d.%m.%Y")
        if column == TransactionTableColumn.DESCRIPTION:
            return transaction.description
        if column == TransactionTableColumn.TYPE:
            return TransactionTableModel._get_transaction_type(transaction)
        if column == TransactionTableColumn.FROM:
            if isinstance(transaction, CashTransaction):
                if transaction.type_ == CashTransactionType.INCOME:
                    return transaction.payee.name
                return transaction.account.path
            if isinstance(transaction, RefundTransaction):
                return transaction.payee.name
            if isinstance(transaction, SecurityTransaction):
                if transaction.type_ == SecurityTransactionType.BUY:
                    return transaction.cash_account.path
                return transaction.security_account.path
            if isinstance(transaction, CashTransfer | SecurityTransfer):
                return transaction.sender.path
        if column == TransactionTableColumn.TO:
            if isinstance(transaction, CashTransaction):
                if transaction.type_ == CashTransactionType.INCOME:
                    return transaction.account.path
                return transaction.payee.name
            if isinstance(transaction, RefundTransaction):
                return transaction.account.path
            if isinstance(transaction, SecurityTransaction):
                if transaction.type_ == SecurityTransactionType.BUY:
                    return transaction.security_account.path
                return transaction.cash_account.path
            if isinstance(transaction, CashTransfer | SecurityTransfer):
                return transaction.recipient.path
        if column == TransactionTableColumn.SECURITY:
            return TransactionTableModel._get_transaction_security(transaction)
        if column == TransactionTableColumn.SHARES:
            return TransactionTableModel._get_transaction_shares(transaction)
        if column == TransactionTableColumn.AMOUNT_NATIVE:
            return self._get_transaction_amount_string(transaction, base=False)
        if column == TransactionTableColumn.AMOUNT_BASE:
            return self._get_transaction_amount_string(transaction, base=True)
        if column == TransactionTableColumn.AMOUNT_SENT:
            return TransactionTableModel._get_transfer_amount_string(
                transaction, sent=True
            )
        if column == TransactionTableColumn.AMOUNT_RECEIVED:
            return TransactionTableModel._get_transfer_amount_string(
                transaction, sent=False
            )
        if column == TransactionTableColumn.BALANCE:
            return self._get_account_balance(transaction)
        if column == TransactionTableColumn.CATEGORY:
            return TransactionTableModel._get_transaction_category(transaction)
        if column == TransactionTableColumn.TAG:
            return TransactionTableModel._get_transaction_tags(transaction)
        if column == TransactionTableColumn.UUID:
            return str(transaction.uuid)
        return None

    def _get_decoration_role_data(  # noqa: PLR0911, PLR0912, C901
        self, transaction: Transaction, column: int
    ) -> QIcon | None:
        if column == TransactionTableColumn.TYPE:
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
        if column == TransactionTableColumn.FROM:
            if isinstance(transaction, CashTransaction):
                if transaction.type_ == CashTransactionType.INCOME:
                    return QIcon("icons_16:user-business.png")
                return QIcon("icons_16:piggy-bank.png")
            if isinstance(transaction, RefundTransaction):
                return QIcon("icons_16:user-business.png")
            if isinstance(transaction, SecurityTransaction):
                if transaction.type_ == SecurityTransactionType.BUY:
                    return QIcon("icons_16:piggy-bank.png")
                return QIcon("icons_16:bank.png")
            if isinstance(transaction, CashTransfer):
                return QIcon("icons_16:piggy-bank.png")
            if isinstance(transaction, SecurityTransfer):
                return QIcon("icons_16:bank.png")
        if column == TransactionTableColumn.TO:
            if isinstance(transaction, CashTransaction):
                if transaction.type_ == CashTransactionType.INCOME:
                    return QIcon("icons_16:piggy-bank.png")
                return QIcon("icons_16:user-business.png")
            if isinstance(transaction, RefundTransaction):
                return QIcon("icons_16:piggy-bank.png")
            if isinstance(transaction, SecurityTransaction):
                if transaction.type_ == SecurityTransactionType.BUY:
                    return QIcon("icons_16:bank.png")
                return QIcon("icons_16:piggy-bank.png")
            if isinstance(transaction, CashTransfer):
                return QIcon("icons_16:piggy-bank.png")
            if isinstance(transaction, SecurityTransfer):
                return QIcon("icons_16:bank.png")
        if (
            column == TransactionTableColumn.CATEGORY
            and isinstance(transaction, CashTransaction)
            and transaction.are_categories_split
        ):
            return QIcon("icons_16:arrow-split.png")
        if (
            column == TransactionTableColumn.TAG
            and isinstance(transaction, CashTransaction)
            and transaction.are_tags_split
        ):
            return QIcon("icons_16:arrow-split.png")
        return None

    def _get_user_role_data(  # noqa: PLR0911
        self, transaction: Transaction, column: int
    ) -> float | str:
        if column == TransactionTableColumn.DATETIME:
            return transaction.datetime_.timestamp()
        if column == TransactionTableColumn.SHARES:
            return TransactionTableModel._get_transaction_shares(transaction)
        if column == TransactionTableColumn.AMOUNT_NATIVE:
            return self._get_transaction_amount_value(transaction, base=False)
        if column == TransactionTableColumn.AMOUNT_BASE:
            return self._get_transaction_amount_value(transaction, base=True)
        if column == TransactionTableColumn.AMOUNT_SENT:
            return TransactionTableModel._get_transfer_amount_value(
                transaction, sent=True
            )
        if column == TransactionTableColumn.AMOUNT_RECEIVED:
            return TransactionTableModel._get_transfer_amount_value(
                transaction, sent=False
            )
        return unicodedata.normalize(
            "NFD", self._get_display_role_data(transaction, column)
        )

    @staticmethod
    def get_text_alignment_data(column: int) -> Qt.AlignmentFlag | None:
        if (
            column == TransactionTableColumn.AMOUNT_NATIVE
            or column == TransactionTableColumn.AMOUNT_BASE
            or column == TransactionTableColumn.AMOUNT_SENT
            or column == TransactionTableColumn.AMOUNT_RECEIVED
            or column == TransactionTableColumn.SHARES
            or column == TransactionTableColumn.BALANCE
        ):
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        return None

    @staticmethod
    def _get_foreground_data(  # noqa: PLR0911, C901
        transaction: Transaction, column: int
    ) -> QBrush | None:
        if (
            column == TransactionTableColumn.AMOUNT_NATIVE
            or column == TransactionTableColumn.AMOUNT_BASE
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
            column == TransactionTableColumn.AMOUNT_SENT
            or column == TransactionTableColumn.AMOUNT_RECEIVED
        ):
            return QBrush(QColor("blue"))
        if column == TransactionTableColumn.SHARES:
            if isinstance(transaction, SecurityTransaction):
                if transaction.type_ == SecurityTransactionType.BUY:
                    return QBrush(QColor("green"))
                return QBrush(QColor("red"))
            if isinstance(transaction, SecurityTransfer):
                return QBrush(QColor("blue"))
        return None

    @staticmethod
    def _get_transaction_type(transaction: Transaction) -> str:
        if isinstance(transaction, CashTransaction):
            if (
                transaction.type_ == CashTransactionType.EXPENSE
                and transaction.is_refunded
            ):
                return transaction.type_.name.capitalize() + " (Refunded)"
            return transaction.type_.name.capitalize()
        if isinstance(transaction, SecurityTransaction):
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
        if isinstance(transaction, CashTransaction | RefundTransaction):
            return transaction.account.path
        return ""

    @staticmethod
    def _get_transfer_account(transaction: Transaction, *, sender: bool) -> str:
        if not isinstance(transaction, CashTransfer | SecurityTransfer):
            return ""
        if sender:
            return transaction.sender.path
        return transaction.recipient.path

    @staticmethod
    def _get_transaction_payee(transaction: Transaction) -> str:
        if isinstance(transaction, CashTransaction | RefundTransaction):
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
        self, transaction: Transaction, *, base: bool
    ) -> str:
        amount = None
        if isinstance(transaction, CashTransaction | RefundTransaction):
            amount = transaction.get_amount(transaction.account)
        if isinstance(transaction, SecurityTransaction):
            amount = transaction.get_amount(transaction.cash_account)

        if amount is None:
            return ""

        if base:
            try:
                return amount.convert(self.base_currency).to_str_rounded()
            except ConversionFactorNotFoundError:
                return "Error!"
        return amount.to_str_rounded()

    def _get_transaction_amount_value(
        self, transaction: Transaction, *, base: bool
    ) -> float:
        amount = None
        if isinstance(transaction, CashTransaction | RefundTransaction):
            amount = transaction.get_amount(transaction.account)
        if isinstance(transaction, SecurityTransaction):
            amount = transaction.get_amount(transaction.cash_account)

        if amount is None:
            return float("-inf")

        if base:
            return float(amount.convert(self.base_currency).value_rounded)
        return float(amount.value_rounded)

    @staticmethod
    def _get_transfer_amount_string(transaction: Transaction, *, sent: bool) -> str:
        if not isinstance(transaction, CashTransfer):
            return ""

        if sent:
            return transaction.get_amount(transaction.sender).to_str_rounded()
        return transaction.get_amount(transaction.recipient).to_str_rounded()

    @staticmethod
    def _get_transfer_amount_value(transaction: Transaction, *, sent: bool) -> float:
        if not isinstance(transaction, CashTransfer):
            return float("-inf")

        if sent:
            return float(transaction.get_amount(transaction.sender).value_rounded)
        return float(transaction.get_amount(transaction.recipient).value_rounded)

    @staticmethod
    def _get_transaction_category(transaction: Transaction) -> str:
        if isinstance(transaction, CashTransaction | RefundTransaction):
            category_paths = [category.path for category in transaction.categories]
            return ", ".join(category_paths)
        return ""

    @staticmethod
    def _get_transaction_tags(transaction: Transaction) -> str:
        tag_names = [tag.name for tag in transaction.tags]
        return ", ".join(tag_names)

    def _get_account_balance(self, transaction: Transaction) -> str:
        if (
            isinstance(transaction, CashRelatedTransaction)
            and len(self.valid_accounts) == 1
        ):
            account = self.valid_accounts[0]
            if not isinstance(account, CashAccount):
                raise TypeError(f"Expected CashAccount, got {type(account)}.")
            if transaction.is_account_related(account):
                balance = account.get_balance_after_transaction(
                    account.currency, transaction
                )
                return balance.to_str_rounded()
            return ""
        return ""
