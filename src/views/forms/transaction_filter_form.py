import logging
from datetime import datetime, time
from enum import Enum, auto

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtWidgets import (
    QAbstractButton,
    QComboBox,
    QDialogButtonBox,
    QLineEdit,
    QListView,
    QWidget,
)
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import (
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.security_objects import (
    SecurityTransactionType,
    SecurityTransfer,
)
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.user_settings import user_settings
from src.views.ui_files.forms.Ui_transaction_filter_form import Ui_TransactionFilterForm


class AccountFilterMode(Enum):
    ACCOUNT_TREE = auto()
    SELECTION = auto()


class TransactionFilterForm(QWidget, Ui_TransactionFilterForm):
    signal_ok = pyqtSignal()
    signal_restore_defaults = pyqtSignal()

    signal_tags_search_text_changed = pyqtSignal(str)
    signal_payees_search_text_changed = pyqtSignal(str)

    signal_tags_select_all = pyqtSignal()
    signal_tags_unselect_all = pyqtSignal()

    signal_payees_select_all = pyqtSignal()
    signal_payees_unselect_all = pyqtSignal()

    signal_currencies_select_all = pyqtSignal()
    signal_currencies_unselect_all = pyqtSignal()

    signal_securities_select_all = pyqtSignal()
    signal_securities_unselect_all = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.resize(475, 400)

        self._initialize_window()
        self._initialize_search_boxes()
        self._initialize_signals()
        self._initialize_mode_comboboxes()

    @property
    def tags_list_view(self) -> QListView:
        return self.tagsListView

    @property
    def payee_list_view(self) -> QListView:
        return self.payeesListView

    @property
    def currency_list_view(self) -> QListView:
        return self.currencyListView

    @property
    def security_list_view(self) -> QListView:
        return self.securityListView

    @property
    def types(
        self,
    ) -> tuple[type[Transaction | CashTransactionType | SecurityTransactionType], ...]:
        _types: list[
            type[Transaction] | CashTransactionType | SecurityTransactionType
        ] = []
        if self.incomeCheckBox.isChecked():
            _types.append(CashTransactionType.INCOME)
        if self.expenseCheckBox.isChecked():
            _types.append(CashTransactionType.EXPENSE)
        if self.refundCheckBox.isChecked():
            _types.append(RefundTransaction)
        if self.cashTransferCheckBox.isChecked():
            _types.append(CashTransfer)
        if self.securityTransferCheckBox.isChecked():
            _types.append(SecurityTransfer)
        if self.buyCheckBox.isChecked():
            _types.append(SecurityTransactionType.BUY)
        if self.sellCheckBox.isChecked():
            _types.append(SecurityTransactionType.SELL)
        return tuple(_types)

    @types.setter
    def types(
        self,
        types: tuple[
            type[Transaction | CashTransactionType | SecurityTransactionType], ...
        ],
    ) -> None:
        self.incomeCheckBox.setChecked(CashTransactionType.INCOME in types)
        self.expenseCheckBox.setChecked(CashTransactionType.EXPENSE in types)
        self.refundCheckBox.setChecked(RefundTransaction in types)
        self.cashTransferCheckBox.setChecked(CashTransfer in types)
        self.securityTransferCheckBox.setChecked(SecurityTransfer in types)
        self.buyCheckBox.setChecked(SecurityTransactionType.BUY in types)
        self.sellCheckBox.setChecked(SecurityTransactionType.SELL in types)

    @property
    def date_filter_mode(self) -> FilterMode:
        return TransactionFilterForm._get_filter_mode_from_combobox(
            self.dateFilterModeComboBox
        )

    @date_filter_mode.setter
    def date_filter_mode(self, mode: FilterMode) -> None:
        self.dateFilterModeComboBox.setCurrentText(mode.name)

    @property
    def date_filter_start(self) -> datetime:
        time_min = time.min
        return (
            self.dateFilterStartDateEdit.dateTime()
            .toPyDateTime()
            .replace(
                tzinfo=user_settings.settings.time_zone,
                hour=time_min.hour,
                minute=time_min.minute,
                second=time_min.second,
                microsecond=time_min.microsecond,
            )
        )

    @date_filter_start.setter
    def date_filter_start(self, datetime_: datetime) -> None:
        self.dateFilterStartDateEdit.setDate(datetime_.date())

    @property
    def date_filter_end(self) -> datetime:
        time_max = time.max
        return (
            self.dateFilterEndDateEdit.dateTime()
            .toPyDateTime()
            .replace(
                tzinfo=user_settings.settings.time_zone,
                hour=time_max.hour,
                minute=time_max.minute,
                second=time_max.second,
                microsecond=time_max.microsecond,
            )
        )

    @date_filter_end.setter
    def date_filter_end(self, datetime_: datetime) -> None:
        self.dateFilterEndDateEdit.setDate(datetime_.date())

    @property
    def description_filter_mode(self) -> FilterMode:
        return TransactionFilterForm._get_filter_mode_from_combobox(
            self.descriptionFilterModeComboBox
        )

    @description_filter_mode.setter
    def description_filter_mode(self, mode: FilterMode) -> None:
        self.descriptionFilterModeComboBox.setCurrentText(mode.name)

    @property
    def description_filter_pattern(self) -> str:
        return self.descriptionFilterPatternLineEdit.text()

    @description_filter_pattern.setter
    def description_filter_pattern(self, pattern: str) -> None:
        self.descriptionFilterPatternLineEdit.setText(pattern)

    @property
    def account_filter_mode(self) -> AccountFilterMode:
        if self.accountsFilterTreeRadioButton.isChecked():
            return AccountFilterMode.ACCOUNT_TREE
        return AccountFilterMode.SELECTION

    @account_filter_mode.setter
    def account_filter_mode(self, mode: AccountFilterMode) -> None:
        if mode == AccountFilterMode.ACCOUNT_TREE:
            self.accountsFilterTreeRadioButton.setChecked(True)
        else:
            self.accountsFilterSelectionRadioButton.setChecked(True)

    @property
    def tagless_filter_mode(self) -> FilterMode:
        return TransactionFilterForm._get_filter_mode_from_combobox(
            self.tagLessFilterModeComboBox
        )

    @tagless_filter_mode.setter
    def tagless_filter_mode(self, mode: FilterMode) -> None:
        self.tagLessFilterModeComboBox.setCurrentText(mode.name)

    @property
    def split_tags_filter_mode(self) -> FilterMode:
        return TransactionFilterForm._get_filter_mode_from_combobox(
            self.splitTagsFilterModeComboBox
        )

    @split_tags_filter_mode.setter
    def split_tags_filter_mode(self, mode: FilterMode) -> None:
        self.splitTagsFilterModeComboBox.setCurrentText(mode.name)

    def show_form(self) -> None:
        logging.debug(f"Showing {self.__class__.__name__}")
        self.show()

    def closeEvent(self, a0: QCloseEvent) -> None:  # noqa: N802
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().closeEvent(a0)

    @staticmethod
    def _get_filter_mode_from_combobox(combobox: QComboBox) -> FilterMode:
        return FilterMode[combobox.currentText()]

    def _initialize_signals(self) -> None:
        self.dateFilterModeComboBox.currentTextChanged.connect(
            self._date_filter_mode_changed
        )
        self.descriptionFilterModeComboBox.currentTextChanged.connect(
            self._description_filter_mode_changed
        )
        self.buttonBox.clicked.connect(self._handle_button_box_click)

        self.tagsSearchLineEdit.textChanged.connect(
            lambda: self.signal_tags_search_text_changed.emit(
                self.tagsSearchLineEdit.text()
            )
        )
        self.payeesSearchLineEdit.textChanged.connect(
            lambda: self.signal_payees_search_text_changed.emit(
                self.payeesSearchLineEdit.text()
            )
        )

        self.tagsSelectAllPushButton.clicked.connect(self.signal_tags_select_all.emit)
        self.tagsUnselectAllPushButton.clicked.connect(
            self.signal_tags_unselect_all.emit
        )

        self.payeesSelectAllPushButton.clicked.connect(
            self.signal_payees_select_all.emit
        )
        self.payeesUnselectAllPushButton.clicked.connect(
            self.signal_payees_unselect_all.emit
        )

        self.currencyFilterSelectAllPushButton.clicked.connect(
            self.signal_currencies_select_all.emit
        )
        self.currencyFilterUnselectAllPushButton.clicked.connect(
            self.signal_currencies_unselect_all.emit
        )

        self.securityFilterSelectAllPushButton.clicked.connect(
            self.signal_securities_select_all.emit
        )
        self.securityFilterUnselectAllPushButton.clicked.connect(
            self.signal_securities_unselect_all.emit
        )

        self.tagLessFilterModeComboBox.currentTextChanged.connect(
            self._tagless_filter_mode_changed
        )

    def _initialize_window(self) -> None:
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle("Filter Transaction Table")
        self.setWindowIcon(QIcon("icons_16:funnel.png"))

    def _initialize_search_boxes(self) -> None:
        self.tagsSearchLineEdit.addAction(
            QIcon("icons_16:magnifier.png"), QLineEdit.ActionPosition.LeadingPosition
        )
        self.payeesSearchLineEdit.addAction(
            QIcon("icons_16:magnifier.png"), QLineEdit.ActionPosition.LeadingPosition
        )

    def _initialize_mode_comboboxes(self) -> None:
        self._initialize_mode_combobox(self.dateFilterModeComboBox)
        self._initialize_mode_combobox(self.descriptionFilterModeComboBox)
        self._initialize_mode_combobox(self.tagLessFilterModeComboBox)
        self._initialize_mode_combobox(self.splitTagsFilterModeComboBox)
        self._initialize_mode_combobox(self.splitCategoriesFilterModeComboBox)

    @staticmethod
    def _initialize_mode_combobox(combobox: QComboBox) -> None:
        for mode in FilterMode:
            combobox.addItem(mode.name)
        combobox.setToolTip(
            f"{FilterMode.OFF.name}: {FilterMode.OFF.value}\n"
            f"{FilterMode.KEEP.name}: {FilterMode.KEEP.value}\n"
            f"{FilterMode.DISCARD.name}: {FilterMode.DISCARD.value}"
        )

    def _date_filter_mode_changed(self) -> None:
        mode = self.date_filter_mode
        self.dateFilterStartDateEdit.setEnabled(mode != FilterMode.OFF)
        self.dateFilterEndDateEdit.setEnabled(mode != FilterMode.OFF)

    def _description_filter_mode_changed(self) -> None:
        mode = self.description_filter_mode
        self.descriptionFilterPatternLineEdit.setEnabled(mode != FilterMode.OFF)

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_ok.emit()
        elif role == QDialogButtonBox.ButtonRole.ResetRole:
            self.signal_restore_defaults.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.close()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")

    def _tagless_filter_mode_changed(self) -> None:
        mode = self.tagless_filter_mode
        self.specificTagsFilterGroupBox.setEnabled(mode != FilterMode.KEEP)
        if mode == FilterMode.KEEP:
            self.splitTagsFilterModeComboBox.setCurrentText(FilterMode.OFF.name)
        self.splitTagsFilterModeComboBox.setEnabled(mode != FilterMode.KEEP)
