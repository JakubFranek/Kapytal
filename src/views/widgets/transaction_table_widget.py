from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QContextMenuEvent, QCursor, QIcon
from PyQt6.QtWidgets import QLineEdit, QMenu, QWidget

from src.views.constants import TRANSACTION_TABLE_COLUMN_HEADERS
from src.views.ui_files.widgets.Ui_transaction_table_widget import (
    Ui_TransactionTableWidget,
)


class TransactionTableWidget(QWidget, Ui_TransactionTableWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.actionFilterTransactions = QAction(self)

        self._create_column_actions()
        self._set_icons()
        self._connect_actions()
        self._setup_header_context_menu()

    @property
    def search_bar_text(self) -> str:
        return self.searchLineEdit.text()

    def resize_table_to_contents(self) -> None:
        self.tableView.resizeColumnsToContents()

    def set_column_visibility(self, column: int, show: bool) -> None:
        columns = TRANSACTION_TABLE_COLUMN_HEADERS.keys()
        if any(
            not self.tableView.isColumnHidden(column_)
            for column_ in columns
            if column_ != column
        ):
            self.tableView.setColumnHidden(column, not show)

    def show_all_columns(self) -> None:
        for column in TRANSACTION_TABLE_COLUMN_HEADERS.keys():
            self.set_column_visibility(column, True)

    def _create_column_actions(self) -> None:
        self.column_actions: list[QAction] = []
        for column, text in TRANSACTION_TABLE_COLUMN_HEADERS.items():
            action = QAction(parent=self)
            text = text.replace("&", "&&")
            action.setText(text)
            action.setData(column)
            action.setCheckable(True)
            action.toggled.connect(
                lambda checked, column=column: self.set_column_visibility(
                    column=column, show=checked
                )
            )
            self.column_actions.append(action)
        self.actionShow_All_Columns = QAction(parent=self)
        self.actionShow_All_Columns.setText("Show All")
        self.actionShow_All_Columns.triggered.connect(self.show_all_columns)

    def _create_header_context_menu(
        self, event: QContextMenuEvent  # noqa: U100
    ) -> None:
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
        self.header_menu.popup(QCursor.pos())

    def _set_icons(self) -> None:
        self.actionFilterTransactions.setIcon(QIcon("icons_16:funnel.png"))
        self.actionIncome.setIcon(QIcon("icons_custom:coins-plus.png"))
        self.actionExpense.setIcon(QIcon("icons_custom:coins-minus.png"))
        self.actionBuy.setIcon(QIcon("icons_custom:certificate-plus.png"))
        self.actionSell.setIcon(QIcon("icons_custom:certificate-minus.png"))
        self.actionCash_Transfer.setIcon(QIcon("icons_custom:coins-arrow.png"))
        self.actionSecurity_Transfer.setIcon(
            QIcon("icons_custom:certificate-arrow.png")
        )
        self.actionRefund.setIcon(QIcon("icons_custom:coins-arrow-back.png"))

        self.transferToolButton.setIcon(QIcon("icons_16:arrow-curve-000-left.png"))

        self.searchLineEdit.addAction(
            QIcon("icons_16:magnifier.png"), QLineEdit.ActionPosition.LeadingPosition
        )

    def _connect_actions(self) -> None:
        self.filterToolButton.setDefaultAction(self.actionFilterTransactions)
        self.buyToolButton.setDefaultAction(self.actionBuy)
        self.sellToolButton.setDefaultAction(self.actionSell)
        self.incomeToolButton.setDefaultAction(self.actionIncome)
        self.expenseToolButton.setDefaultAction(self.actionExpense)

        self.transferToolButton.addAction(self.actionCash_Transfer)
        self.transferToolButton.addAction(self.actionSecurity_Transfer)

    def _setup_header_context_menu(self) -> None:
        self.tableView.horizontalHeader().setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.tableView.horizontalHeader().customContextMenuRequested.connect(
            self._create_header_context_menu
        )
