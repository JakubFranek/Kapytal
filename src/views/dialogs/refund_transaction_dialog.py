import logging
from collections.abc import Collection
from datetime import datetime
from decimal import Decimal

from PyQt6.QtCore import Qt, pyqtSignal
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
from src.views.ui_files.dialogs.Ui_refund_transaction_dialog import (
    Ui_RefundTransactionDialog,
)
from src.views.utilities.helper_functions import (
    convert_datetime_format_to_qt,
    get_spinbox_value_as_decimal,
)
from src.views.widgets.description_plain_text_edit import DescriptionPlainTextEdit
from src.views.widgets.label_widget import LabelWidget
from src.views.widgets.refund_row_widget import RefundRowWidget
from src.views.widgets.smart_combo_box import SmartComboBox


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

        self._initialize_accounts_combobox(accounts)
        self._initialize_payees_combobox(payees)

        self.amountDoubleSpinBox.setSuffix(" " + refunded_transaction.currency.code)

        self.descriptionPlainTextEdit = DescriptionPlainTextEdit(descriptions)
        self.description_label = QLabel("Description")
        self.formLayout.insertRow(
            3, self.description_label, self.descriptionPlainTextEdit
        )

        self._initialize_category_rows()
        self._initialize_tag_rows()
        self._amount_changed()  # recalculate limits

        self._initialize_window()

        if edited_refund is not None:
            self._initialize_values()

        self._set_tab_order()

        display_format = convert_datetime_format_to_qt(
            user_settings.settings.general_date_format
        )
        if "hh" not in display_format or "mm" not in display_format:
            display_format += " hh:mm"
        self.dateTimeEdit.setDisplayFormat(display_format)
        self.dateTimeEdit.calendarWidget().setFirstDayOfWeek(Qt.DayOfWeek.Monday)

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
            self.dateTimeEdit.dateTime()
            .toPyDateTime()
            .replace(
                tzinfo=user_settings.settings.time_zone,
                microsecond=0,
            )
        )

    @datetime_.setter
    def datetime_(self, value: datetime) -> None:
        self.dateTimeEdit.setDateTime(value)

    @property
    def min_datetime(self) -> datetime:
        return (
            self.dateTimeEdit.minimumDateTime()
            .toPyDateTime()
            .replace(
                tzinfo=user_settings.settings.time_zone,
                microsecond=0,
            )
        )

    @property
    def description(self) -> str:
        return self.descriptionPlainTextEdit.toPlainText()

    @description.setter
    def description(self, value: str) -> None:
        self.descriptionPlainTextEdit.setPlainText(value)

    @property
    def amount(self) -> Decimal:
        return get_spinbox_value_as_decimal(self.amountDoubleSpinBox)

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

    def _initialize_accounts_combobox(self, accounts: Collection[Account]) -> None:
        items = [account.path for account in accounts]

        self.accountsComboBox = SmartComboBox(parent=self)
        self.accountsComboBox.load_items(
            items, icons.cash_account, "Enter Account path"
        )
        self.formLayout.insertRow(0, "Account", self.accountsComboBox)

    def _initialize_payees_combobox(self, payees: Collection[str]) -> None:
        self.payeeComboBox = SmartComboBox(parent=self)
        self.payeeComboBox.load_items(payees, icons.payee, "Enter Payee name")
        self.formLayout.insertRow(1, "Payee", self.payeeComboBox)

    def _initialize_category_rows(self) -> None:
        self.category_rows_vertical_layout = QVBoxLayout()
        self._category_rows: list[RefundRowWidget] = []

        for category, amount in self._refunded_transaction.category_amount_pairs:
            row = RefundRowWidget(
                self, category.path, self.currency_code, icons.category
            )
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
            row = RefundRowWidget(self, tag.name, self.currency_code, icons.tag)
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

    def _set_tab_order(self) -> None:
        self.setTabOrder(self.accountsComboBox, self.payeeComboBox)
        self.setTabOrder(self.payeeComboBox, self.dateTimeEdit)
        self.setTabOrder(self.dateTimeEdit, self.descriptionPlainTextEdit)
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
