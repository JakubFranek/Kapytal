import unicodedata
from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, auto

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractButton,
    QDialogButtonBox,
    QWidget,
)
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
)
from src.models.user_settings import user_settings
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_security_transfer_dialog import (
    Ui_SecurityTransferDialog,
)
from src.views.utilities.helper_functions import (
    convert_datetime_format_to_qt,
    get_spinbox_value_as_decimal,
)
from src.views.widgets.description_plain_text_edit import DescriptionPlainTextEdit
from src.views.widgets.multiple_tags_selector_widget import MultipleTagsSelectorWidget
from src.views.widgets.smart_combo_box import SmartComboBox


class EditMode(Enum):
    ADD = auto()
    EDIT_SINGLE = auto()
    EDIT_MULTIPLE = auto()


class SecurityTransferDialog(CustomDialog, Ui_SecurityTransferDialog):
    KEEP_CURRENT_VALUES = "Keep current values"

    signal_do_and_close = pyqtSignal()
    signal_do_and_continue = pyqtSignal()
    signal_request_shares_suffix_update = pyqtSignal()

    def __init__(
        self,
        parent: QWidget,
        securities: Collection[Security],
        security_accounts: Collection[SecurityAccount],
        tag_names: Collection[str],
        descriptions: Collection[str],
        *,
        edit_mode: EditMode,
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.edit_mode = edit_mode

        self._security_accounts = security_accounts
        self._securities = securities

        self.tags_widget = MultipleTagsSelectorWidget(self, tag_names)
        self.gridLayout.addWidget(self.tags_widget, 6, 1, 1, -1)

        self._initialize_window()
        self._initialize_security_combobox(securities)
        self._initialize_security_account_comboboxes()
        self._initialize_description_plain_text_edit(descriptions)
        self._initialize_placeholders()
        self._initialize_actions()
        self._set_tab_order()

        display_format = convert_datetime_format_to_qt(
            user_settings.settings.general_date_format
        )
        if "hh" not in display_format or "mm" not in display_format:
            display_format += " hh:mm"
        self.dateTimeEdit.setDisplayFormat(display_format)
        self.dateTimeEdit.calendarWidget().setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        self.dateTimeEdit.dateTimeChanged.connect(
            self.signal_request_shares_suffix_update.emit
        )

    @property
    def security_name(self) -> str | None:
        text = self.securityComboBox.currentText()
        if not text or text == self.KEEP_CURRENT_VALUES:
            return None
        return SecurityTransferDialog._get_security_name_from_security_text(text)

    @security_name.setter
    def security_name(self, value: str) -> None:
        security = self._get_security(value)
        if security is None:
            if self.edit_mode != EditMode.EDIT_MULTIPLE:
                raise ValueError(f"Security {value} not found.")
            self.securityComboBox.setCurrentText(self.KEEP_CURRENT_VALUES)
            return
        text = SecurityTransferDialog._get_security_text(security)
        self.securityComboBox.setCurrentText(text)

    @property
    def sender_path(self) -> str | None:
        text = self.senderComboBox.currentText()
        if text == self.KEEP_CURRENT_VALUES:
            return None
        return text

    @sender_path.setter
    def sender_path(self, value: str) -> None:
        self.senderComboBox.setCurrentText(value)

    @property
    def recipient_path(self) -> str | None:
        text = self.recipientComboBox.currentText()
        if text == self.KEEP_CURRENT_VALUES:
            return None
        return text

    @recipient_path.setter
    def recipient_path(self, value: str) -> None:
        self.recipientComboBox.setCurrentText(value)

    @property
    def datetime_(self) -> datetime | None:
        if self.dateTimeEdit.text() == self.KEEP_CURRENT_VALUES:
            return None
        return (
            self.dateTimeEdit.dateTime()
            .toPyDateTime()
            .replace(
                tzinfo=user_settings.settings.time_zone,
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
                microsecond=0,
            )
        )

    @property
    def description(self) -> str | None:
        text = self.descriptionPlainTextEdit.toPlainText()
        if self.edit_mode == EditMode.EDIT_MULTIPLE:
            return text if text else None
        return text

    @description.setter
    def description(self, description: str) -> None:
        self.descriptionPlainTextEdit.setPlainText(description)

    @property
    def shares(self) -> Decimal | None:
        text = self.sharesDoubleSpinBox.cleanText()
        if text == self.KEEP_CURRENT_VALUES:
            return None
        return get_spinbox_value_as_decimal(self.sharesDoubleSpinBox)

    @shares.setter
    def shares(self, shares: Decimal) -> None:
        self.sharesDoubleSpinBox.setValue(shares)

    @property
    def tag_names(self) -> Collection[str] | None:
        _tag_names = self.tags_widget.tag_names

        if len(_tag_names) != 0:
            return _tag_names

        if self.edit_mode == EditMode.EDIT_MULTIPLE:
            return None
        return ()

    @tag_names.setter
    def tag_names(self, tag_names: Collection[str]) -> None:
        self.tags_widget.tag_names = tag_names

    def set_shares_suffix(self, suffix: str) -> None:
        self.sharesDoubleSpinBox.setSuffix(suffix)

    def _initialize_window(self) -> None:
        self.setWindowIcon(icons.security_transfer)
        self.buttonBox = QDialogButtonBox(self)
        if self.edit_mode != EditMode.ADD:
            if self.edit_mode == EditMode.EDIT_MULTIPLE:
                self.setWindowTitle("Edit Security Transfers")
            else:
                self.setWindowTitle("Edit Security Transfer")
            self.buttonBox.addButton("OK", QDialogButtonBox.ButtonRole.AcceptRole)
        else:
            self.setWindowTitle("Add Security Transfer")
            self.buttonBox.addButton(
                "Create && Continue", QDialogButtonBox.ButtonRole.ApplyRole
            )
            self.buttonBox.addButton(
                "Create && Close", QDialogButtonBox.ButtonRole.AcceptRole
            )
        self.buttonBox.clicked.connect(self._handle_button_box_click)
        self.buttonBox.addButton("Close", QDialogButtonBox.ButtonRole.RejectRole)
        self.gridLayout.addWidget(self.buttonBox, 7, 1, 1, -1)

    def _initialize_placeholders(self) -> None:
        if self.edit_mode == EditMode.EDIT_MULTIPLE:
            self.descriptionPlainTextEdit.setPlaceholderText(
                "Leave empty to keep current values"
            )
            self.dateTimeEdit.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.dateTimeEdit.setMinimumDate(date(1900, 1, 1))
            self.sharesDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.tags_widget.set_placeholder_text("Leave empty to keep current values")

    def _initialize_actions(self) -> None:
        self.actionSwap_Accounts.setIcon(icons.swap)
        self.actionSwap_Accounts.triggered.connect(self._swap_accounts)
        self.swapAccountsToolButton.setDefaultAction(self.actionSwap_Accounts)

    def _initialize_description_plain_text_edit(
        self, descriptions: Collection[str]
    ) -> None:
        self.descriptionPlainTextEdit = DescriptionPlainTextEdit(descriptions)
        self.gridLayout.addWidget(self.descriptionPlainTextEdit, 5, 1, 1, -1)

    def _initialize_security_combobox(self, securities: Collection[Security]) -> None:
        if self.edit_mode == EditMode.EDIT_MULTIPLE:
            placeholder_text = "Leave empty to keep current values"
        else:
            placeholder_text = "Enter Security name"

        _securities = sorted(
            securities,
            key=lambda security: unicodedata.normalize("NFD", security.name.lower()),
        )
        _securities = [
            SecurityTransferDialog._get_security_text(security)
            for security in _securities
        ]
        self.securityComboBox = SmartComboBox(parent=self)
        self.securityComboBox.load_items(_securities, icons.security, placeholder_text)
        self.gridLayout.addWidget(self.securityComboBox, 0, 1, 1, -1)

        self.securityComboBox.currentTextChanged.connect(self._security_changed)
        self._security_changed()

    @staticmethod
    def _get_security_text(security: Security) -> str:
        return (
            f"{security.name} [{security.symbol}]" if security.symbol else security.name
        )

    @staticmethod
    def _get_security_name_from_security_text(text: str) -> str:
        # return the string without the square brackets and its contents
        return text.split("[")[0].strip()

    def _initialize_security_account_comboboxes(
        self,
    ) -> None:
        items = [account.path for account in self._security_accounts]

        if self.edit_mode == EditMode.EDIT_MULTIPLE:
            placeholder_text = "Leave empty to keep current values"
        else:
            placeholder_text = "Enter Account path"

        self.senderComboBox = SmartComboBox(parent=self)
        self.senderComboBox.load_items(items, icons.security_account, placeholder_text)
        self.gridLayout.addWidget(self.senderComboBox, 1, 1, 1, 1)
        self.senderComboBox.setMinimumWidth(300)
        self.senderComboBox.currentTextChanged.connect(
            self.signal_request_shares_suffix_update.emit
        )

        self.recipientComboBox = SmartComboBox(parent=self)
        self.recipientComboBox.load_items(
            items, icons.security_account, placeholder_text
        )
        self.gridLayout.addWidget(self.recipientComboBox, 2, 1, 1, 1)
        self.recipientComboBox.setMinimumWidth(300)

    def _get_security(self, security_name: str) -> Security | None:
        for security in self._securities:
            if security.name == security_name:
                return security
        return None

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

    def _security_changed(self) -> None:
        security = self._get_security(self.security_name)

        if security is None:
            self.sharesDoubleSpinBox.setDecimals(0)  # default value
            self.sharesDoubleSpinBox.setSuffix("")
            return

        self.sharesDoubleSpinBox.setDecimals(security.shares_decimals)
        self.sharesDoubleSpinBox.setSingleStep(10 ** (-security.shares_decimals))
        self.signal_request_shares_suffix_update.emit()

    def _set_tab_order(self) -> None:
        self.setTabOrder(self.securityComboBox, self.senderComboBox)
        self.setTabOrder(self.senderComboBox, self.recipientComboBox)
        self.setTabOrder(self.recipientComboBox, self.sharesDoubleSpinBox)
        self.setTabOrder(self.sharesDoubleSpinBox, self.dateTimeEdit)
        self.setTabOrder(self.dateTimeEdit, self.descriptionPlainTextEdit)
        self.setTabOrder(self.descriptionPlainTextEdit, self.tags_widget)

    def _swap_accounts(self) -> None:
        sender = self.sender_path
        recipient = self.recipient_path
        self.sender_path = recipient
        self.recipient_path = sender
