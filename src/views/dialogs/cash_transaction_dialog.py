import logging
from collections.abc import Collection
from datetime import datetime
from decimal import Decimal

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QAbstractButton,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QWidget,
)

from src.models.model_objects.cash_objects import CashTransactionType
from src.views.ui_files.dialogs.Ui_cash_transaction_dialog import (
    Ui_CashTransactionDialog,
)


class AccountGroupDialog(QDialog, Ui_CashTransactionDialog):
    signal_OK = pyqtSignal()

    def __init__(
        self,
        parent: QWidget,
        accounts: Collection[str],
        categories: Collection[str],
        tags: Collection[str],
        edit: bool,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)

        self.categories_completer = QCompleter(categories)
        self.categories_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.categoryLineEdit.setCompleter(self.categories_completer)

        self.tags_completer = QCompleter(tags)
        self.tags_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.tagsLineEdit.setCompleter(self.tags_completer)

        if edit:
            self.setWindowTitle("Edit Cash Transaction")
            self.setWindowIcon(QIcon("icons_custom:coins-pencil.png"))
        else:
            self.setWindowTitle("Add Cash Transaction")
            self.setWindowIcon(QIcon("icons_custom:coins.png"))

        for account in accounts:
            self.accountsComboBox.addItem(account)

        self.buttonBox.clicked.connect(self._handle_button_box_click)

    @property
    def type_(self) -> CashTransactionType:
        if self.incomeRadioButton.isChecked():
            return CashTransactionType.INCOME
        if self.expenseRadioButton.isChecked():
            return CashTransactionType.EXPENSE
        raise ValueError("No radio button checked.")

    @type_.setter
    def type_(self, type_: CashTransactionType) -> None:
        if type_ == CashTransactionType.INCOME:
            self.incomeRadioButton.setChecked(True)
            return
        if type_ == CashTransactionType.EXPENSE:
            self.expenseRadioButton.setChecked(True)
            return
        raise ValueError("Invalid type_ value.")

    @property
    def account(self) -> str:
        return self.accountsComboBox.currentText()

    @account.setter
    def account(self, account: str) -> None:
        self.accountsComboBox.setCurrentText(account)

    @property
    def datetime_(self) -> datetime:
        return self.dateTimeEdit.dateTime().toPyDateTime()

    @datetime_.setter
    def datetime_(self, datetime_: datetime) -> None:
        self.dateTimeEdit.setDateTime(datetime_)

    @property
    def description(self) -> str:
        return self.descriptionPlainTextEdit.toPlainText()

    @description.setter
    def description(self, description: str) -> None:
        self.descriptionPlainTextEdit.setPlainText(description)

    @property
    def amount(self) -> Decimal:
        return Decimal(self.amountDoubleSpinBox.text())

    @amount.setter
    def amount(self, amount: Decimal) -> None:
        self.amountDoubleSpinBox.setValue(amount)

    @property
    def category(self) -> str:
        return self.categoryLineEdit.text()

    @category.setter
    def category(self, category: str) -> None:
        self.categoryLineEdit.setText(category)

    @property
    def tags(self) -> tuple[str]:
        tags = self.tagsLineEdit.text().split(";")
        tags = [tag.strip() for tag in tags]
        return tuple(tags)

    @tags.setter
    def tags(self, tags: Collection[str]) -> None:
        text = "; ".join(tags)
        self.tagsLineEdit.setText(text)

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_OK.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.reject()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")

    def reject(self) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().reject()
