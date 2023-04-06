import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QContextMenuEvent, QCursor, QIcon
from PyQt6.QtWidgets import QLineEdit, QMenu, QWidget
from src.views.constants import TRANSACTION_TABLE_COLUMN_HEADERS, TransactionTableColumn
from src.views.ui_files.widgets.Ui_transaction_table_widget import (
    Ui_TransactionTableWidget,
)


class TransactionTableWidget(QWidget, Ui_TransactionTableWidget):
    signal_search_text_changed = pyqtSignal()

    signal_income = pyqtSignal()
    signal_expense = pyqtSignal()
    signal_refund = pyqtSignal()
    signal_cash_transfer = pyqtSignal()
    signal_buy = pyqtSignal()
    signal_sell = pyqtSignal()
    signal_security_transfer = pyqtSignal()

    signal_find_related = pyqtSignal()

    signal_delete = pyqtSignal()
    signal_edit = pyqtSignal()
    signal_duplicate = pyqtSignal()

    signal_add_tags = pyqtSignal()
    signal_remove_tags = pyqtSignal()
    signal_selection_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self._create_column_actions()
        self._set_icons()
        self._connect_actions()
        self._connect_signals()
        self._setup_header()
        self._setup_table()

    @property
    def search_bar_text(self) -> str:
        return self.searchLineEdit.text()

    @search_bar_text.setter
    def search_bar_text(self, text: str) -> None:
        self.searchLineEdit.setText(text)

    def finalize_setup(self) -> None:
        self.tableView.selectionModel().selectionChanged.connect(
            self.signal_selection_changed.emit
        )
        self.signal_selection_changed.emit()

    def resize_table_to_contents(self) -> None:
        self.tableView.horizontalHeader().setStretchLastSection(False)
        self.tableView.resizeColumnsToContents()
        self.tableView.horizontalHeader().setStretchLastSection(True)

    def set_column_visibility(
        self, column: TransactionTableColumn, *, show: bool
    ) -> None:
        if show != self.tableView.isColumnHidden(column):
            return

        columns = TRANSACTION_TABLE_COLUMN_HEADERS.keys()
        if all(
            self.tableView.isColumnHidden(column_)
            for column_ in columns
            if column_ != column
        ):
            return  # If all other columns are hidden, this column must stay shown

        self.tableView.setColumnHidden(column, not show)
        if show:
            logging.debug(f"Showing TransactionTable column {column.name}")
            self.tableView.resizeColumnToContents(column)
        else:
            logging.debug(f"Hiding TransactionTable column {column.name}")

    def show_all_columns(self) -> None:
        for column in TRANSACTION_TABLE_COLUMN_HEADERS:
            self.set_column_visibility(column, show=True)

    def _create_column_actions(self) -> None:
        self.column_actions: list[QAction] = []
        for column, text in TRANSACTION_TABLE_COLUMN_HEADERS.items():
            action = QAction(parent=self)
            _text = text.replace("&", "&&")
            action.setText(_text)
            action.setData(column)
            action.setCheckable(True)
            action.triggered.connect(
                lambda checked, column=column: self.set_column_visibility(
                    column=column, show=checked
                )
            )
            self.column_actions.append(action)

    def _create_header_context_menu(self, event: QContextMenuEvent) -> None:
        del event
        self.header_menu = QMenu(self)
        for action in self.column_actions:
            column = action.data()
            if self.tableView.isColumnHidden(column):
                action.setChecked(False)
            else:
                action.setChecked(True)
            self.header_menu.addAction(action)
        self.header_menu.addSeparator()
        self.header_menu.addAction(self.actionShow_All_Columns)
        self.header_menu.addAction(self.actionResize_Columns_to_Fit)
        self.header_menu.addAction(self.actionReset_Columns)
        self.header_menu.popup(QCursor.pos())

    def _create_table_context_menu(self, event: QContextMenuEvent) -> None:
        del event
        self.header_menu = QMenu(self)
        self.header_menu.setToolTipsVisible(True)
        self.header_menu.addAction(self.actionEdit)
        self.header_menu.addAction(self.actionDuplicate)
        self.header_menu.addAction(self.actionDelete)
        self.header_menu.addSeparator()
        self.header_menu.addAction(self.actionAdd_Tags)
        self.header_menu.addAction(self.actionRemove_Tags)
        self.header_menu.addSeparator()
        self.header_menu.addAction(self.actionRefund)
        self.header_menu.addAction(self.actionFind_Related)
        self.header_menu.popup(QCursor.pos())

    def _set_icons(self) -> None:
        self.actionFilter_Transactions = QAction(self)
        self.actionFilter_Transactions.setIcon(QIcon("icons_16:funnel.png"))
        self.actionIncome.setIcon(QIcon("icons_custom:coins-plus.png"))
        self.actionExpense.setIcon(QIcon("icons_custom:coins-minus.png"))
        self.actionBuy.setIcon(QIcon("icons_custom:certificate-plus.png"))
        self.actionSell.setIcon(QIcon("icons_custom:certificate-minus.png"))
        self.actionCash_Transfer.setIcon(QIcon("icons_custom:coins-arrow.png"))
        self.actionSecurity_Transfer.setIcon(
            QIcon("icons_custom:certificate-arrow.png")
        )
        self.actionRefund.setIcon(QIcon("icons_custom:coins-arrow-back.png"))
        self.actionFind_Related.setIcon(QIcon("icons_16:magnifier.png"))

        self.actionEdit.setIcon(QIcon("icons_16:pencil.png"))
        self.actionDelete.setIcon(QIcon("icons_16:minus.png"))
        self.actionDuplicate.setIcon(QIcon("icons_16:document-copy.png"))

        self.actionAdd_Tags.setIcon(QIcon("icons_16:tag--plus.png"))
        self.actionRemove_Tags.setIcon(QIcon("icons_16:tag--minus.png"))

        self.transferToolButton.setIcon(QIcon("icons_16:arrow-curve-000-left.png"))

        self.searchLineEdit.addAction(
            QIcon("icons_16:magnifier.png"), QLineEdit.ActionPosition.LeadingPosition
        )

    def _connect_actions(self) -> None:
        self.filterToolButton.setDefaultAction(self.actionFilter_Transactions)
        self.buyToolButton.setDefaultAction(self.actionBuy)
        self.sellToolButton.setDefaultAction(self.actionSell)
        self.incomeToolButton.setDefaultAction(self.actionIncome)
        self.expenseToolButton.setDefaultAction(self.actionExpense)

        self.transferToolButton.addAction(self.actionCash_Transfer)
        self.transferToolButton.addAction(self.actionSecurity_Transfer)

        self.actionShow_All_Columns.triggered.connect(self.show_all_columns)
        self.actionResize_Columns_to_Fit.triggered.connect(
            self.resize_table_to_contents
        )
        self.actionReset_Columns.triggered.connect(self._reset_column_order)

    def _connect_signals(self) -> None:
        self.actionIncome.triggered.connect(self.signal_income.emit)
        self.actionExpense.triggered.connect(self.signal_expense.emit)
        self.actionRefund.triggered.connect(self.signal_refund.emit)
        self.actionCash_Transfer.triggered.connect(self.signal_cash_transfer.emit)
        self.actionBuy.triggered.connect(self.signal_buy.emit)
        self.actionSell.triggered.connect(self.signal_sell.emit)
        self.actionSecurity_Transfer.triggered.connect(
            self.signal_security_transfer.emit
        )

        self.actionFind_Related.triggered.connect(self.signal_find_related.emit)

        self.actionEdit.triggered.connect(self.signal_edit.emit)
        self.actionDuplicate.triggered.connect(self.signal_duplicate.emit)
        self.actionDelete.triggered.connect(self.signal_delete.emit)

        self.actionAdd_Tags.triggered.connect(self.signal_add_tags.emit)
        self.actionRemove_Tags.triggered.connect(self.signal_remove_tags.emit)

        self.searchLineEdit.textChanged.connect(self.signal_search_text_changed.emit)

    def _setup_header(self) -> None:
        header = self.tableView.horizontalHeader()
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self._create_header_context_menu)
        header.setSectionsMovable(True)

    def _setup_table(self) -> None:
        self.tableView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(
            self._create_table_context_menu
        )

    def set_actions(
        self, *, enable_duplicate: bool, enable_refund: bool, enable_find_related: bool
    ) -> None:
        selected_indexes = self.tableView.selectionModel().selectedIndexes()
        selected_rows = [index for index in selected_indexes if index.column() == 0]

        is_any_selected = len(selected_rows) > 0
        is_one_selected = len(selected_rows) == 1

        self.actionEdit.setEnabled(is_any_selected)
        self.actionDuplicate.setEnabled(is_one_selected and enable_duplicate)
        self.actionDelete.setEnabled(is_any_selected)
        self.actionAdd_Tags.setEnabled(is_any_selected)
        self.actionRemove_Tags.setEnabled(is_any_selected)
        self.actionRefund.setEnabled(enable_refund)
        self.actionFind_Related.setEnabled(enable_find_related)

    def _reset_column_order(self) -> None:
        header = self.tableView.horizontalHeader()
        for column in TransactionTableColumn:
            visual_index = header.visualIndex(column)
            header.moveSection(visual_index, column)
        self.resize_table_to_contents()
