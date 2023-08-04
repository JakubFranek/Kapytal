import logging
from collections.abc import Collection
from datetime import datetime
from decimal import Decimal

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractButton,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from src.models.base_classes.account import Account
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import CashAmount
from src.models.user_settings import user_settings
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.dialogs.select_item_dialog import ask_user_for_selection
from src.views.ui_files.dialogs.Ui_refund_transaction_dialog import (
    Ui_RefundTransactionDialog,
)
from src.views.widgets.description_plain_text_edit import DescriptionPlainTextEdit
from src.views.widgets.label_widget import LabelWidget
from src.views.widgets.refund_row_widget import RefundRowWidget


class RefundTransactionDialog(CustomDialog, Ui_RefundTransactionDialog):
    signal_do_and_close = pyqtSignal()

    def __init__(  # noqa: PLR0913
        self,
        parent: QWidget,
        refunded_transaction: CashTransaction,
        accounts: Collection[CashAccount],
        payees: Collection[str],
        descriptions: Collection[str],
        edited_refund: RefundTransaction | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)

        self._edited_refund = edited_refund
        self._refunded_transaction = refunded_transaction
        self._accounts = accounts
        self._payees = payees
        for payee in payees:
            self.payeeComboBox.addItem(payee)

        self.amountDoubleSpinBox.setSuffix(" " + refunded_transaction.currency.code)

        self.descriptionPlainTextEdit = DescriptionPlainTextEdit(descriptions)
        self.description_label = QLabel("Description")
        self.formLayout.insertRow(
            3, self.description_label, self.descriptionPlainTextEdit
        )

        self._initialize_category_rows()
        self._initialize_tag_rows()
        self._amount_changed()  # recalculate limits

        self._initialize_accounts_combobox(accounts)
        self._initialize_window()
        self._initialize_actions()
        self._initialize_placeholders()

        if edited_refund is not None:
            self._initialize_values()

        self._set_tab_order()

    @property
    def account_path(self) -> str:
        return self.accountsComboBox.currentText()

    @account_path.setter
    def account_path(self, value: str) -> None:
        self.accountsComboBox.setCurrentText(value)

    @property
    def payee(self) -> str:
        return self.payeeComboBox.currentText()

    @payee.setter
    def payee(self, value: str) -> None:
        self.payeeComboBox.setCurrentText(value)

    @property
    def datetime_(self) -> datetime:
        return (
            self.dateEdit.dateTime()
            .toPyDateTime()
            .replace(tzinfo=user_settings.settings.time_zone)
        )

    @datetime_.setter
    def datetime_(self, value: datetime) -> None:
        self.dateEdit.setDateTime(value)

    @property
    def min_datetime(self) -> datetime:
        return (
            self.dateEdit.minimumDateTime()
            .toPyDateTime()
            .replace(tzinfo=user_settings.settings.time_zone)
        )

    @property
    def description(self) -> str:
        return self.descriptionPlainTextEdit.toPlainText()

    @description.setter
    def description(self, value: str) -> None:
        self.descriptionPlainTextEdit.setPlainText(value)

    @property
    def amount(self) -> Decimal:
        text = self.amountDoubleSpinBox.cleanText().replace(",", "")
        return Decimal(text)

    @property
    def min_amount(self) -> Decimal:
        return Decimal(self.amountDoubleSpinBox.minimum())

    @property
    def currency_code(self) -> str:
        return self._refunded_transaction.currency.code

    @property
    def amount_decimals(self) -> int:
        self.amountDoubleSpinBox.decimals()

    @property
    def category_amount_pairs(self) -> tuple[tuple[str, Decimal], ...]:
        return tuple((row.text, row.amount) for row in self._category_rows)

    @property
    def tag_amount_pairs(self) -> tuple[tuple[str, Decimal], ...]:
        return tuple((row.text, row.amount) for row in self._tag_rows)

    @property
    def refunded_transaction(self) -> CashTransaction:
        return self._refunded_transaction

    @property
    def edited_refund(self) -> RefundTransaction | None:
        return self._edited_refund

    def reject(self) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().reject()

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_do_and_close.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.reject()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")

    def _initialize_window(self) -> None:
        self.setWindowIcon(icons.refund)

        if self._edited_refund is not None:
            self.setWindowTitle("Edit Refund")
        else:
            self.setWindowTitle("Add Refund")

        self.buttonBox.addButton("OK", QDialogButtonBox.ButtonRole.AcceptRole)
        self.buttonBox.clicked.connect(self._handle_button_box_click)
        self.buttonBox.addButton("Close", QDialogButtonBox.ButtonRole.RejectRole)

    def _initialize_actions(self) -> None:
        self.actionSelect_Payee.setIcon(icons.payee)
        self.actionSelect_Payee.triggered.connect(self._get_payee)
        self.payeeToolButton.setDefaultAction(self.actionSelect_Payee)

        self.actionSelect_Account.setIcon(icons.cash_account)
        self.actionSelect_Account.triggered.connect(self._get_account)
        self.accountsToolButton.setDefaultAction(self.actionSelect_Account)

    def _initialize_accounts_combobox(self, accounts: Collection[Account]) -> None:
        for account in accounts:
            self.accountsComboBox.addItem(icons.cash_account, account.path)

    def _initialize_placeholders(self) -> None:
        self.payeeComboBox.lineEdit().setPlaceholderText("Enter Payee name")
        self.payeeComboBox.setCurrentIndex(-1)

    def _initialize_category_rows(self) -> None:
        self.category_rows_vertical_layout = QVBoxLayout()
        self._category_rows: list[RefundRowWidget] = []

        for category, amount in self._refunded_transaction.category_amount_pairs:
            row = RefundRowWidget(self, category.path, self.currency_code)
            row.set_min(0)
            max_amount = self._refunded_transaction.get_max_refundable_for_category(
                category, self._edited_refund
            ).value_rounded
            row.set_max(max_amount)
            row.set_spinbox_enabled(enable=max_amount != 0)
            row.amount = amount.value_rounded
            self._category_rows.append(row)
            self.category_rows_vertical_layout.addWidget(row)
            row.signal_amount_changed.connect(self._amount_changed)

        self.formLayout.insertRow(
            6, LabelWidget(self, "Categories"), self.category_rows_vertical_layout
        )

    def _initialize_tag_rows(self) -> None:
        self.tag_rows_vertical_layout = QVBoxLayout()
        self._tag_rows: list[RefundRowWidget] = []

        for tag, amount in self._refunded_transaction.tag_amount_pairs:
            row = RefundRowWidget(self, tag.name, self.currency_code)
            row.amount = amount.value_rounded
            self._tag_rows.append(row)
            self.tag_rows_vertical_layout.addWidget(row)
            row.signal_amount_changed.connect(self._amount_changed)

        if len(self._tag_rows) > 0:
            self.formLayout.insertRow(
                7, LabelWidget(self, "Tags"), self.tag_rows_vertical_layout
            )

    def _amount_changed(self) -> None:
        total_amount = Decimal(0)
        for row in self._category_rows:
            total_amount += row.amount

        self.amountDoubleSpinBox.setValue(total_amount)

        refund_amount = CashAmount(self.amount, self._refunded_transaction.currency)
        for tag, _ in self._refunded_transaction.tag_amount_pairs:
            row = None
            for _row in self._tag_rows:
                if _row.text == tag.name:
                    row = _row
                    break
            if row is None:
                raise ValueError(f"RefundRowWidget for Tag {tag.name} not found.")

            tag_min = self._refunded_transaction.get_min_refundable_for_tag(
                tag,
                self._edited_refund,
                refund_amount=refund_amount,
            ).value_rounded
            tag_max = self._refunded_transaction.get_max_refundable_for_tag(
                tag,
                self._edited_refund,
                refund_amount=refund_amount,
            ).value_rounded

            row.set_min(tag_min)
            row.set_max(tag_max)
            row.set_spinbox_enabled(enable=tag_min != tag_max)

    def _get_payee(self) -> None:
        payee = ask_user_for_selection(
            self,
            self._payees,
            "Select Payee",
            icons.payee,
        )
        self.payee = payee if payee else self.payee

    def _get_account(self) -> None:
        account_paths = [account.path for account in self._accounts]
        account = ask_user_for_selection(
            self,
            account_paths,
            "Select Account",
            icons.cash_account,
        )
        self.account_path = account if account else self.account_path

    def _set_tab_order(self) -> None:
        self.setTabOrder(self.accountsComboBox, self.accountsToolButton)
        self.setTabOrder(self.accountsToolButton, self.payeeComboBox)
        self.setTabOrder(self.payeeComboBox, self.payeeToolButton)
        self.setTabOrder(self.payeeToolButton, self.dateEdit)
        self.setTabOrder(self.dateEdit, self.descriptionPlainTextEdit)
        self.setTabOrder(self.descriptionPlainTextEdit, self.amountDoubleSpinBox)

        self.setTabOrder(self.amountDoubleSpinBox, self._category_rows[0])

        index = 0
        while index + 1 < len(self._category_rows):
            self.setTabOrder(self._category_rows[index], self._category_rows[index + 1])
            index += 1
        last_widget = self._category_rows[index]

        if len(self._tag_rows) == 0:
            return

        self.setTabOrder(last_widget, self._tag_rows[0])

        index = 0
        while index + 1 < len(self._tag_rows):
            self.setTabOrder(self._tag_rows[index], self._tag_rows[index + 1])
            index += 1

    def _initialize_values(self) -> None:
        if self._edited_refund is None:
            raise ValueError("Expected RefundTransaction, received None.")
        self.account_path = self._edited_refund.account.path
        self.payee = self._edited_refund.payee.name
        self.datetime_ = self._edited_refund.datetime_
        self.description = self._edited_refund.description

        for category, amount in self._edited_refund.category_amount_pairs:
            for _row in self._category_rows:
                if _row.text == category.path:
                    row = _row
                    break
            else:
                raise ValueError(
                    f"RefundRowWidget for Category '{category.path}' not found."
                )
            row.amount = amount.value_rounded

        for tag, amount in self._edited_refund.tag_amount_pairs:
            for _row in self._tag_rows:
                if _row.text == tag.name:
                    row = _row
                    break
            else:
                raise ValueError(f"RefundRowWidget for Tag '{tag.name}' not found.")
            row.amount = amount.value_rounded
