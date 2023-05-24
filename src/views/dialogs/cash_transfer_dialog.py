from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal, DivisionByZero, InvalidOperation
from enum import Enum, auto

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractButton,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QWidget,
)
from src.models.model_objects.cash_objects import CashAccount
from src.models.user_settings import user_settings
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_cash_transfer_dialog import Ui_CashTransferDialog
from src.views.widgets.multiple_tags_selector_widget import MultipleTagsSelectorWidget


class EditMode(Enum):
    ADD = auto()
    EDIT_SINGLE = auto()
    EDIT_MULTIPLE = auto()
    EDIT_MULTIPLE_SENDER_MIXED_CURRENCY = auto()
    EDIT_MULTIPLE_RECIPIENT_MIXED_CURRENCY = auto()
    EDIT_MULTIPLE_MIXED_CURRENCY = auto()

    @staticmethod
    def get_multiple_edit_values() -> tuple["EditMode", ...]:
        return (
            EditMode.EDIT_MULTIPLE,
            EditMode.EDIT_MULTIPLE_SENDER_MIXED_CURRENCY,
            EditMode.EDIT_MULTIPLE_RECIPIENT_MIXED_CURRENCY,
            EditMode.EDIT_MULTIPLE_MIXED_CURRENCY,
        )


class CashTransferDialog(CustomDialog, Ui_CashTransferDialog):
    KEEP_CURRENT_VALUES = "Keep current values"

    signal_do_and_close = pyqtSignal()
    signal_do_and_continue = pyqtSignal()

    def __init__(
        self,
        parent: QWidget,
        accounts: Collection[CashAccount],
        tag_names: Collection[str],
        *,
        edit_mode: EditMode,
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.tags_widget = MultipleTagsSelectorWidget(self, tag_names)
        self.tags_label = QLabel("Tags", self)
        self.formLayout.addRow(self.tags_label, self.tags_widget)

        self._accounts = accounts
        self._edit_mode = edit_mode

        self._initialize_accounts_comboboxes(accounts)
        self._initialize_window()
        self._initialize_placeholders()
        self._set_spinbox_states()
        self._initialize_signals()

    @property
    def datetime_(self) -> datetime | None:
        if self.dateEdit.text() == self.KEEP_CURRENT_VALUES:
            return None
        return (
            self.dateEdit.dateTime()
            .toPyDateTime()
            .replace(tzinfo=user_settings.settings.time_zone)
        )

    @datetime_.setter
    def datetime_(self, datetime_: datetime) -> None:
        self.dateEdit.setDateTime(datetime_)

    @property
    def min_datetime(self) -> datetime:
        return (
            self.dateEdit.minimumDateTime()
            .toPyDateTime()
            .replace(tzinfo=user_settings.settings.time_zone)
        )

    @property
    def sender_path(self) -> str | None:
        text = self.senderComboBox.currentText()
        if text == self.KEEP_CURRENT_VALUES:
            return None
        return text

    @sender_path.setter
    def sender_path(self, account: str) -> None:
        self.senderComboBox.setCurrentText(account)

    @property
    def recipient_path(self) -> str | None:
        text = self.recipientComboBox.currentText()
        if text == self.KEEP_CURRENT_VALUES:
            return None
        return text

    @recipient_path.setter
    def recipient_path(self, account: str) -> None:
        self.recipientComboBox.setCurrentText(account)

    @property
    def description(self) -> str | None:
        text = self.descriptionPlainTextEdit.toPlainText()
        return text if text else None

    @description.setter
    def description(self, description: str) -> None:
        self.descriptionPlainTextEdit.setPlainText(description)

    @property
    def amount_sent(self) -> Decimal | None:
        text = self.sentDoubleSpinBox.cleanText().replace(",", "")
        if text == self.KEEP_CURRENT_VALUES:
            return None
        return Decimal(text)

    @amount_sent.setter
    def amount_sent(self, amount: Decimal) -> None:
        self.sentDoubleSpinBox.setValue(amount)

    @property
    def amount_received(self) -> Decimal | None:
        text = self.receivedDoubleSpinBox.cleanText()
        if text == self.KEEP_CURRENT_VALUES:
            return None
        text = text.replace(",", "")
        return Decimal(text)

    @amount_received.setter
    def amount_received(self, amount: Decimal) -> None:
        self.receivedDoubleSpinBox.setValue(amount)

    @property
    def tag_names(self) -> tuple[str, ...] | None:
        _tags = self.tags_widget.tag_names
        if len(_tags) == 0 and self._edit_mode in EditMode.get_multiple_edit_values():
            return None
        return _tags

    @tag_names.setter
    def tag_names(self, values: Collection[str]) -> None:
        self.tags_widget.tag_names = values

    def _set_spinboxes_currencies(self) -> None:
        self._set_spinbox_currency(self.sender_path, self.sentDoubleSpinBox)
        self._set_spinbox_currency(self.recipient_path, self.receivedDoubleSpinBox)
        self._set_exchange_rate()

    def _set_spinbox_currency(
        self, account_path: str | None, spinbox: QDoubleSpinBox
    ) -> None:
        if account_path is None:
            return

        account = self._get_account(account_path)
        if account is None:
            return
        spinbox.setSuffix(" " + account.currency.code)
        spinbox.setDecimals(account.currency.places)

    def _get_account(self, account_path: str) -> CashAccount | None:
        for account in self._accounts:
            if account.path == account_path:
                return account
        if self._edit_mode not in EditMode.get_multiple_edit_values():
            raise ValueError(f"Invalid Account path: {account_path}")
        return None

    def _set_exchange_rate(self) -> None:
        sender = self._get_account(self.sender_path)
        recipient = self._get_account(self.recipient_path)
        if sender is None or recipient is None:
            return

        self.exchangeRateLabel.setVisible(sender.currency != recipient.currency)
        self.exchangeRateLineEdit.setVisible(sender.currency != recipient.currency)

        if sender.currency == recipient.currency:
            return

        try:
            rate_primary = self.amount_received / self.amount_sent
            rate_secondary = self.amount_sent / self.amount_received
            rate_primary = round(rate_primary, 2 * recipient.currency.places)
            rate_secondary = round(rate_secondary, 2 * sender.currency.places)
        except (InvalidOperation, DivisionByZero, TypeError):
            self.exchangeRateLineEdit.setText("Undefined")
            return

        text_primary = (
            f"1 {sender.currency.code} = {rate_primary} {recipient.currency.code}"
        )
        text_secondary = (
            f"1 {recipient.currency.code} = {rate_secondary} {sender.currency.code}"
        )

        text_overall = text_primary + " | " + text_secondary
        self.exchangeRateLineEdit.setText(text_overall)

    def _initialize_window(self) -> None:
        self.setWindowIcon(icons.cash_transfer)
        self.buttonBox = QDialogButtonBox(self)
        if self._edit_mode != EditMode.ADD:
            if self._edit_mode in EditMode.get_multiple_edit_values():
                self.setWindowTitle("Edit Cash Transfers")
            else:
                self.setWindowTitle("Edit Cash Transfer")
            self.buttonBox.addButton("OK", QDialogButtonBox.ButtonRole.AcceptRole)
        else:
            self.setWindowTitle("Add Cash Transfer")
            self.buttonBox.addButton(
                "Create && Continue", QDialogButtonBox.ButtonRole.ApplyRole
            )
            self.buttonBox.addButton(
                "Create && Close", QDialogButtonBox.ButtonRole.AcceptRole
            )
        self.buttonBox.clicked.connect(self._handle_button_box_click)
        self.buttonBox.addButton("Close", QDialogButtonBox.ButtonRole.RejectRole)
        self.formLayout.setWidget(
            self.formLayout.count() - 1,
            QFormLayout.ItemRole.SpanningRole,
            self.buttonBox,
        )

    def _initialize_accounts_comboboxes(
        self, accounts: Collection[CashAccount]
    ) -> None:
        if self._edit_mode in EditMode.get_multiple_edit_values():
            self.senderComboBox.addItem(self.KEEP_CURRENT_VALUES)
            self.recipientComboBox.addItem(self.KEEP_CURRENT_VALUES)
        for account in accounts:
            self.senderComboBox.addItem(icons.cash_account, account.path)
            self.recipientComboBox.addItem(icons.cash_account, account.path)

        self.senderComboBox.currentTextChanged.connect(self._set_spinboxes_currencies)
        self.recipientComboBox.currentTextChanged.connect(
            self._set_spinboxes_currencies
        )
        self._set_spinboxes_currencies()

    def _initialize_placeholders(self) -> None:
        if self._edit_mode in EditMode.get_multiple_edit_values():
            self.descriptionPlainTextEdit.setPlaceholderText(
                "Leave empty to keep current values"
            )
            self.dateEdit.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.dateEdit.setMinimumDate(date(1900, 1, 1))
            self.sentDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.receivedDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.tags_widget.set_placeholder_text("Leave empty to keep current values")

    def _set_spinbox_states(self) -> None:
        sender_specified = self.sender_path is not None
        recipient_specified = self.recipient_path is not None

        if self._edit_mode == EditMode.EDIT_MULTIPLE_SENDER_MIXED_CURRENCY:
            self.sentDoubleSpinBox.setEnabled(sender_specified)
        elif self._edit_mode == EditMode.EDIT_MULTIPLE_RECIPIENT_MIXED_CURRENCY:
            self.receivedDoubleSpinBox.setEnabled(recipient_specified)
        elif self._edit_mode == EditMode.EDIT_MULTIPLE_MIXED_CURRENCY:
            self.sentDoubleSpinBox.setEnabled(sender_specified)
            self.receivedDoubleSpinBox.setEnabled(recipient_specified)

        if not sender_specified:
            self.sentDoubleSpinBox.setValue(0)
        if not recipient_specified:
            self.receivedDoubleSpinBox.setValue(0)

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

    def _initialize_signals(self) -> None:
        self.sentDoubleSpinBox.valueChanged.connect(self._set_exchange_rate)
        self.receivedDoubleSpinBox.valueChanged.connect(self._set_exchange_rate)
        self.senderComboBox.currentTextChanged.connect(self._set_spinbox_states)
        self.recipientComboBox.currentTextChanged.connect(self._set_spinbox_states)