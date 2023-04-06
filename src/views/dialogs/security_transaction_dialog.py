from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, auto

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QAbstractButton,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QWidget,
)
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransactionType,
)
from src.models.user_settings import user_settings
from src.views.ui_files.dialogs.Ui_security_transaction_dialog import (
    Ui_SecurityTransactionDialog,
)
from src.views.widgets.multiple_tags_selector_widget import MultipleTagsSelectorWidget


class EditMode(Enum):
    ADD = auto()
    EDIT_SINGLE = auto()
    EDIT_MULTIPLE = auto()


class SecurityTransactionDialog(QDialog, Ui_SecurityTransactionDialog):
    KEEP_CURRENT_VALUES = "Keep current values"

    signal_do_and_close = pyqtSignal()
    signal_do_and_continue = pyqtSignal()

    def __init__(  # noqa: PLR0913
        self,
        parent: QWidget,
        securities: Collection[Security],
        cash_accounts: Collection[CashAccount],
        security_accounts: Collection[SecurityAccount],
        tags: Collection[str],
        *,
        edit_mode: EditMode,
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self._edit_mode = edit_mode

        self._cash_accounts = cash_accounts

        self.tags_widget = MultipleTagsSelectorWidget(self, tags)
        self.tags_label = QLabel("Tags", self)
        self.formLayout.addRow(self.tags_label, self.tags_widget)

        self._initialize_window()
        self._initialize_security_combobox(securities)
        self._initialize_accounts_comboboxes(cash_accounts, security_accounts)

    @property
    def type_(self) -> SecurityTransactionType:
        if self.buyRadioButton.isChecked():
            return SecurityTransactionType.BUY
        if self.sellRadioButton.isChecked():
            return SecurityTransactionType.SELL
        raise ValueError("No radio button checked.")

    @type_.setter
    def type_(self, value: SecurityTransactionType) -> None:
        if value == SecurityTransactionType.BUY:
            self.buyRadioButton.setChecked(True)
        elif value == SecurityTransactionType.SELL:
            self.sellRadioButton.setChecked(True)
        else:
            raise ValueError("Invalid type_ value.")

    @property
    def security_name(self) -> str | None:
        text = self.securityComboBox.currentText()
        if text == self.KEEP_CURRENT_VALUES:
            return None
        return text

    @security_name.setter
    def security_name(self, value: str) -> None:
        self.securityAccountComboBox.setCurrentText(value)

    @property
    def cash_account_path(self) -> str | None:
        text = self.cashAccountComboBox.currentText()
        if text == self.KEEP_CURRENT_VALUES:
            return None
        return text

    @cash_account_path.setter
    def cash_account_path(self, value: str) -> None:
        self.cashAccountComboBox.setCurrentText(value)

    @property
    def security_account_path(self) -> str | None:
        text = self.securityAccountComboBox.currentText()
        if text == self.KEEP_CURRENT_VALUES:
            return None
        return text

    @security_account_path.setter
    def security_account_path(self, value: str) -> None:
        self.securityAccountComboBox.setCurrentText(value)

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
    def description(self) -> str | None:
        text = self.descriptionPlainTextEdit.toPlainText()
        return text if text else None

    @description.setter
    def description(self, description: str) -> None:
        self.descriptionPlainTextEdit.setPlainText(description)

    @property
    def shares(self) -> Decimal:
        text = self.sharesDoubleSpinBox.text()
        if text == self.KEEP_CURRENT_VALUES:
            return None
        if "," in text:
            text = text.replace(",", "")
        return Decimal(text)

    @shares.setter
    def shares(self, shares: Decimal) -> None:
        self.sharesDoubleSpinBox.setValue(shares)

    @property
    def price_per_share(self) -> Decimal:
        text = self.priceDoubleSpinBox.text()
        if text == self.KEEP_CURRENT_VALUES:
            return None
        suffix = self.priceDoubleSpinBox.suffix()
        if suffix in text:
            text = text.removesuffix(suffix)
        if "," in text:
            text = text.replace(",", "")
        return Decimal(text)

    @price_per_share.setter
    def price_per_share(self, price_per_share: Decimal) -> None:
        self.priceDoubleSpinBox.setValue(price_per_share)

    @property
    def tags(self) -> Collection[str]:
        return self.tags_widget.tags

    @tags.setter
    def tags(self, tags: Collection[str]) -> None:
        self.tags_widget.tags = tags

    def _initialize_window(self) -> None:
        self.setWindowIcon(QIcon("icons_custom:certificate.png"))
        self.buttonBox = QDialogButtonBox(self)
        if self._edit_mode != EditMode.ADD:
            self.setWindowTitle("Edit Security Transaction")
            self.buttonBox.addButton("OK", QDialogButtonBox.ButtonRole.AcceptRole)
        else:
            self.setWindowTitle("Add Security Transaction")
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
            self.priceDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.tags_widget.set_placeholder_text("Leave empty to keep current values")

    def _initialize_security_combobox(self, securities: Collection[Security]) -> None:
        if self._edit_mode == EditMode.EDIT_MULTIPLE:
            self.securityComboBox.addItem(self.KEEP_CURRENT_VALUES)
        icon = QIcon("icons_16:certificate.png")
        for security in securities:
            text = (
                f"{security.name} [{security.symbol}]"
                if security.symbol
                else security.name
            )
            self.securityComboBox.addItem(icon, text)

    def _initialize_accounts_comboboxes(
        self,
        cash_accounts: Collection[CashAccount],
        security_accounts: Collection[SecurityAccount],
    ) -> None:
        if self._edit_mode == EditMode.EDIT_MULTIPLE:
            self.cashAccountComboBox.addItem(self.KEEP_CURRENT_VALUES)
            self.securityAccountComboBox.addItem(self.KEEP_CURRENT_VALUES)
        icon_cash_account = QIcon("icons_16:piggy-bank.png")
        icon_security_account = QIcon("icons_16:bank.png")
        for cash_account in cash_accounts:
            self.cashAccountComboBox.addItem(icon_cash_account, cash_account.path)
        for security_account in security_accounts:
            self.securityAccountComboBox.addItem(
                icon_security_account, security_account.path
            )

        self.cashAccountComboBox.currentTextChanged.connect(
            self._set_spinboxes_currencies
        )
        self._set_spinboxes_currencies()

    def _set_spinboxes_currencies(self) -> None:
        self._set_spinbox_currency(self.cash_account_path, self.priceDoubleSpinBox)
        self._set_spinbox_currency(self.cash_account_path, self.totalDoubleSpinBox)

    def _set_spinbox_currency(
        self, cash_account_path: str | None, spinbox: QDoubleSpinBox
    ) -> None:
        if cash_account_path is None:
            return

        account = self._get_cash_account(cash_account_path)
        if account is None:
            return
        spinbox.setSuffix(" " + account.currency.code)
        spinbox.setDecimals(account.currency.places)

    def _get_cash_account(self, account_path: str) -> CashAccount | None:
        for account in self._cash_accounts:
            if account.path == account_path:
                return account
        if self._edit_mode != EditMode.EDIT_MULTIPLE:
            raise ValueError(f"Invalid Account path: {account_path}")
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
