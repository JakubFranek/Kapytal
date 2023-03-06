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

from src.models.base_classes.account import Account
from src.models.model_objects.cash_objects import CashAccount, CashTransactionType
from src.models.model_objects.security_objects import SecurityAccount
from src.views.ui_files.dialogs.Ui_cash_transaction_dialog import (
    Ui_CashTransactionDialog,
)


class CashTransactionDialog(QDialog, Ui_CashTransactionDialog):
    signal_create_and_close = pyqtSignal()
    signal_create_and_continue = pyqtSignal()

    signal_account_changed = pyqtSignal()

    def __init__(
        self,
        parent: QWidget,
        accounts: Collection[Account],
        payees: Collection[str],
        categories: Collection[str],
        tags: Collection[str],
        type_: CashTransactionType,
        edit: bool,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)

        self._payees_completer = QCompleter(payees)
        self._payees_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._payees_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.payeeLineEdit.setCompleter(self._payees_completer)

        self._categories_completer = QCompleter(categories)
        self._categories_completer.setCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )
        self._categories_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.categoryLineEdit.setCompleter(self._categories_completer)

        self._tags_completer = QCompleter(tags)
        self._tags_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._tags_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._tags_completer.setWidget(self.tagsLineEdit)
        self._tags_completer.activated.connect(self._handle_tags_completion)
        self.tagsLineEdit.textChanged.connect(self._handle_tags_text_changed)
        self._tags_completing = False

        if edit:
            self.setWindowTitle("Edit Cash Transaction")
            self.setWindowIcon(QIcon("icons_custom:coins-pencil.png"))
        else:
            self.setWindowTitle("Add Cash Transaction")
            self.setWindowIcon(QIcon("icons_custom:coins.png"))

        for account in accounts:
            if isinstance(account, CashAccount):
                icon = QIcon("icons_16:piggy-bank.png")
            elif isinstance(account, SecurityAccount):
                icon = QIcon("icons_16:bank.png")
            else:
                raise TypeError("Unexpected Account type.")
            self.accountsComboBox.addItem(icon, account.path)

        self.accountsComboBox.currentTextChanged.connect(
            self.signal_account_changed.emit
        )

        self.buttonBox.clicked.connect(self._handle_button_box_click)
        self.buttonBox.addButton(
            "Create && Continue", QDialogButtonBox.ButtonRole.ApplyRole
        )
        self.buttonBox.addButton(
            "Create && Close", QDialogButtonBox.ButtonRole.AcceptRole
        )
        self.buttonBox.addButton("Close", QDialogButtonBox.ButtonRole.RejectRole)

        self.type_ = type_

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
    def payee(self) -> str:
        return self.payeeLineEdit.text()

    @payee.setter
    def payee(self, payee: str) -> None:
        self.payeeLineEdit.setText(payee)

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
    def currency_code(self) -> str:
        self.amountDoubleSpinBox.suffix()

    @currency_code.setter
    def currency_code(self, code: str) -> None:
        self.amountDoubleSpinBox.setSuffix(" " + code)

    @property
    def amount_decimals(self) -> int:
        self.amountDoubleSpinBox.decimals()

    @amount_decimals.setter
    def amount_decimals(self, value: int) -> None:
        self.amountDoubleSpinBox.setDecimals(value)

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
            self.signal_create_and_close.emit()
        elif role == QDialogButtonBox.ButtonRole.ApplyRole:
            self.signal_create_and_continue.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.reject()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")

    def reject(self) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().reject()

    def _handle_tags_text_changed(self, text: str) -> None:
        if not self._tags_completing:
            found = False
            prefix = text.rpartition(";")[-1].strip()
            if len(prefix) > 0:
                self._tags_completer.setCompletionPrefix(prefix)
                if self._tags_completer.currentRow() >= 0:
                    found = True
            if found:
                self._tags_completer.complete()
            else:
                self._tags_completer.popup().hide()

    def _handle_tags_completion(self, text: str) -> None:
        if not self._tags_completing:
            self._tags_completing = True
            prefix = self._tags_completer.completionPrefix()
            final_text = self.tagsLineEdit.text()[: -len(prefix)] + text
            self.tagsLineEdit.setText(final_text)
            self._tags_completing = False
