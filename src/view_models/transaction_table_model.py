import unicodedata
from collections.abc import Collection, Sequence
from decimal import Decimal
from uuid import UUID

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush, QIcon
from PyQt6.QtWidgets import QTableView
from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import Category
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashRelatedTransaction,
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import (
    CashAmount,
    ConversionFactorNotFoundError,
    Currency,
)
from src.models.model_objects.security_objects import (
    SecurityRelatedTransaction,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
)
from src.models.user_settings import user_settings
from src.utilities.formatting import convert_decimal_to_string, format_percentage
from src.views import colors, icons
from src.views.constants import (
    TRANSACTION_TABLE_COLUMN_HEADERS,
    TransactionTableColumn,
    monospace_font,
)

ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

COLUMNS_ALIGNED_RIGHT = {
    TransactionTableColumn.AMOUNT_NATIVE,
    TransactionTableColumn.AMOUNT_BASE,
    TransactionTableColumn.AMOUNT_SENT,
    TransactionTableColumn.AMOUNT_RECEIVED,
    TransactionTableColumn.SHARES,
    TransactionTableColumn.AMOUNT_PER_SHARE,
    TransactionTableColumn.BALANCE,
}
COLUMNS_TRANSACTION_AMOUNTS = {
    TransactionTableColumn.AMOUNT_NATIVE,
    TransactionTableColumn.AMOUNT_BASE,
}
COLUMNS_TRANSFER_AMOUNTS = {
    TransactionTableColumn.AMOUNT_SENT,
    TransactionTableColumn.AMOUNT_RECEIVED,
}
SHARES_SIGNIFICANT_DIGITS = 4


class TransactionTableModel(QAbstractTableModel):
    def __init__(
        self,
        view: QTableView,
        proxy_viewside: QSortFilterProxyModel,
        proxy_sourceside: QSortFilterProxyModel | None,
    ) -> None:
        super().__init__()
        self._view = view
        self._proxy_viewside = proxy_viewside
        self._proxy_sourceside = proxy_sourceside

        self._transaction_uuid_dict: dict[UUID, Transaction] = {}
        self._transactions: tuple[Transaction] = ()
        self._row_count = 0
        self._base_currency: Currency | None = None
        self._valid_accounts = ()

    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return self._transactions

    @property
    def base_currency(self) -> Currency:
        return self._base_currency

    @base_currency.setter
    def base_currency(self, currency: Currency) -> None:
        self._base_currency = currency

    @property
    def transaction_uuid_dict(self) -> dict[UUID, Transaction]:
        return self._transaction_uuid_dict

    @property
    def valid_accounts(self) -> tuple[Account]:
        return self._valid_accounts

    @valid_accounts.setter
    def valid_accounts(self, accounts: Collection[Account]) -> None:
        self._valid_accounts = tuple(accounts)

    # FIXME: it feels hacky to rely on transactions being pre-sorted descending
    def load_data(
        self,
        transactions: Collection[Transaction],
        transaction_uuid_dict: dict[UUID, Transaction],
        base_currency: Currency | None,
    ) -> None:
        """Transactions should be sorted in descending manner upon initial load!"""

        self._base_currency = base_currency
        self._transactions = tuple(transactions)
        self._transaction_uuid_dict = transaction_uuid_dict
        self._row_count = len(self._transactions)

    def rowCount(self, index: QModelIndex = ...) -> int:
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return self._row_count

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(TRANSACTION_TABLE_COLUMN_HEADERS)
        return self._column_count

    def data(  # noqa: PLR0911
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | float | QIcon | Qt.AlignmentFlag | QBrush | None:
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(
                self._transactions[index.row()], index.column()
            )
        if role == Qt.ItemDataRole.UserRole:
            return self._get_user_role_data(
                self._transactions[index.row()], index.column()
            )
        if role == Qt.ItemDataRole.DecorationRole:
            return self._get_decoration_role_data(
                self._transactions[index.row()], index.column()
            )
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return TransactionTableModel._get_text_alignment_role_data(index.column())
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(
                self._transactions[index.row()], index.column()
            )
        if (
            role == Qt.ItemDataRole.FontRole
            and index.column() == TransactionTableColumn.UUID
        ):
            return monospace_font
        if role == Qt.ItemDataRole.ToolTipRole:
            return self._get_tooltip_role_data(
                self._transactions[index.row()], index.column()
            )
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
        self._view.setSortingEnabled(False)
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

    def post_add(self) -> None:
        self.endInsertRows()
        self._view.setSortingEnabled(True)

    def pre_reset_model(self) -> None:
        if self._proxy_sourceside is not None:
            self._proxy_sourceside.setDynamicSortFilter(False)

        self._proxy_viewside.setDynamicSortFilter(False)

        # this effectively turns off sorting and dramatically decreases calls
        # to data() for sorting purposes during file load
        self._proxy_viewside.sort(-1)

        self.beginResetModel()

    def post_reset_model(
        self,
        sort_column: int = 0,
        sort_order: Qt.SortOrder = Qt.SortOrder.DescendingOrder,
    ) -> None:
        self.endResetModel()

        if self._proxy_sourceside is not None:
            self._proxy_sourceside.setDynamicSortFilter(True)

        self._proxy_viewside.setDynamicSortFilter(True)
        # this slows down file load but enables dynamic sort filter
        self._view.sortByColumn(sort_column, sort_order)

    def pre_remove_item(self, item: Transaction) -> None:
        index = self.get_index_from_item(item)
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())

    def post_remove_item(self) -> None:
        self.endRemoveRows()

    def get_selected_items(self) -> tuple[Transaction, ...]:
        indexes = self._view.selectedIndexes()
        indexes = [self._proxy_viewside.mapToSource(index) for index in indexes]
        if self._proxy_sourceside is not None:
            indexes = [self._proxy_sourceside.mapToSource(index) for index in indexes]
        return tuple(
            self._transactions[index.row()] for index in indexes if index.column() == 0
        )

    def get_visible_items(self) -> tuple[Transaction, ...]:
        items: list[Transaction] = []
        for row in range(self._view.model().rowCount()):
            index = self._proxy_viewside.index(row, 0)
            index = self._proxy_viewside.mapToSource(index)
            if self._proxy_sourceside is not None:
                index = self._proxy_sourceside.mapToSource(index)
            items.append(self._transactions[index.row()])
        return tuple(items)

    def get_index_from_item(self, item: Transaction | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        row = self._transactions.index(item)
        return QAbstractTableModel.createIndex(self, row, 0)

    def _get_display_role_data(  # noqa: PLR0911, PLR0912, C901
        self, transaction: Transaction, column: int
    ) -> str | None:
        if column == TransactionTableColumn.DATETIME:
            return transaction.datetime_.strftime(
                user_settings.settings.transaction_date_format
            )
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
            return TransactionTableModel._get_transaction_shares_string(transaction)
        if column == TransactionTableColumn.AMOUNT_PER_SHARE:
            return TransactionTableModel._get_transaction_amount_per_share_string(
                transaction
            )
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
            return self._get_account_balance_string(transaction)
        if column == TransactionTableColumn.CATEGORY:
            return TransactionTableModel._get_transaction_category(transaction)
        if column == TransactionTableColumn.TAG:
            return TransactionTableModel._get_transaction_tags(transaction)
        if column == TransactionTableColumn.UUID:
            return str(transaction.uuid)
        if column == TransactionTableColumn.DATETIME_CREATED:
            return transaction.datetime_created.strftime("%Y-%m-%d %H:%M:%S")
        return None

    def _get_decoration_role_data(  # noqa: PLR0911, PLR0912, C901
        self, transaction: Transaction, column: int
    ) -> QIcon | None:
        if column == TransactionTableColumn.TYPE:
            if isinstance(transaction, CashTransaction):
                if transaction.type_ == CashTransactionType.INCOME:
                    return icons.income
                return icons.expense
            if isinstance(transaction, RefundTransaction):
                return icons.refund
            if isinstance(transaction, CashTransfer):
                return icons.cash_transfer
            if isinstance(transaction, SecurityTransaction):
                if transaction.type_ == SecurityTransactionType.BUY:
                    return icons.buy
                if transaction.type_ == SecurityTransactionType.SELL:
                    return icons.sell
                return icons.dividend
            if isinstance(transaction, SecurityTransfer):
                return icons.security_transfer
        if column == TransactionTableColumn.FROM:
            if isinstance(transaction, CashTransaction):
                if transaction.type_ == CashTransactionType.INCOME:
                    return icons.payee
                return icons.cash_account
            if isinstance(transaction, RefundTransaction):
                return icons.payee
            if isinstance(transaction, SecurityTransaction):
                if transaction.type_ == SecurityTransactionType.BUY:
                    return icons.cash_account
                return icons.security_account
            if isinstance(transaction, CashTransfer):
                return icons.cash_account
            if isinstance(transaction, SecurityTransfer):
                return icons.security_account
        if column == TransactionTableColumn.TO:
            if isinstance(transaction, CashTransaction):
                if transaction.type_ == CashTransactionType.INCOME:
                    return icons.cash_account
                return icons.payee
            if isinstance(transaction, RefundTransaction):
                return icons.cash_account
            if isinstance(transaction, SecurityTransaction):
                if transaction.type_ == SecurityTransactionType.BUY:
                    return icons.security_account
                return icons.cash_account
            if isinstance(transaction, CashTransfer):
                return icons.cash_account
            if isinstance(transaction, SecurityTransfer):
                return icons.security_account
        if (
            column == TransactionTableColumn.CATEGORY
            and isinstance(transaction, CashTransaction | RefundTransaction)
            and transaction.are_categories_split
        ):
            return icons.split_attribute
        if (
            column == TransactionTableColumn.TAG
            and isinstance(transaction, CashTransaction | RefundTransaction)
            and transaction.are_tags_split
        ):
            return icons.split_attribute
        return None

    def _get_user_role_data(  # noqa: PLR0911
        self, transaction: Transaction, column: int
    ) -> float | str:
        if column == TransactionTableColumn.DATETIME:
            return transaction.timestamp
        if column == TransactionTableColumn.SHARES:
            shares = TransactionTableModel._get_transaction_shares(transaction)
            return float(shares) if shares else float("-inf")
        if column == TransactionTableColumn.AMOUNT_PER_SHARE:
            amount_per_share = TransactionTableModel._get_transaction_amount_per_share(
                transaction
            )
            return float(amount_per_share) if amount_per_share else float("-inf")
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
        if column == TransactionTableColumn.DATETIME_CREATED:
            return transaction.datetime_created.timestamp()
        if column == TransactionTableColumn.BALANCE:
            balance = self._get_account_balance(transaction)
            return float(balance.value_normalized)
        return unicodedata.normalize(
            "NFD", self._get_display_role_data(transaction, column)
        )

    def _get_tooltip_role_data(
        self, transaction: Transaction, column: int
    ) -> float | str:
        if column == TransactionTableColumn.DESCRIPTION:
            return transaction.description
        if column == TransactionTableColumn.SHARES:
            shares = TransactionTableModel._get_transaction_shares(transaction)
            return f"{shares:n}"
        if column == TransactionTableColumn.AMOUNT_PER_SHARE:
            return TransactionTableModel._get_transaction_amount_per_share_tooltip(
                transaction
            )
        return None

    @staticmethod
    def _get_text_alignment_role_data(column: int) -> Qt.AlignmentFlag | None:
        if column in COLUMNS_ALIGNED_RIGHT:
            return ALIGNMENT_RIGHT
        return None

    def _get_foreground_role_data(  # noqa: PLR0911, C901, PLR0912
        self, transaction: Transaction, column: int
    ) -> QBrush | None:
        if column in COLUMNS_TRANSACTION_AMOUNTS:
            if isinstance(transaction, CashTransaction):
                if transaction.type_ == CashTransactionType.INCOME:
                    return colors.get_green_brush()
                return colors.get_red_brush()
            if isinstance(transaction, RefundTransaction):
                return colors.get_green_brush()
            if isinstance(transaction, SecurityTransaction):
                if transaction.type_ == SecurityTransactionType.BUY:
                    return colors.get_red_brush()
                return colors.get_green_brush()
        if column in COLUMNS_TRANSFER_AMOUNTS:
            return colors.get_blue_brush()
        if column == TransactionTableColumn.SHARES:
            if isinstance(transaction, SecurityTransaction):
                if transaction.type_ == SecurityTransactionType.BUY:
                    return colors.get_green_brush()
                if transaction.type_ == SecurityTransactionType.SELL:
                    return colors.get_red_brush()
                return None
            if isinstance(transaction, SecurityTransfer):
                return colors.get_blue_brush()
        if column == TransactionTableColumn.BALANCE:
            balance = self._get_account_balance(transaction)
            if not balance.is_finite():
                return None
            if balance.value_rounded < 0:
                return colors.get_red_brush()
            if balance.value_rounded > 0:
                return None
            return colors.get_gray_brush()
        return None

    @staticmethod
    def _get_transaction_type(transaction: Transaction) -> str:
        if isinstance(transaction, CashTransaction):
            if (
                transaction.type_ == CashTransactionType.EXPENSE
                and transaction.is_refunded
            ):
                refunded_ratio = transaction.refunded_ratio
                return (
                    f"Expense ({format_percentage(100*refunded_ratio,decimals=0)} "
                    "Refunded)"
                )
            return transaction.type_.name.capitalize()
        if isinstance(transaction, SecurityTransaction):
            return transaction.type_.name.capitalize()
        if isinstance(transaction, CashTransfer):
            return "Cash Transfer"
        if isinstance(transaction, RefundTransaction):
            return (
                f"Refund ({format_percentage(100*transaction.refund_ratio,decimals=0)})"
            )
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
    def _get_transaction_shares(transaction: Transaction) -> Decimal:
        if isinstance(transaction, SecurityTransaction):
            return transaction.get_shares()
        if isinstance(transaction, SecurityTransfer):
            return transaction.get_shares()
        return Decimal("NaN")

    @staticmethod
    def _get_transaction_shares_string(transaction: Transaction) -> str:
        if not isinstance(transaction, (SecurityTransaction, SecurityTransfer)):
            return ""
        if isinstance(transaction, SecurityTransaction):
            shares = transaction.get_shares()
        else:
            shares = transaction.get_shares()

        return convert_decimal_to_string(shares)

    @staticmethod
    def _get_transaction_amount_per_share(transaction: Transaction) -> Decimal:
        if isinstance(transaction, SecurityTransaction):
            return transaction.amount_per_share.value_normalized
        return Decimal("NaN")

    @staticmethod
    def _get_transaction_amount_per_share_string(transaction: Transaction) -> str:
        if isinstance(transaction, SecurityTransaction):
            return (
                convert_decimal_to_string(
                    transaction.amount_per_share.value_normalized,
                    min_decimals=transaction.security.price_decimals,
                    significant_digits=transaction.security.price_decimals,
                )
                + " "
                + transaction.currency.code
            )
        return ""

    @staticmethod
    def _get_transaction_amount_per_share_tooltip(transaction: Transaction) -> str:
        if isinstance(transaction, SecurityTransaction):
            return transaction.amount_per_share.to_str_normalized()
        return ""

    def _get_transaction_amount_string(
        self, transaction: Transaction, *, base: bool
    ) -> str:
        try:
            amount: CashAmount = transaction.get_amount()
        except Exception:  # noqa: BLE001
            return ""  # probably a CashTransfer or SecurityTransfer

        if base:
            try:
                return amount.convert(
                    self._base_currency, transaction.date_
                ).to_str_rounded()
            except ConversionFactorNotFoundError:
                return "Error!"
        elif amount.currency == self._base_currency:
            return ""
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
            return float(
                amount.convert(self._base_currency, transaction.date_).value_rounded
            )
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
            if not transaction.are_categories_split:
                return transaction.category_amount_pairs[0][0].path
            return _get_split_category_string(transaction.category_amount_pairs)
        return ""

    @staticmethod
    def _get_transaction_tags(transaction: Transaction) -> str:
        if isinstance(transaction, CashTransaction | RefundTransaction):
            if transaction.are_tags_split:
                tag_names: list[str] = []
                for tag, amount in transaction.tag_amount_pairs:
                    if amount != transaction.amount:
                        tag_names.append(f"{tag.name} ({amount.to_str_rounded()})")
                    else:
                        tag_names.append(tag.name)
                tag_names = sorted(tag_name for tag_name in tag_names)
            else:
                tag_names = sorted(tag.name for tag in transaction.tags)
        else:
            tag_names = sorted(tag.name for tag in transaction.tags)
        return ", ".join(tag_names)

    def _get_account_balance(self, transaction: Transaction) -> CashAmount:
        if (
            isinstance(transaction, CashRelatedTransaction)
            and len(self._valid_accounts) == 1
        ):
            account = self._valid_accounts[0]
            if isinstance(account, CashAccount) and transaction.is_account_related(
                account
            ):
                return account.get_balance_after_transaction(
                    account.currency, transaction
                )
            return CashAmount("-inf", self._base_currency)
        return CashAmount("-inf", self._base_currency)

    def _get_account_balance_string(self, transaction: Transaction) -> str:
        if (
            isinstance(transaction, CashRelatedTransaction)
            and len(self._valid_accounts) == 1
        ):
            account = self._valid_accounts[0]
            if isinstance(account, CashAccount) and transaction.is_account_related(
                account
            ):
                balance = account.get_balance_after_transaction(
                    account.currency, transaction
                )
                return balance.to_str_rounded()
            return ""
        return ""

    def emit_data_changed_for_uuids(self, uuids: Collection[UUID]) -> None:
        for uuid_ in uuids:
            item = self._transaction_uuid_dict[uuid_]
            index = self.get_index_from_item(item)
            self.dataChanged.emit(index, index)


def _get_split_category_string(
    category_amount_pairs: Sequence[tuple[Category, CashAmount]],
) -> str:
    remaining_pairs = list(category_amount_pairs)
    grouped_pairs: list[list[tuple[Category, CashAmount]]] = []

    while remaining_pairs:
        pair = remaining_pairs.pop(0)
        group = [pair] + [
            _pair
            for _pair in remaining_pairs
            if pair[0].parent == _pair[0].parent and pair[0].parent is not None
        ]
        remaining_pairs = [p for p in remaining_pairs if p not in group]
        grouped_pairs.append(group)

    strings = []
    for group in grouped_pairs:
        if len(group) == 1:
            strings.append(f"{group[0][0].path} ({group[0][1].to_str_rounded()})")
        else:
            string_inner = [f"{p[0].name} ({p[1].to_str_rounded()})" for p in group]
            string = f"{group[0][0].parent.path}/[{' + '.join(string_inner)}]"
            strings.append(string)

    return ", ".join(strings)
