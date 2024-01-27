import locale
from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal, DivisionByZero, InvalidOperation
from enum import Enum, auto

from PyQt6.QtCore import QSignalBlocker, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractButton,
    QDialogButtonBox,
    QDoubleSpinBox,
    QWidget,
)
from src.models.model_objects.cash_objects import CashAccount
from src.models.user_settings import user_settings
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_cash_transfer_dialog import Ui_CashTransferDialog
from src.views.utilities.helper_functions import convert_datetime_format_to_qt
from src.views.widgets.description_plain_text_edit import DescriptionPlainTextEdit
from src.views.widgets.multiple_tags_selector_widget import MultipleTagsSelectorWidget
from src.views.widgets.smart_combo_box import SmartComboBox


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
        descriptions: Collection[str],
        *,
        edit_mode: EditMode,
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.descriptionPlainTextEdit = DescriptionPlainTextEdit(descriptions)
        self.gridLayout.addWidget(self.descriptionPlainTextEdit, 6, 1, 1, -1)

        self.tags_widget = MultipleTagsSelectorWidget(self, tag_names)
        self.gridLayout.addWidget(self.tags_widget, 7, 1, 1, -1)

        self._accounts = accounts
        self._edit_mode = edit_mode

        self._initialize_accounts_comboboxes(accounts)
        self._initialize_window()
        self._initialize_placeholders()
        self._set_spinbox_states()
        self._initialize_signals()
        self._initialize_actions()
        self._set_tab_order()

        display_format = (
            convert_datetime_format_to_qt(user_settings.settings.general_date_format)
            + " hh:mm"
        )
        self.dateTimeEdit.setDisplayFormat(display_format)

    @property
    def datetime_(self) -> datetime | None:
        if self.dateTimeEdit.text() == self.KEEP_CURRENT_VALUES:
            return None
        return (
            self.dateTimeEdit.dateTime()
            .toPyDateTime()
            .replace(
                tzinfo=user_settings.settings.time_zone,
                second=0,
                microsecond=0,
            )
        )

    @datetime_.setter
    def datetime_(self, datetime_: datetime) -> None:
        self.dateTimeEdit.setDateTime(datetime_)

    @property
    def min_datetime(self) -> datetime:
        return (
            self.dateTimeEdit.minimumDateTime()
            .toPyDateTime()
            .replace(
                tzinfo=user_settings.settings.time_zone,
                second=0,
                microsecond=0,
            )
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
        if self._edit_mode in EditMode.get_multiple_edit_values():
            return text if text else None
        return text

    @description.setter
    def description(self, description: str) -> None:
        self.descriptionPlainTextEdit.setPlainText(description)

    @property
    def amount_sent(self) -> Decimal | None:
        text = self.sentDoubleSpinBox.cleanText()
        text_delocalized = locale.delocalize(text)
        if text == self.KEEP_CURRENT_VALUES:
            return None
        return Decimal(text_delocalized)

    @amount_sent.setter
    def amount_sent(self, amount: Decimal) -> None:
        self.sentDoubleSpinBox.setValue(amount)

    @property
    def amount_received(self) -> Decimal | None:
        text = self.receivedDoubleSpinBox.cleanText()
        text_delocalized = locale.delocalize(text)
        if text == self.KEEP_CURRENT_VALUES:
            return None
        return Decimal(text_delocalized)

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
            spinbox.setSuffix("")
            return

        account = self._get_account(account_path)
        if account is None:
            spinbox.setSuffix("")
            return
        spinbox.setSuffix(" " + account.currency.code)
        spinbox.setDecimals(account.currency.decimals)

    def _get_account(self, account_path: str) -> CashAccount | None:
        for account in self._accounts:
            if account.path == account_path:
                return account
        return None

    def _set_exchange_rate(self) -> None:
        sender = self._get_account(self.sender_path)
        recipient = self._get_account(self.recipient_path)
        if sender is None or recipient is None:
            self.exchangeRateLabel.hide()
            self.exchangeRateLineEdit.hide()
            return

        self.exchangeRateLabel.setVisible(sender.currency != recipient.currency)
        self.exchangeRateLineEdit.setVisible(sender.currency != recipient.currency)

        if sender.currency == recipient.currency:
            self.receivedDoubleSpinBox.setValue(float(self.amount_sent))
            return

        try:
            rate_primary = self.amount_received / self.amount_sent
            rate_secondary = self.amount_sent / self.amount_received
            rate_primary = round(rate_primary, recipient.currency.decimals)
            rate_secondary = round(rate_secondary, sender.currency.decimals)
        except (InvalidOperation, DivisionByZero, TypeError):
            self.exchangeRateLineEdit.setText("Undefined")
            return

        text_primary = (
            f"1 {sender.currency.code} = {rate_primary:n} {recipient.currency.code}"
        )
        text_secondary = (
            f"1 {recipient.currency.code} = {rate_secondary:n} {sender.currency.code}"
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
        self.gridLayout.addWidget(self.buttonBox, 8, 1, 1, -1)

    def _initialize_accounts_comboboxes(
        self, accounts: Collection[CashAccount]
    ) -> None:
        items = [account.path for account in accounts]

        if self._edit_mode in EditMode.get_multiple_edit_values():
            placeholder_text = "Leave empty to keep current values"
        else:
            placeholder_text = "Enter Account path"

        self.senderComboBox = SmartComboBox(parent=self)
        self.senderComboBox.load_items(items, icons.cash_account, placeholder_text)
        self.gridLayout.addWidget(self.senderComboBox, 0, 1, 1, 1)

        self.recipientComboBox = SmartComboBox(parent=self)
        self.recipientComboBox.load_items(items, icons.cash_account, placeholder_text)
        self.gridLayout.addWidget(self.recipientComboBox, 1, 1, 1, 1)

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
            self.dateTimeEdit.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.dateTimeEdit.setMinimumDate(date(1900, 1, 1))
            self.sentDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.receivedDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.tags_widget.set_placeholder_text("Leave empty to keep current values")

    def _set_spinbox_states(self) -> None:
        sender_account = self._get_account(self.sender_path)
        recipient_account = self._get_account(self.recipient_path)
        sender_specified = sender_account is not None
        recipient_specified = recipient_account is not None

        if self._edit_mode == EditMode.EDIT_MULTIPLE_SENDER_MIXED_CURRENCY:
            self.sentDoubleSpinBox.setEnabled(sender_specified)
        elif self._edit_mode == EditMode.EDIT_MULTIPLE_RECIPIENT_MIXED_CURRENCY:
            self.receivedDoubleSpinBox.setEnabled(recipient_specified)
        elif self._edit_mode == EditMode.EDIT_MULTIPLE_MIXED_CURRENCY:
            self.sentDoubleSpinBox.setEnabled(sender_specified)
            self.receivedDoubleSpinBox.setEnabled(recipient_specified)

        if sender_specified and recipient_specified:
            self.receivedDoubleSpinBox.setEnabled(
                sender_account.currency != recipient_account.currency
            )

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

    def _initialize_actions(self) -> None:
        self.actionSwap_Accounts.setIcon(icons.swap)
        self.actionSwap_Accounts.triggered.connect(self._swap_accounts)
        self.swapAccountsToolButton.setDefaultAction(self.actionSwap_Accounts)

    def _set_tab_order(self) -> None:
        self.setTabOrder(self.senderComboBox, self.recipientComboBox)
        self.setTabOrder(self.recipientComboBox, self.sentDoubleSpinBox)
        self.setTabOrder(self.sentDoubleSpinBox, self.receivedDoubleSpinBox)
        self.setTabOrder(self.receivedDoubleSpinBox, self.dateTimeEdit)
        self.setTabOrder(self.dateTimeEdit, self.descriptionPlainTextEdit)
        self.setTabOrder(self.descriptionPlainTextEdit, self.tags_widget)

    def _swap_accounts(self) -> None:
        sender = self.sender_path
        recipient = self.recipient_path
        sent = self.amount_sent
        received = self.amount_received
        with QSignalBlocker(self.senderComboBox):
            self.senderComboBox.setCurrentText(recipient)
        with QSignalBlocker(self.recipientComboBox):
            self.recipientComboBox.setCurrentText(sender)
        with QSignalBlocker(self.sentDoubleSpinBox):
            self.sentDoubleSpinBox.setValue(received)
        with QSignalBlocker(self.receivedDoubleSpinBox):
            self.receivedDoubleSpinBox.setValue(sent)
        self._set_spinboxes_currencies()
        self._set_spinbox_states()
