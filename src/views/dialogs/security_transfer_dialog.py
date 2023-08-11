import unicodedata
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
        self._edit_mode = edit_mode

        self._security_accounts = security_accounts
        self._securities = securities

        self.tags_widget = MultipleTagsSelectorWidget(self, tag_names)
        self.tags_label = QLabel("Tags", self)
        self.formLayout.addRow(self.tags_label, self.tags_widget)

        self._initialize_window()
        self._initialize_security_combobox(securities)
        self._initialize_security_account_comboboxes()
        self._initialize_description_plain_text_edit(descriptions)
        self._initialize_placeholders()
        self._set_tab_order()

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
            .replace(
                tzinfo=user_settings.settings.time_zone,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
        )

    @datetime_.setter
    def datetime_(self, datetime_: datetime) -> None:
        self.dateEdit.setDateTime(datetime_)

    @property
    def min_datetime(self) -> datetime:
        return (
            self.dateEdit.minimumDateTime()
            .toPyDateTime()
            .replace(
                tzinfo=user_settings.settings.time_zone,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
        )

    @property
    def description(self) -> str | None:
        text = self.descriptionPlainTextEdit.toPlainText()
        if self._edit_mode == EditMode.EDIT_MULTIPLE:
            return text if text else None
        return text

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

    def _initialize_description_plain_text_edit(
        self, descriptions: Collection[str]
    ) -> None:
        self.descriptionPlainTextEdit = DescriptionPlainTextEdit(descriptions)
        self.description_label = QLabel("Description")
        self.formLayout.insertRow(
            5, self.description_label, self.descriptionPlainTextEdit
        )

    def _initialize_security_combobox(self, securities: Collection[Security]) -> None:
        if self._edit_mode == EditMode.EDIT_MULTIPLE:
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
        self.formLayout.insertRow(0, "Security", self.securityComboBox)

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

        if self._edit_mode == EditMode.EDIT_MULTIPLE:
            placeholder_text = "Leave empty to keep current values"
        else:
            placeholder_text = "Enter Account path"

        self.senderComboBox = SmartComboBox(parent=self)
        self.senderComboBox.load_items(items, icons.security_account, placeholder_text)
        self.formLayout.insertRow(1, "Sender", self.senderComboBox)
        self.senderComboBox.setMinimumWidth(300)

        self.recipientComboBox = SmartComboBox(parent=self)
        self.recipientComboBox.load_items(
            items, icons.security_account, placeholder_text
        )
        self.formLayout.insertRow(2, "Recipient", self.recipientComboBox)
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
            return

        exponent = security.shares_unit.as_tuple().exponent
        decimals = -exponent if exponent < 0 else 0
        self.sharesDoubleSpinBox.setDecimals(decimals)
        self.sharesDoubleSpinBox.setSingleStep(10**exponent)

    def _set_tab_order(self) -> None:
        self.setTabOrder(self.securityComboBox, self.senderComboBox)
        self.setTabOrder(self.senderComboBox, self.recipientComboBox)
        self.setTabOrder(self.recipientComboBox, self.sharesDoubleSpinBox)
        self.setTabOrder(self.sharesDoubleSpinBox, self.dateEdit)
        self.setTabOrder(self.dateEdit, self.descriptionPlainTextEdit)
        self.setTabOrder(self.descriptionPlainTextEdit, self.tags_widget)
