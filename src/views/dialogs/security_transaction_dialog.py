import unicodedata
from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, auto

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractButton,
    QApplication,
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
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_security_transaction_dialog import (
    Ui_SecurityTransactionDialog,
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
    EDIT_MULTIPLE_MIXED_CURRENCY = auto()

    @staticmethod
    def get_multiple_edit_values() -> tuple["EditMode", ...]:
        return (
            EditMode.EDIT_MULTIPLE,
            EditMode.EDIT_MULTIPLE_MIXED_CURRENCY,
        )


class SecurityTransactionDialog(CustomDialog, Ui_SecurityTransactionDialog):
    KEEP_CURRENT_VALUES = "Keep current values"

    signal_do_and_close = pyqtSignal()
    signal_do_and_continue = pyqtSignal()
    signal_request_shares_suffix_update = pyqtSignal()

    def __init__(  # noqa: PLR0913
        self,
        parent: QWidget,
        securities: Collection[Security],
        cash_accounts: Collection[CashAccount],
        security_accounts: Collection[SecurityAccount],
        tag_names: Collection[str],
        descriptions: Collection[str],
        *,
        edit_mode: EditMode,
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.edit_mode = edit_mode

        self._cash_accounts = cash_accounts
        self._security_accounts = security_accounts
        self._securities = securities

        self.tags_widget = MultipleTagsSelectorWidget(self, tag_names)
        self.tags_label = QLabel("Tags", self)
        self.formLayout.addRow(self.tags_label, self.tags_widget)

        self._fixed_spinboxes: list[QDoubleSpinBox] = []
        self._spinboxes = {
            self.sharesDoubleSpinBox,
            self.priceDoubleSpinBox,
            self.totalDoubleSpinBox,
        }

        self.priceDoubleSpinBox.setDecimals(
            user_settings.settings.amount_per_share_decimals
        )

        self._initialize_window()
        self._initialize_security_combobox(securities)
        self._initialize_cash_account_combobox()
        self._setup_cash_account_combobox()
        self._initialize_security_account_combobox()
        self._initialize_description_plain_text_edit(descriptions)
        self._initialize_signals()
        self._initialize_placeholders()
        self._initialize_events()
        self._set_tab_order()

        display_format = convert_datetime_format_to_qt(
            user_settings.settings.general_date_format
        )
        if "hh" not in display_format or "mm" not in display_format:
            display_format += " hh:mm"
        self.dateTimeEdit.setDisplayFormat(display_format)
        self.dateTimeEdit.calendarWidget().setFirstDayOfWeek(Qt.DayOfWeek.Monday)

    @property
    def type_(self) -> SecurityTransactionType:
        if self.buyRadioButton.isChecked():
            return SecurityTransactionType.BUY
        if self.sellRadioButton.isChecked():
            return SecurityTransactionType.SELL
        if self.dividendRadioButton.isChecked():
            return SecurityTransactionType.DIVIDEND
        raise ValueError("No radio button checked.")

    @type_.setter
    def type_(self, value: SecurityTransactionType) -> None:
        if value == SecurityTransactionType.BUY:
            self.buyRadioButton.setChecked(True)
        elif value == SecurityTransactionType.SELL:
            self.sellRadioButton.setChecked(True)
        elif value == SecurityTransactionType.DIVIDEND:
            self.dividendRadioButton.setChecked(True)
        else:
            raise ValueError("Invalid type_ value.")

    @property
    def security_name(self) -> str | None:
        text = self.securityComboBox.currentText()
        if not text or text == self.KEEP_CURRENT_VALUES:
            return None
        return SecurityTransactionDialog._get_security_name_from_security_text(text)

    @security_name.setter
    def security_name(self, value: str) -> None:
        security = self._get_security(value)
        if security is None:
            if self.edit_mode not in EditMode.get_multiple_edit_values():
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
        if self.edit_mode in EditMode.get_multiple_edit_values():
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
        self._fixed_spinboxes = []

    @property
    def amount_per_share(self) -> Decimal | None:
        text = self.priceDoubleSpinBox.cleanText()
        if text == self.KEEP_CURRENT_VALUES:
            return None
        return get_spinbox_value_as_decimal(self.priceDoubleSpinBox)

    @amount_per_share.setter
    def amount_per_share(self, amount_per_share: Decimal) -> None:
        self.priceDoubleSpinBox.setValue(amount_per_share)
        self._fixed_spinboxes = []

    @property
    def currency_code(self) -> str | None:
        if self.priceDoubleSpinBox.cleanText() == self.KEEP_CURRENT_VALUES:
            return None
        suffix = self.priceDoubleSpinBox.suffix()
        return suffix.strip()

    @property
    def tag_names(self) -> Collection[str] | None:
        _tag_names = self.tags_widget.tag_names

        if len(_tag_names) != 0:
            return _tag_names

        if self.edit_mode in EditMode.get_multiple_edit_values():
            return None
        return ()

    @tag_names.setter
    def tag_names(self, tag_names: Collection[str]) -> None:
        self.tags_widget.tag_names = tag_names

    def set_shares_suffix(self, suffix: str) -> None:
        self.sharesDoubleSpinBox.setSuffix(suffix)

    def _initialize_window(self) -> None:
        self.setWindowIcon(icons.security)
        self.buttonBox = QDialogButtonBox(self)
        if self.edit_mode != EditMode.ADD:
            if self.edit_mode in EditMode.get_multiple_edit_values():
                self.setWindowTitle("Edit Security Transactions")
            else:
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
        if self.edit_mode in EditMode.get_multiple_edit_values():
            self.descriptionPlainTextEdit.setPlaceholderText(
                "Leave empty to keep current values"
            )
            self.dateTimeEdit.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.dateTimeEdit.setMinimumDate(date(1900, 1, 1))
            self.sharesDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.priceDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.totalDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.tags_widget.set_placeholder_text("Leave empty to keep current values")

    def _initialize_events(self) -> None:
        self.securityAccountComboBox.currentTextChanged.connect(
            self._update_shares_spinbox_suffix
        )
        self.buyRadioButton.toggled.connect(self._update_shares_spinbox_suffix)
        self.dateTimeEdit.dateTimeChanged.connect(self._update_shares_spinbox_suffix)

    def _initialize_security_combobox(self, securities: Collection[Security]) -> None:
        if self.edit_mode in EditMode.get_multiple_edit_values():
            placeholder_text = "Leave empty to keep current values"
        else:
            placeholder_text = "Enter Security name"

        _securities = sorted(
            securities,
            key=lambda security: unicodedata.normalize("NFD", security.name.lower()),
        )
        _securities = [
            SecurityTransactionDialog._get_security_text(security)
            for security in _securities
        ]
        self.securityComboBox = SmartComboBox(parent=self)
        self.securityComboBox.load_items(_securities, icons.security, placeholder_text)
        self.formLayout.insertRow(1, "Security", self.securityComboBox)

        self.securityComboBox.currentTextChanged.connect(self._security_changed)

    @staticmethod
    def _get_security_text(security: Security) -> str:
        return (
            f"{security.name} [{security.symbol}]" if security.symbol else security.name
        )

    @staticmethod
    def _get_security_name_from_security_text(text: str) -> str:
        # return the string without the square brackets and its contents
        return text.split("[")[0].strip()

    def _initialize_description_plain_text_edit(
        self, descriptions: Collection[str]
    ) -> None:
        self.descriptionPlainTextEdit = DescriptionPlainTextEdit(descriptions)
        self.description_label = QLabel("Description")
        self.formLayout.insertRow(
            5, self.description_label, self.descriptionPlainTextEdit
        )

    def _initialize_cash_account_combobox(
        self,
    ) -> None:
        self.cashAccountComboBox = SmartComboBox(parent=self)
        self.formLayout.insertRow(2, "Cash Account", self.cashAccountComboBox)

        self._security_changed()

    def _initialize_security_account_combobox(
        self,
    ) -> None:
        items = [account.path for account in self._security_accounts]

        if self.edit_mode in EditMode.get_multiple_edit_values():
            placeholder_text = "Leave empty to keep current values"
        else:
            placeholder_text = "Enter Account path"

        self.securityAccountComboBox = SmartComboBox(parent=self)
        self.securityAccountComboBox.load_items(
            items, icons.security_account, placeholder_text
        )
        self.formLayout.insertRow(3, "Security Account", self.securityAccountComboBox)
        self.securityAccountComboBox.setMinimumWidth(300)

    def _setup_cash_account_combobox(self) -> None:
        with QSignalBlocker(self.cashAccountComboBox):
            security = self._get_security(self.security_name)
            cash_account_path = self.cash_account_path
            self.cashAccountComboBox.clear()

            if self.edit_mode == EditMode.EDIT_MULTIPLE or (
                self.edit_mode == EditMode.EDIT_MULTIPLE_MIXED_CURRENCY
                and security is None
            ):
                placeholder_text = "Leave empty to keep current values"
            elif security is None:
                placeholder_text = "Select valid Security"
            else:
                placeholder_text = "Enter Account path"

            if security is not None:
                self.cashAccountComboBox.setEnabled(True)
                items = [
                    account.path
                    for account in self._cash_accounts
                    if account.currency == security.currency
                ]
                self.cashAccountComboBox.load_items(
                    items, icons.cash_account, placeholder_text
                )
                self.cash_account_path = cash_account_path
            else:
                self.cashAccountComboBox.setEnabled(False)
                self.cashAccountComboBox.load_items(
                    [], icons.cash_account, placeholder_text
                )

    def _initialize_signals(self) -> None:
        self.sharesDoubleSpinBox.valueChanged.connect(
            lambda: self._update_spinbox_values(self.sharesDoubleSpinBox)
        )
        self.priceDoubleSpinBox.valueChanged.connect(
            lambda: self._update_spinbox_values(self.priceDoubleSpinBox)
        )
        self.totalDoubleSpinBox.valueChanged.connect(
            lambda: self._update_spinbox_values(self.totalDoubleSpinBox)
        )
        app: QApplication = QApplication.instance()
        app.focusChanged.connect(self._focus_changed)

    def _focus_changed(self, old: QWidget, new: QWidget) -> None:
        if old not in self._spinboxes and new not in self._spinboxes:
            return
        if len(self._fixed_spinboxes) != 2:
            return
        with QSignalBlocker(self.priceDoubleSpinBox):
            shares = self.shares
            total = get_spinbox_value_as_decimal(self.totalDoubleSpinBox)
            if (shares is None or shares == 0) and len(self._fixed_spinboxes) == 2:
                self.priceDoubleSpinBox.setValue(0)
                return
            self.priceDoubleSpinBox.setValue(total / shares)

    def _update_spinbox_values(self, spinbox: QDoubleSpinBox) -> None:
        if spinbox not in self._fixed_spinboxes:
            self._fixed_spinboxes.insert(0, spinbox)
            if len(self._fixed_spinboxes) > 2:
                self._fixed_spinboxes.pop()

        if self.totalDoubleSpinBox not in self._fixed_spinboxes:
            with QSignalBlocker(self.totalDoubleSpinBox):
                shares = self.shares
                amount_per_share = self.amount_per_share
                if shares is None or amount_per_share is None:
                    self.totalDoubleSpinBox.setValue(0)
                    return
                total = shares * amount_per_share
                self.totalDoubleSpinBox.setValue(total)
        elif self.priceDoubleSpinBox not in self._fixed_spinboxes:
            with QSignalBlocker(self.priceDoubleSpinBox):
                shares = self.shares
                total = get_spinbox_value_as_decimal(self.totalDoubleSpinBox)
                if shares is None or shares == 0:
                    self.priceDoubleSpinBox.setValue(0)
                    with QSignalBlocker(self.totalDoubleSpinBox):
                        self.totalDoubleSpinBox.setValue(0)
                    return
                self.priceDoubleSpinBox.setValue(total / shares)
        elif self.sharesDoubleSpinBox not in self._fixed_spinboxes:
            with QSignalBlocker(self.sharesDoubleSpinBox):
                amount_per_share = self.amount_per_share
                total = get_spinbox_value_as_decimal(self.totalDoubleSpinBox)
                if amount_per_share is None or amount_per_share == 0:
                    self.sharesDoubleSpinBox.setValue(0)
                    with QSignalBlocker(self.totalDoubleSpinBox):
                        self.totalDoubleSpinBox.setValue(0)
                    return
                shares = total / amount_per_share
                self.sharesDoubleSpinBox.setValue(shares)
        else:
            raise ValueError("Invalid spinbox")

        value = get_spinbox_value_as_decimal(spinbox)
        if value == 0:
            self._fixed_spinboxes.remove(spinbox)

    def _set_spinboxes_currencies(self) -> None:
        security = self._get_security(self.security_name)
        self._set_spinbox_currency(security, self.priceDoubleSpinBox)
        self._set_spinbox_currency(security, self.totalDoubleSpinBox)

    def _set_spinbox_currency(
        self, security: Security | None, spinbox: QDoubleSpinBox
    ) -> None:
        if security is None:
            spinbox.setSuffix("")
        else:
            spinbox.setSuffix(" " + security.currency.code)

    def _get_cash_account(self, account_path: str) -> CashAccount | None:
        for account in self._cash_accounts:
            if account.path == account_path:
                return account
        return None

    def _get_security_account(self, account_path: str) -> SecurityAccount | None:
        for account in self._security_accounts:
            if account.path == account_path:
                return account
        return None

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
        self._setup_cash_account_combobox()

        if self.edit_mode == EditMode.EDIT_MULTIPLE_MIXED_CURRENCY:
            self.cashAccountComboBox.setEnabled(security is not None)
            self.priceDoubleSpinBox.setEnabled(security is not None)
            if security is not None:
                self.priceDoubleSpinBox.setSpecialValueText("")
            else:
                self.priceDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)

        self._set_spinboxes_currencies()
        if security is None:
            self.actionSelect_Cash_Account.setEnabled(False)
            self._set_spinbox_state(enabled=False)
            return
        self.actionSelect_Cash_Account.setEnabled(True)
        self._set_spinbox_state(enabled=True)

        self.sharesDoubleSpinBox.setDecimals(security.shares_decimals)
        self.sharesDoubleSpinBox.setSingleStep(10 ** (-security.shares_decimals))
        self._update_shares_spinbox_suffix()

        self.totalDoubleSpinBox.setDecimals(security.currency.decimals)

    def _update_shares_spinbox_suffix(self) -> None:
        self.signal_request_shares_suffix_update.emit()

    def _set_tab_order(self) -> None:
        self.setTabOrder(self.buyRadioButton, self.sellRadioButton)
        self.setTabOrder(self.sellRadioButton, self.securityComboBox)
        self.setTabOrder(self.securityComboBox, self.cashAccountComboBox)
        self.setTabOrder(self.cashAccountComboBox, self.securityAccountComboBox)
        self.setTabOrder(self.securityAccountComboBox, self.dateTimeEdit)
        self.setTabOrder(self.dateTimeEdit, self.descriptionPlainTextEdit)
        self.setTabOrder(self.descriptionPlainTextEdit, self.sharesDoubleSpinBox)
        self.setTabOrder(self.sharesDoubleSpinBox, self.priceDoubleSpinBox)
        self.setTabOrder(self.priceDoubleSpinBox, self.totalDoubleSpinBox)
        self.setTabOrder(self.totalDoubleSpinBox, self.tags_widget)

    def _set_spinbox_state(self, *, enabled: bool) -> None:
        self.sharesDoubleSpinBox.setEnabled(enabled)
        self.priceDoubleSpinBox.setEnabled(enabled)
        self.totalDoubleSpinBox.setEnabled(enabled)
