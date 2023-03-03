from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QLineEdit, QWidget

from src.views.ui_files.widgets.Ui_transaction_table_widget import (
    Ui_TransactionTableWidget,
)


class TransactionTableWidget(QWidget, Ui_TransactionTableWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.actionFilterTransactions = QAction(self)

        self._set_icons()
        self._connect_actions()

        self.searchLineEdit.addAction(
            QIcon("icons_16:magnifier.png"), QLineEdit.ActionPosition.LeadingPosition
        )

    @property
    def search_bar_text(self) -> str:
        return self.searchLineEdit.text()

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

    def _connect_actions(self) -> None:
        self.filterToolButton.setDefaultAction(self.actionFilterTransactions)
        self.buyToolButton.setDefaultAction(self.actionBuy)
        self.sellToolButton.setDefaultAction(self.actionSell)
        self.incomeToolButton.setDefaultAction(self.actionIncome)
        self.expenseToolButton.setDefaultAction(self.actionExpense)

        self.transferToolButton.addAction(self.actionCash_Transfer)
        self.transferToolButton.addAction(self.actionSecurity_Transfer)
