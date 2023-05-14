from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, auto

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractButton,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
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
from src.views.widgets.multiple_tags_selector_widget import MultipleTagsSelectorWidget


class EditMode(Enum):
    ADD = auto()
    EDIT_SINGLE = auto()
    EDIT_MULTIPLE = auto()


class SecurityTransferDialog(CustomDialog, Ui_SecurityTransferDialog):
    KEEP_CURRENT_VALUES = "Keep current values"

    signal_do_and_close = pyqtSignal()
    signal_do_and_continue = pyqtSignal()

    def __init__(
        self,
        parent: QWidget,
        securities: Collection[Security],
        security_accounts: Collection[SecurityAccount],
        tag_names: Collection[str],
        *,
        edit_mode: EditMode,
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self._edit_mode = edit_mode

        self._security_accounts = security_accounts
        self._securities = securities

        self.tags_widget = MultipleTagsSelectorWidget(self, tag_names)
        self.tags_label = QLabel("Tags", self)
        self.formLayout.addRow(self.tags_label, self.tags_widget)

        self._initialize_window()
        self._initialize_placeholders()
        self._initialize_security_combobox(securities)
        self._initialize_security_account_comboboxes()

    @property
    def security_name(self) -> str | None:
        text = self.securityComboBox.currentText()
        if text == self.KEEP_CURRENT_VALUES:
            return None
        security: Security = self.securityComboBox.currentData()
        return security.name

    @security_name.setter
    def security_name(self, value: str) -> None:
        security = self._get_security(value)
        if security is None:
            if self._edit_mode != EditMode.EDIT_MULTIPLE:
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
    def description(self) -> str | None:
        text = self.descriptionPlainTextEdit.toPlainText()
        return text if text else None

    @description.setter
    def description(self, description: str) -> None:
        self.descriptionPlainTextEdit.setPlainText(description)

    @property
    def shares(self) -> Decimal | None:
        text = self.sharesDoubleSpinBox.cleanText().replace(",", "")
        if text == self.KEEP_CURRENT_VALUES:
            return None
        return Decimal(text)

    @shares.setter
    def shares(self, shares: Decimal) -> None:
        self.sharesDoubleSpinBox.setValue(shares)

    @property
    def tag_names(self) -> Collection[str] | None:
        _tag_names = self.tags_widget.tag_names

        if len(_tag_names) != 0:
            return _tag_names

        if self._edit_mode == EditMode.EDIT_MULTIPLE:
            return None
        return ()

    @tag_names.setter
    def tag_names(self, tag_names: Collection[str]) -> None:
        self.tags_widget.tag_names = tag_names

    def _initialize_window(self) -> None:
        self.setWindowIcon(icons.security_transfer)
        self.buttonBox = QDialogButtonBox(self)
        if self._edit_mode != EditMode.ADD:
            if self._edit_mode == EditMode.EDIT_MULTIPLE:
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
        self.formLayout.setWidget(
            self.formLayout.count() - 1,
            QFormLayout.ItemRole.SpanningRole,
            self.buttonBox,
        )

    def _initialize_placeholders(self) -> None:
        if self._edit_mode == EditMode.EDIT_MULTIPLE:
            self.descriptionPlainTextEdit.setPlaceholderText(
                "Leave empty to keep current values"
            )
            self.dateEdit.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.dateEdit.setMinimumDate(date(1900, 1, 1))
            self.sharesDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.tags_widget.set_placeholder_text("Leave empty to keep current values")

    def _initialize_security_combobox(self, securities: Collection[Security]) -> None:
        if self._edit_mode == EditMode.EDIT_MULTIPLE:
            self.securityComboBox.addItem(self.KEEP_CURRENT_VALUES)
        for security in securities:
            text = SecurityTransferDialog._get_security_text(security)
            self.securityComboBox.addItem(icons.security, text, security)

        self.securityComboBox.currentTextChanged.connect(self._security_changed)
        self._security_changed()

    @staticmethod
    def _get_security_text(security: Security) -> str:
        return (
            f"{security.name} [{security.symbol}]" if security.symbol else security.name
        )

    def _initialize_security_account_comboboxes(
        self,
    ) -> None:
        if self._edit_mode == EditMode.EDIT_MULTIPLE:
            self.senderComboBox.addItem(self.KEEP_CURRENT_VALUES)
            self.recipientComboBox.addItem(self.KEEP_CURRENT_VALUES)

        for security_account in self._security_accounts:
            self.senderComboBox.addItem(icons.security_account, security_account.path)
            self.recipientComboBox.addItem(
                icons.security_account, security_account.path
            )

    def _get_security(self, security_name: str) -> Security | None:
        for security in self._securities:
            if security.name == security_name:
                return security
        if self._edit_mode != EditMode.EDIT_MULTIPLE:
            raise ValueError(f"Invalid Security name: {security_name}")
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
            return

        exponent = security.shares_unit.as_tuple().exponent
        decimals = -exponent if exponent < 0 else 0
        self.sharesDoubleSpinBox.setDecimals(decimals)
        self.sharesDoubleSpinBox.setSingleStep(10**exponent)
