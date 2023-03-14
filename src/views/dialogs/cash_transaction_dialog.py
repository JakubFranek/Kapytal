import logging
from collections.abc import Collection
from datetime import datetime
from decimal import Decimal

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QAbstractButton,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.models.base_classes.account import Account
from src.models.model_objects.cash_objects import CashAccount, CashTransactionType
from src.models.model_objects.security_objects import SecurityAccount
from src.views.ui_files.dialogs.Ui_cash_transaction_dialog import (
    Ui_CashTransactionDialog,
)
from src.views.widgets.add_attribute_row_widget import AddAttributeRowWidget
from src.views.widgets.single_category_row_widget import SingleCategoryRowWidget
from src.views.widgets.split_attribute_row_widget import ItemType, SplitItemRowWidget


class CashTransactionDialog(QDialog, Ui_CashTransactionDialog):
    signal_do_and_close = pyqtSignal()
    signal_do_and_continue = pyqtSignal()

    signal_account_changed = pyqtSignal()

    signal_select_tag = pyqtSignal()
    signal_select_category = pyqtSignal()
    signal_select_payee = pyqtSignal()

    def __init__(
        self,
        parent: QWidget,
        accounts: Collection[Account],
        payees: Collection[str],
        categories_income: Collection[str],
        categories_expense: Collection[str],
        tags: Collection[str],
        type_: CashTransactionType,
        edit: bool,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)

        self.type_ = type_
        self._categories_income = categories_income
        self._categories_expense = categories_expense

        self._initialize_single_category()
        self.incomeRadioButton.toggled.connect(self._setup_categories_combobox)
        self.expenseRadioButton.toggled.connect(self._setup_categories_combobox)

        for payee in payees:
            self.payeeComboBox.addItem(payee)

        self._initialize_tags_completer(tags)
        self._initialize_accounts_combobox(accounts)
        self._initialize_window(edit)
        self._initialize_actions()
        self._initialize_combobox_placeholders()

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
        return self.payeeComboBox.currentText()

    @payee.setter
    def payee(self, payee: str) -> None:
        self.payeeComboBox.setCurrentText(payee)

    @property
    def datetime_(self) -> datetime:
        return self.dateEdit.dateTime().toPyDateTime()

    @datetime_.setter
    def datetime_(self, datetime_: datetime) -> None:
        self.dateEdit.setDateTime(datetime_)

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
        return self.categoryComboBox.currentText()

    @category.setter
    def category(self, category: str) -> None:
        self.categoryComboBox.setCurrentText(category)

    @property
    def tags(self) -> tuple[str]:
        tags = self.tagsLineEdit.text().split(";")
        tags = [tag.strip() for tag in tags if tag.strip() != ""]
        return tuple(tags)

    @tags.setter
    def tags(self, tags: Collection[str]) -> None:
        text = "; ".join(tags)
        self.tagsLineEdit.setText(text)

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_do_and_close.emit()
        elif role == QDialogButtonBox.ButtonRole.ApplyRole:
            self.signal_do_and_continue.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.reject()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")

    def reject(self) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().reject()

    def _initialize_window(self, edit: bool) -> None:
        if edit:
            self.setWindowTitle("Edit Cash Transaction")
            self.setWindowIcon(QIcon("icons_custom:coins-pencil.png"))
            self.buttonBox.addButton("OK", QDialogButtonBox.ButtonRole.AcceptRole)
        else:
            self.setWindowTitle("Add Cash Transaction")
            self.setWindowIcon(QIcon("icons_custom:coins.png"))
            self.buttonBox.addButton(
                "Create && Continue", QDialogButtonBox.ButtonRole.ApplyRole
            )
            self.buttonBox.addButton(
                "Create && Close", QDialogButtonBox.ButtonRole.AcceptRole
            )
        self.buttonBox.clicked.connect(self._handle_button_box_click)
        self.buttonBox.addButton("Close", QDialogButtonBox.ButtonRole.RejectRole)

    def _initialize_actions(self) -> None:
        self.actionSelect_Payee.setIcon(QIcon("icons_16:user-silhouette.png"))
        self.actionSelect_Tag.setIcon(QIcon("icons_16:tag.png"))
        self.actionSplit_Tags.setIcon(QIcon("icons_16:arrow-split.png"))

        self.actionSelect_Payee.triggered.connect(self.signal_select_payee)
        self.actionSelect_Tag.triggered.connect(self.signal_select_tag)

        self.payeeToolButton.setDefaultAction(self.actionSelect_Payee)
        self.tagsToolButton.setDefaultAction(self.actionSelect_Tag)
        self.splitTagsToolButton.setDefaultAction(self.actionSplit_Tags)

    def _initialize_accounts_combobox(self, accounts: Collection[Account]) -> None:
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

    def _initialize_combobox_placeholders(self) -> None:
        self.payeeComboBox.lineEdit().setPlaceholderText("Enter Payee name")
        self.payeeComboBox.setCurrentIndex(-1)

    def _initialize_tags_completer(self, tags: Collection[str]) -> None:
        self._tags_completer = QCompleter(tags)
        self._tags_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._tags_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._tags_completer.setWidget(self.tagsLineEdit)
        self._tags_completer.activated.connect(self._handle_tags_completion)
        self.tagsLineEdit.textEdited.connect(self._handle_tags_text_changed)
        self._tags_completing = False

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

    def _setup_categories_combobox(self) -> None:
        for row in self._category_rows:
            if self.type_ == CashTransactionType.INCOME:
                row.load_categories(self._categories_income)
            else:
                row.load_categories(self._categories_expense)

    def _initialize_single_category(self) -> None:
        self._single_category_row = SingleCategoryRowWidget(self)
        self._category_rows = [self._single_category_row]
        self.formLayout.insertRow(
            6, QLabel("Category", self), self._single_category_row
        )
        self._setup_categories_combobox()
        self._single_category_row.signal_split_categories.connect(
            self._split_categories
        )

    def _split_categories(self) -> None:
        current_category = self._single_category_row.category

        self.formLayout.removeRow(6)
        self.split_categories_vertical_layout = QVBoxLayout(None)
        row1 = SplitItemRowWidget(ItemType.CATEGORY, self)
        row2 = SplitItemRowWidget(ItemType.CATEGORY, self)
        self._category_rows = [row1, row2]
        self.split_categories_vertical_layout.addWidget(row1)
        self.split_categories_vertical_layout.addWidget(row2)
        self.formLayout.insertRow(
            6, QLabel("Categories", self), self.split_categories_vertical_layout
        )

        self._setup_categories_combobox()
        row1.category = current_category

        for row in self._category_rows:
            row.signal_remove_row.connect(self._remove_split_row)

        self.add_row_widget = AddAttributeRowWidget(self)
        self.add_row_widget.signal_add_row.connect(self._add_row)
        self.split_categories_vertical_layout.addWidget(self.add_row_widget)

    def _add_row(self) -> None:
        row = SplitItemRowWidget(ItemType.CATEGORY, self)
        self._category_rows.append(row)
        index = self.split_categories_vertical_layout.count() - 1
        self.split_categories_vertical_layout.insertWidget(index, row)

    def _remove_split_row(self, removed_row: SplitItemRowWidget) -> None:
        no_of_rows = self.split_categories_vertical_layout.count() - 1
        if no_of_rows == 2:
            self._category_rows.remove(removed_row)
            remaining_category = self._category_rows[0].category
            self.formLayout.removeRow(6)
            self._initialize_single_category()
            self._single_category_row.category = remaining_category
            return
        self.split_categories_vertical_layout.removeWidget(removed_row)
        self._category_rows.remove(removed_row)
        # FIXME: wrong row is deleted when a row has been added beforehand
        # IDEA: "preferred" size for description? or something
