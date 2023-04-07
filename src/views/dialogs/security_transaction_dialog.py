from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, auto

from PyQt6.QtCore import QSignalBlocker, pyqtSignal
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
    EDIT_MULTIPLE_MIXED_CURRENCY = auto()

    @staticmethod
    def get_multiple_edit_values() -> tuple["EditMode", ...]:
        return (
            EditMode.EDIT_MULTIPLE,
            EditMode.EDIT_MULTIPLE_MIXED_CURRENCY,
        )


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
        self._security_accounts = security_accounts
        self._securities = securities

        self.tags_widget = MultipleTagsSelectorWidget(self, tags)
        self.tags_label = QLabel("Tags", self)
        self.formLayout.addRow(self.tags_label, self.tags_widget)

        self._initialize_window()
        self._initialize_placeholders()
        self._initialize_signals()
        self._initialize_security_combobox(securities)
        self._setup_security_account_combobox()
        self._setup_cash_account_combobox()

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
        security: Security = self.securityComboBox.currentData()
        return security.name

    @security_name.setter
    def security_name(self, value: str) -> None:
        security = self._get_security(value)
        if security is None:
            if self._edit_mode not in EditMode.get_multiple_edit_values():
                raise ValueError(f"Security {value} not found.")
            self.securityComboBox.setCurrentText(self.KEEP_CURRENT_VALUES)
            return
        text = SecurityTransactionDialog._get_security_text(security)
        self.securityComboBox.setCurrentText(text)

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
    def price_per_share(self) -> Decimal | None:
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
    def currency_code(self) -> str | None:
        if self.priceDoubleSpinBox.text() == self.KEEP_CURRENT_VALUES:
            return None
        suffix = self.priceDoubleSpinBox.suffix()
        return suffix.strip()

    @property
    def tag_names(self) -> Collection[str] | None:
        _tag_names = self.tags_widget.tag_names

        if len(_tag_names) != 0:
            return _tag_names

        if self._edit_mode in EditMode.get_multiple_edit_values():
            return None
        return ()

    @tag_names.setter
    def tag_names(self, tags: Collection[str]) -> None:
        self.tags_widget.tag_names = tags

    def _initialize_window(self) -> None:
        self.setWindowIcon(QIcon("icons_16:certificate.png"))
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
        if self._edit_mode in EditMode.get_multiple_edit_values():
            self.descriptionPlainTextEdit.setPlaceholderText(
                "Leave empty to keep current values"
            )
            self.dateEdit.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.dateEdit.setMinimumDate(date(1900, 1, 1))
            self.sharesDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.priceDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.totalDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.tags_widget.set_placeholder_text("Leave empty to keep current values")

    def _initialize_security_combobox(self, securities: Collection[Security]) -> None:
        if self._edit_mode in EditMode.get_multiple_edit_values():
            self.securityComboBox.addItem(self.KEEP_CURRENT_VALUES)
        icon = QIcon("icons_16:certificate.png")
        for security in securities:
            text = SecurityTransactionDialog._get_security_text(security)
            self.securityComboBox.addItem(icon, text, security)

        self.securityComboBox.currentTextChanged.connect(self._security_changed)
        self._security_changed()

    @staticmethod
    def _get_security_text(security: Security) -> str:
        return (
            f"{security.name} [{security.symbol}]" if security.symbol else security.name
        )

    def _setup_security_account_combobox(
        self,
    ) -> None:
        if self._edit_mode in EditMode.get_multiple_edit_values():
            self.securityAccountComboBox.addItem(self.KEEP_CURRENT_VALUES)
        icon_security_account = QIcon("icons_16:bank.png")
        for security_account in self._security_accounts:
            self.securityAccountComboBox.addItem(
                icon_security_account, security_account.path
            )

    def _setup_cash_account_combobox(self) -> None:
        with QSignalBlocker(self.cashAccountComboBox):
            security = self._get_security(self.security_name)
            cash_account_path = self.cash_account_path
            self.cashAccountComboBox.clear()
            icon_cash_account = QIcon("icons_16:piggy-bank.png")

            if self._edit_mode == EditMode.EDIT_MULTIPLE or (
                self._edit_mode == EditMode.EDIT_MULTIPLE_MIXED_CURRENCY
                and security is None
            ):
                self.cashAccountComboBox.addItem(self.KEEP_CURRENT_VALUES)

            for cash_account in self._cash_accounts:
                if security is not None and cash_account.currency == security.currency:
                    self.cashAccountComboBox.addItem(
                        icon_cash_account, cash_account.path
                    )

            self.cash_account_path = cash_account_path

            self._set_spinboxes_currencies()

    def _initialize_signals(self) -> None:
        self.cashAccountComboBox.currentTextChanged.connect(
            self._set_spinboxes_currencies
        )
        self.sharesDoubleSpinBox.valueChanged.connect(self._update_total)
        self.priceDoubleSpinBox.valueChanged.connect(self._update_total)

    def _update_total(self) -> None:
        shares = self.shares
        price_per_share = self.price_per_share
        if shares is None or price_per_share is None:
            self.totalDoubleSpinBox.setValue(0)
            return
        total = shares * price_per_share
        self.totalDoubleSpinBox.setValue(total)

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

    def _get_cash_account(self, account_path: str) -> CashAccount | None:
        for account in self._cash_accounts:
            if account.path == account_path:
                return account
        if self._edit_mode not in EditMode.get_multiple_edit_values():
            raise ValueError(f"Invalid Account path: {account_path}")
        return None

    def _get_security(self, security_name: str) -> Security | None:
        for security in self._securities:
            if security.name == security_name:
                return security
        if self._edit_mode not in EditMode.get_multiple_edit_values():
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
        self._setup_cash_account_combobox()

        if self._edit_mode == EditMode.EDIT_MULTIPLE_MIXED_CURRENCY:
            self.cashAccountComboBox.setEnabled(security is not None)
            self.priceDoubleSpinBox.setEnabled(security is not None)
            if security is not None:
                self.priceDoubleSpinBox.setSpecialValueText("")
            else:
                self.priceDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)

        if security is None:
            return

        exponent = security.shares_unit.as_tuple().exponent
        decimals = -exponent if exponent < 0 else 0
        self.sharesDoubleSpinBox.setDecimals(decimals)
        self.sharesDoubleSpinBox.setSingleStep(10**exponent)
