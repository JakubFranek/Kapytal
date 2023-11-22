import unicodedata
from collections.abc import Collection, Sequence
from decimal import Decimal
from typing import Self

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush, QFont
from PyQt6.QtWidgets import QTreeView
from src.models.custom_exceptions import InvalidOperationError
from src.models.model_objects.attributes import Category
from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.model_objects.currency_objects import Currency
from src.models.statistics.category_stats import CategoryStats, TransactionBalance
from src.views import colors

overline_font = QFont()
overline_font.setOverline(True)  # noqa: FBT003
bold_font = QFont()
bold_font.setBold(True)  # noqa: FBT003
overline_bold_font = QFont()
overline_bold_font.setOverline(True)  # noqa: FBT003
overline_bold_font.setBold(True)  # noqa: FBT003

ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
ALIGNMENT_CENTER = Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
ALIGNMENT_LEFT = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter


class RowObject:
    def __init__(
        self,
        name: str,
        path: str,
        amounts: Sequence[Decimal],
        transactions: Sequence[Sequence[CashTransaction | RefundTransaction]],
        parent: Self | None,
    ) -> None:
        self.name = name
        self.path = path
        self.data = tuple(amounts)
        self.transactions: tuple[
            tuple[CashTransaction | RefundTransaction, ...], ...
        ] = tuple(tuple(transaction_sequence) for transaction_sequence in transactions)
        self.parent = parent
        self.children: list[Self] = []

    def __repr__(self) -> str:
        return f"RowObject({self.name})"


class PeriodicCategoryStatsTreeModel(QAbstractItemModel):
    def __init__(
        self,
        view: QTreeView,
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._view = view
        self._proxy = proxy

    def load_periodic_category_stats(
        self,
        periodic_stats: dict[str, tuple[CategoryStats]],
        periodic_totals: dict[str, TransactionBalance],
        periodic_income_totals: dict[str, TransactionBalance],
        periodic_expense_totals: dict[str, TransactionBalance],
        category_averages: dict[Category, TransactionBalance],
        category_totals: dict[Category, TransactionBalance],
        base_currency: Currency,
    ) -> None:
        self._root_row_objects: list[RowObject] = []
        self._flat_row_objects: list[RowObject] = []
        periods = list(periodic_stats.keys())
        self._column_headers = ("Category", *periods, "Average", "Σ Total")

        categories = frozenset(
            item.category for stats in periodic_stats.values() for item in stats
        )
        # sorting by path ensures parents are processed before their children
        categories = sorted(categories, key=lambda x: x.path)
        for category in categories:
            row_data: list[Decimal] = []
            row_transactions: list[tuple[CashTransaction | RefundTransaction]] = []

            for period in periodic_stats:
                stats = _get_category_stats(periodic_stats[period], category.path)
                if stats is not None:
                    row_data.append(stats.balance.value_rounded)
                    row_transactions.append(tuple(stats.transactions))
                else:
                    row_data.append(Decimal(0))
                    row_transactions.append(())

            if all(balance == 0 for balance in row_data):
                continue
            row_data.append(category_averages[category].balance.value_rounded)
            row_data.append(category_totals[category].balance.value_rounded)
            row_transactions.append(tuple(category_averages[category].transactions))
            row_transactions.append(tuple(category_totals[category].transactions))

            if category.parent is None:
                row_object = RowObject(
                    category.name, category.path, row_data, row_transactions, None
                )
                self._root_row_objects.append(row_object)
            else:
                parent_row = _get_row_object_by_path(
                    self._flat_row_objects, category.parent.path
                )
                row_object = RowObject(
                    category.name, category.path, row_data, row_transactions, parent_row
                )
                parent_row.children.append(row_object)
            self._flat_row_objects.append(row_object)

        periodic_totals_row_data: list[Decimal] = []
        periodic_income_totals_row_data: list[Decimal] = []
        periodic_expense_totals_row_data: list[Decimal] = []
        periodic_totals_transactions: list[
            list[CashTransaction | RefundTransaction]
        ] = []
        periodic_income_totals_transactions: list[
            list[CashTransaction | RefundTransaction]
        ] = []
        periodic_expense_totals_transactions: list[
            list[CashTransaction | RefundTransaction]
        ] = []
        for period in periodic_totals:
            periodic_totals_row_data.append(
                periodic_totals[period].balance.value_rounded
            )
            periodic_income_totals_row_data.append(
                periodic_income_totals[period].balance.value_rounded
            )
            periodic_expense_totals_row_data.append(
                periodic_expense_totals[period].balance.value_rounded
            )
            periodic_totals_transactions.append(
                tuple(periodic_totals[period].transactions)
            )
            periodic_income_totals_transactions.append(
                tuple(periodic_income_totals[period].transactions)
            )
            periodic_expense_totals_transactions.append(
                tuple(periodic_expense_totals[period].transactions)
            )

        all_transactions = tuple(
            transaction
            for transactions_balance in periodic_totals.values()
            for transaction in transactions_balance.transactions
        )
        all_income_transactions = tuple(
            transaction
            for transactions_balance in periodic_income_totals.values()
            for transaction in transactions_balance.transactions
        )
        all_expense_transactions = tuple(
            transaction
            for transactions_balance in periodic_expense_totals.values()
            for transaction in transactions_balance.transactions
        )

        total_sum = sum(periodic_totals_row_data)
        average_sum = round(
            total_sum / len(periodic_totals_row_data), base_currency.places
        )
        periodic_totals_row_data.append(average_sum)
        periodic_totals_row_data.append(total_sum)
        periodic_totals_transactions.append(all_transactions)
        periodic_totals_transactions.append(all_transactions)

        income_sum = sum(periodic_income_totals_row_data)
        average_income_sum = round(
            income_sum / len(periodic_income_totals_row_data), base_currency.places
        )
        periodic_income_totals_row_data.append(average_income_sum)
        periodic_income_totals_row_data.append(income_sum)
        periodic_income_totals_transactions.append(all_income_transactions)
        periodic_income_totals_transactions.append(all_income_transactions)

        expense_sum = sum(periodic_expense_totals_row_data)
        average_expense_sum = round(
            expense_sum / len(periodic_expense_totals_row_data), base_currency.places
        )
        periodic_expense_totals_row_data.append(average_expense_sum)
        periodic_expense_totals_row_data.append(expense_sum)
        periodic_expense_totals_transactions.append(all_expense_transactions)
        periodic_expense_totals_transactions.append(all_expense_transactions)

        self._root_row_objects.sort(key=lambda x: x.data[-1], reverse=True)
        self._root_row_objects.append(
            RowObject(
                "Σ Income",
                "Σ Income",
                periodic_income_totals_row_data,
                periodic_income_totals_transactions,
                None,
            )
        )
        self._root_row_objects.append(
            RowObject(
                "Σ Expense",
                "Σ Expense",
                periodic_expense_totals_row_data,
                periodic_expense_totals_transactions,
                None,
            )
        )
        self._root_row_objects.append(
            RowObject(
                "Σ Total",
                "Σ Total",
                periodic_totals_row_data,
                periodic_totals_transactions,
                None,
            )
        )

        for row in self._flat_row_objects:
            if len(row.children) == 0:
                continue
            row.children.sort(key=lambda x: abs(x.data[-1]), reverse=True)

        self.TOTAL_COLUMN_INDEX = len(self._column_headers) - 1
        self.AVERAGE_COLUMN_INDEX = len(self._column_headers) - 2
        self.TOTAL_ROWS_INDEXES = (
            len(self._root_row_objects) - 1,
            len(self._root_row_objects) - 2,
            len(self._root_row_objects) - 3,
        )

    def rowCount(self, index: QModelIndex = ...) -> int:
        if index.isValid():
            if index.column() != 0:
                return 0
            item: RowObject = index.internalPointer()
            return len(item.children)
        return len(self._root_row_objects)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(self._column_headers)
        return self._column_count

    def index(self, row: int, column: int, _parent: QModelIndex = ...) -> QModelIndex:
        if _parent.isValid() and _parent.column() != 0:
            return QModelIndex()

        if not _parent or not _parent.isValid():
            parent = None
        else:
            parent: RowObject = _parent.internalPointer()

        child = self._root_row_objects[row] if parent is None else parent.children[row]
        if child:
            return QAbstractItemModel.createIndex(self, row, column, child)
        return QModelIndex()

    def parent(self, index: QModelIndex = ...) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child: RowObject = index.internalPointer()
        parent = child.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            row = self._root_row_objects.index(parent)
        else:
            row = grandparent.children.index(parent)
        return QAbstractItemModel.createIndex(self, row, 0, parent)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return self._column_headers[section]
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return ALIGNMENT_CENTER
        if (
            role == Qt.ItemDataRole.FontRole
            and orientation == Qt.Orientation.Horizontal
            and section == self.AVERAGE_COLUMN_INDEX
        ):
            return overline_font
        return None

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | Qt.AlignmentFlag | QFont | QBrush | float | int | None:
        if not index.isValid():
            return None

        row_object: RowObject = index.internalPointer()
        row = index.row()
        column = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(row, column, row_object)
        if role == Qt.ItemDataRole.UserRole:
            return self._get_user_role_data(column, row_object)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column == 0:
                return ALIGNMENT_LEFT
            return ALIGNMENT_RIGHT
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(column, row_object.data[column - 1])
        if role == Qt.ItemDataRole.FontRole:
            return self._get_font_role_data(row, column)
        return None

    def _get_display_role_data(
        self, row: int, column: int, row_object: RowObject
    ) -> str | None:
        if column == 0:
            return row_object.name
        if column == self.TOTAL_COLUMN_INDEX or row in self.TOTAL_ROWS_INDEXES:
            prefix = "Σ "
        else:
            prefix = ""
        return prefix + f"{row_object.data[column-1]:,}"

    def _get_user_role_data(self, column: int, row_object: RowObject) -> str | None:
        if column == 0:
            return unicodedata.normalize("NFD", row_object.name)
        return float(row_object.data[column - 1])

    def _get_foreground_role_data(self, column: int, amount: Decimal) -> QBrush | None:
        if column == 0:
            return None
        if amount > 0:
            return colors.get_green_brush()
        if amount < 0:
            return colors.get_red_brush()
        return colors.get_gray_brush()

    def _get_font_role_data(self, row: int, column: int) -> QFont | None:
        if row in self.TOTAL_ROWS_INDEXES:
            if column == self.AVERAGE_COLUMN_INDEX:
                return overline_bold_font
            return bold_font
        if column == self.TOTAL_COLUMN_INDEX:
            return bold_font
        if column == self.AVERAGE_COLUMN_INDEX:
            return overline_font
        return None

    def pre_reset_model(self) -> None:
        self._view.setSortingEnabled(False)  # noqa: FBT003
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()
        self._view.setSortingEnabled(True)  # noqa: FBT003

    def get_selected_transactions(
        self,
    ) -> tuple[tuple[CashTransaction | RefundTransaction, ...], str, str]:
        """Returns a tuple of selected Transactions, period and name."""
        indexes = self._view.selectedIndexes()
        if len(indexes) != 1:
            raise InvalidOperationError(
                "Transactions can be shown for only for exactly one Category."
            )
        index = indexes[0]
        if self._proxy:
            index = self._proxy.mapToSource(index)

        row_object: RowObject = index.internalPointer()
        return (
            row_object.transactions[index.column() - 1],
            self._column_headers[index.column()],
            row_object.path,
        )


def _get_category_stats(
    stats: Collection[CategoryStats], category_path: str
) -> CategoryStats | None:
    for category_stats in stats:
        if category_stats.category.path == category_path:
            return category_stats
    return None


def _get_row_object_by_path(rows: Collection[RowObject], path: str) -> RowObject:
    for row in rows:
        if row.path == path:
            return row
    raise ValueError(f"RowObject for {path=} not found")
