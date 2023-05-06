import logging
from collections.abc import Collection
from datetime import datetime, time
from decimal import Decimal
from enum import Enum, auto

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QCloseEvent, QContextMenuEvent, QCursor
from PyQt6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QComboBox,
    QDialogButtonBox,
    QLineEdit,
    QListView,
    QMenu,
    QTreeView,
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
from src.view_models.checkable_category_tree_model import CategorySelectionMode
from src.views import icons
from src.views.ui_files.forms.Ui_transaction_filter_form import Ui_TransactionFilterForm

CASH_RELATED_TRANSACTION_TYPES = (
    CashTransactionType.INCOME,
    CashTransactionType.EXPENSE,
    CashTransfer,
    RefundTransaction,
    SecurityTransactionType.BUY,
    SecurityTransactionType.SELL,
)


class AccountFilterMode(Enum):
    ACCOUNT_TREE = auto()
    SELECTION = auto()


# TODO: print Filter summary button?
# TODO: improve Type Filter selection (list view?)


class TransactionFilterForm(QWidget, Ui_TransactionFilterForm):
    signal_ok = pyqtSignal()
    signal_restore_defaults = pyqtSignal()

    signal_accounts_search_text_changed = pyqtSignal(str)
    signal_tags_search_text_changed = pyqtSignal(str)
    signal_payees_search_text_changed = pyqtSignal(str)
    signal_income_categories_search_text_changed = pyqtSignal(str)
    signal_expense_categories_search_text_changed = pyqtSignal(str)
    signal_income_and_expense_categories_search_text_changed = pyqtSignal(str)

    signal_accounts_select_all = pyqtSignal()
    signal_accounts_unselect_all = pyqtSignal()
    signal_accounts_select_all_cash_accounts_below = pyqtSignal()
    signal_accounts_select_all_security_accounts_below = pyqtSignal()
    signal_accounts_expand_all_below = pyqtSignal()

    signal_tags_select_all = pyqtSignal()
    signal_tags_unselect_all = pyqtSignal()

    signal_payees_select_all = pyqtSignal()
    signal_payees_unselect_all = pyqtSignal()

    signal_category_selection_mode_changed = pyqtSignal()
    signal_income_categories_select_all = pyqtSignal()
    signal_income_categories_unselect_all = pyqtSignal()
    signal_expense_categories_select_all = pyqtSignal()
    signal_expense_categories_unselect_all = pyqtSignal()
    signal_income_and_expense_categories_select_all = pyqtSignal()
    signal_income_and_expense_categories_unselect_all = pyqtSignal()

    signal_currencies_select_all = pyqtSignal()
    signal_currencies_unselect_all = pyqtSignal()

    signal_securities_select_all = pyqtSignal()
    signal_securities_unselect_all = pyqtSignal()

    def __init__(
        self,
        parent: QWidget,
        base_currency_code: str,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.resize(475, 400)

        self._initialize_window()
        self._initialize_search_boxes()
        self._initialize_tool_buttons()
        self._initialize_signals()
        self._initialize_mode_comboboxes()
        self._initialize_account_filter_actions()
        self._initialize_context_menu_events()
        self.base_currency_code = base_currency_code
        self._description_filter_mode_changed()
        self._date_filter_mode_changed()
        self._account_filter_mode_changed()
        self._tagless_filter_mode_changed()

    @property
    def account_tree_view(self) -> QTreeView:
        return self.accountsTreeView

    @property
    def tags_list_view(self) -> QListView:
        return self.tagsListView

    @property
    def payee_list_view(self) -> QListView:
        return self.payeesListView

    @property
    def income_category_tree_view(self) -> QTreeView:
        return self.incomeCategoriesTreeView

    @property
    def expense_category_tree_view(self) -> QTreeView:
        return self.expenseCategoriesTreeView

    @property
    def income_and_expense_category_tree_view(self) -> QTreeView:
        return self.incomeAndExpenseCategoriesTreeView

    @property
    def currency_list_view(self) -> QListView:
        return self.currencyListView

    @property
    def security_list_view(self) -> QListView:
        return self.securityListView

    @property
    def payee_filter_active(self) -> bool:
        return self.payeeFilterGroupBox.isChecked()

    @payee_filter_active.setter
    def payee_filter_active(self, value: bool) -> None:
        self.payeeFilterGroupBox.setChecked(value)

    @property
    def category_filters_active(self) -> bool:
        return self.categoryFiltersGroupBox.isChecked()

    @category_filters_active.setter
    def category_filters_active(self, value: bool) -> None:
        self.categoryFiltersGroupBox.setChecked(value)

    @property
    def currency_filter_active(self) -> bool:
        return self.currencyFilterGroupBox.isChecked()

    @currency_filter_active.setter
    def currency_filter_active(self, value: bool) -> None:
        self.currencyFilterGroupBox.setChecked(value)

    @property
    def security_filter_active(self) -> bool:
        return self.securityFilterGroupBox.isChecked()

    @security_filter_active.setter
    def security_filter_active(self, value: bool) -> None:
        self.securityFilterGroupBox.setChecked(value)

    @property
    def types(
        self,
    ) -> set[type[Transaction | CashTransactionType | SecurityTransactionType]]:
        _types: set[
            type[Transaction] | CashTransactionType | SecurityTransactionType
        ] = set()
        if self.incomeCheckBox.isChecked():
            _types.add(CashTransactionType.INCOME)
        if self.expenseCheckBox.isChecked():
            _types.add(CashTransactionType.EXPENSE)
        if self.refundCheckBox.isChecked():
            _types.add(RefundTransaction)
        if self.cashTransferCheckBox.isChecked():
            _types.add(CashTransfer)
        if self.securityTransferCheckBox.isChecked():
            _types.add(SecurityTransfer)
        if self.buyCheckBox.isChecked():
            _types.add(SecurityTransactionType.BUY)
        if self.sellCheckBox.isChecked():
            _types.add(SecurityTransactionType.SELL)
        return _types

    @types.setter
    def types(
        self,
        types: Collection[
            type[Transaction | CashTransactionType | SecurityTransactionType]
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
        self._account_filter_mode_changed()

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

    @property
    def base_currency_code(self) -> str:
        return self._base_currency_code

    @base_currency_code.setter
    def base_currency_code(self, base_currency_code: str) -> None:
        self._base_currency_code = base_currency_code
        self.cashAmountFilterMaximumDoubleSpinBox.setSuffix(" " + base_currency_code)
        self.cashAmountFilterMinimumDoubleSpinBox.setSuffix(" " + base_currency_code)
        self._update_cash_amount_filter_state()

    @property
    def cash_amount_filter_mode(self) -> FilterMode:
        return TransactionFilterForm._get_filter_mode_from_combobox(
            self.cashAmountFilterModeComboBox
        )

    @cash_amount_filter_mode.setter
    def cash_amount_filter_mode(self, mode: FilterMode) -> None:
        self.cashAmountFilterModeComboBox.setCurrentText(mode.name)

    @property
    def cash_amount_filter_minimum(self) -> Decimal:
        text = self.cashAmountFilterMinimumDoubleSpinBox.text()
        suffix = self.cashAmountFilterMinimumDoubleSpinBox.suffix()
        if suffix in text:
            text = text.removesuffix(suffix)
        if "," in text:
            text = text.replace(",", "")
        return Decimal(text)

    @cash_amount_filter_minimum.setter
    def cash_amount_filter_minimum(self, amount: Decimal) -> None:
        self.cashAmountFilterMinimumDoubleSpinBox.setValue(amount)

    @property
    def cash_amount_filter_maximum(self) -> Decimal:
        text = self.cashAmountFilterMaximumDoubleSpinBox.text()
        suffix = self.cashAmountFilterMaximumDoubleSpinBox.suffix()
        if suffix in text:
            text = text.removesuffix(suffix)
        if "," in text:
            text = text.replace(",", "")
        return Decimal(text)

    @cash_amount_filter_maximum.setter
    def cash_amount_filter_maximum(self, amount: Decimal) -> None:
        self.cashAmountFilterMaximumDoubleSpinBox.setValue(amount)

    @property
    def category_selection_mode(self) -> CategorySelectionMode:
        if self.hierarchicalSelectionModeRadioButton.isChecked():
            return CategorySelectionMode.HIERARCHICAL
        if self.individualSelectionModeRadioButton.isChecked():
            return CategorySelectionMode.INDIVIDUAL
        raise ValueError("Unknown selection mode")

    @category_selection_mode.setter
    def category_selection_mode(self, mode: CategorySelectionMode) -> None:
        if mode == CategorySelectionMode.HIERARCHICAL:
            self.hierarchicalSelectionModeRadioButton.setChecked(True)
        else:
            self.individualSelectionModeRadioButton.setChecked(True)

    @property
    def multiple_categories_filter_mode(self) -> FilterMode:
        return TransactionFilterForm._get_filter_mode_from_combobox(
            self.multipleCategoriesFilterModeComboBox
        )

    @multiple_categories_filter_mode.setter
    def multiple_categories_filter_mode(self, mode: FilterMode) -> None:
        self.multipleCategoriesFilterModeComboBox.setCurrentText(mode.name)

    def show_form(self) -> None:
        logging.debug(f"Showing {self.__class__.__name__}")
        self.show()

    def closeEvent(self, a0: QCloseEvent) -> None:  # noqa: N802
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().closeEvent(a0)

    def _update_cash_amount_filter_state(self) -> None:
        if self._base_currency_code:
            any_cash_related = any(
                type_ in CASH_RELATED_TRANSACTION_TYPES for type_ in self.types
            )
            self.cashAmountGroupBox.setEnabled(any_cash_related)
            self.cashAmountFilterMinimumDoubleSpinBox.setEnabled(
                self.cash_amount_filter_mode != FilterMode.OFF
            )
            self.cashAmountFilterMaximumDoubleSpinBox.setEnabled(
                self.cash_amount_filter_mode != FilterMode.OFF
            )
        else:
            self.cashAmountGroupBox.setEnabled(False)
            self.cashAmountFilterModeComboBox.setCurrentText(FilterMode.OFF.name)

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
        self.accountsFilterRadioButtonGroup = QButtonGroup()
        self.accountsFilterRadioButtonGroup.addButton(
            self.accountsFilterTreeRadioButton
        )
        self.accountsFilterRadioButtonGroup.addButton(
            self.accountsFilterSelectionRadioButton
        )
        self.accountsFilterRadioButtonGroup.buttonClicked.connect(
            self._account_filter_mode_changed
        )

        self.buttonBox.clicked.connect(self._handle_button_box_click)

        self.accountsSearchLineEdit.textChanged.connect(
            self.signal_accounts_search_text_changed.emit
        )
        self.tagsSearchLineEdit.textChanged.connect(
            self.signal_tags_search_text_changed.emit
        )
        self.payeesSearchLineEdit.textChanged.connect(
            self.signal_payees_search_text_changed.emit
        )
        self.incomeCategoriesSearchLineEdit.textChanged.connect(
            self.signal_income_categories_search_text_changed.emit
        )
        self.expenseCategoriesSearchLineEdit.textChanged.connect(
            self.signal_expense_categories_search_text_changed.emit
        )
        self.incomeAndExpenseCategoriesSearchLineEdit.textChanged.connect(
            self.signal_income_and_expense_categories_search_text_changed.emit
        )

        self.accountsFilterSelectAllPushButton.clicked.connect(
            self.signal_accounts_select_all.emit
        )
        self.accountsFilterUnselectAllPushButton.clicked.connect(
            self.signal_accounts_unselect_all.emit
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

        self.specificCategoryFilterSelectionModeRadioButtonGroup = QButtonGroup()
        self.specificCategoryFilterSelectionModeRadioButtonGroup.addButton(
            self.hierarchicalSelectionModeRadioButton
        )
        self.specificCategoryFilterSelectionModeRadioButtonGroup.addButton(
            self.individualSelectionModeRadioButton
        )
        self.specificCategoryFilterSelectionModeRadioButtonGroup.buttonClicked.connect(
            self.signal_category_selection_mode_changed.emit
        )

        self.incomeCategoriesSelectAllPushButton.clicked.connect(
            self.signal_income_categories_select_all.emit
        )
        self.incomeCategoriesUnselectAllPushButton.clicked.connect(
            self.signal_income_categories_unselect_all.emit
        )
        self.expenseCategoriesSelectAllPushButton.clicked.connect(
            self.signal_expense_categories_select_all.emit
        )
        self.expenseCategoriesUnselectAllPushButton.clicked.connect(
            self.signal_expense_categories_unselect_all.emit
        )
        self.incomeAndExpenseCategoriesSelectAllPushButton.clicked.connect(
            self.signal_income_and_expense_categories_select_all.emit
        )
        self.incomeAndExpenseCategoriesUnselectAllPushButton.clicked.connect(
            self.signal_income_and_expense_categories_unselect_all.emit
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

        self.cashAmountFilterModeComboBox.currentTextChanged.connect(
            self._update_cash_amount_filter_state
        )

        self.incomeCheckBox.toggled.connect(self._update_cash_amount_filter_state)
        self.expenseCheckBox.toggled.connect(self._update_cash_amount_filter_state)
        self.refundCheckBox.toggled.connect(self._update_cash_amount_filter_state)
        self.cashTransferCheckBox.toggled.connect(self._update_cash_amount_filter_state)
        self.securityTransferCheckBox.toggled.connect(
            self._update_cash_amount_filter_state
        )
        self.buyCheckBox.toggled.connect(self._update_cash_amount_filter_state)
        self.sellCheckBox.toggled.connect(self._update_cash_amount_filter_state)

    def _initialize_window(self) -> None:
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle("Filter Transaction Table")
        self.setWindowIcon(icons.filter_)

    def _initialize_search_boxes(self) -> None:
        self.accountsSearchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )
        self.tagsSearchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )
        self.payeesSearchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )
        self.incomeCategoriesSearchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )
        self.expenseCategoriesSearchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )
        self.incomeAndExpenseCategoriesSearchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )

    def _initialize_mode_comboboxes(self) -> None:
        self._initialize_mode_combobox(self.dateFilterModeComboBox)
        self._initialize_mode_combobox(self.descriptionFilterModeComboBox)
        self._initialize_mode_combobox(self.tagLessFilterModeComboBox)
        self._initialize_mode_combobox(self.splitTagsFilterModeComboBox)
        self._initialize_mode_combobox(self.multipleCategoriesFilterModeComboBox)
        self._initialize_mode_combobox(self.cashAmountFilterModeComboBox)

    @staticmethod
    def _initialize_mode_combobox(combobox: QComboBox) -> None:
        with QSignalBlocker(combobox):
            for mode in FilterMode:
                combobox.addItem(mode.name)

    def _initialize_tool_buttons(self) -> None:
        self.actionExpandAllAccounts = QAction("Expand All", self)
        self.actionExpandAllIncomeCategories = QAction("Expand All", self)
        self.actionExpandAllExpenseCategories = QAction("Expand All", self)
        self.actionExpandAllIncomeAndExpenseCategories = QAction("Expand All", self)
        self.actionCollapseAllAccounts = QAction("Collapse All", self)
        self.actionCollapseAllIncomeCategories = QAction("Collapse All", self)
        self.actionCollapseAllExpenseCategories = QAction("Collapse All", self)
        self.actionCollapseAllIncomeAndExpenseCategories = QAction("Collapse All", self)

        self.actionExpandAllAccounts.setIcon(icons.expand)
        self.actionExpandAllIncomeCategories.setIcon(icons.expand)
        self.actionExpandAllExpenseCategories.setIcon(icons.expand)
        self.actionExpandAllIncomeAndExpenseCategories.setIcon(icons.expand)
        self.actionCollapseAllAccounts.setIcon(icons.collapse)
        self.actionCollapseAllIncomeCategories.setIcon(icons.collapse)
        self.actionCollapseAllExpenseCategories.setIcon(icons.collapse)
        self.actionCollapseAllIncomeAndExpenseCategories.setIcon(icons.collapse)

        self.actionExpandAllAccounts.triggered.connect(self.accountsTreeView.expandAll)
        self.actionExpandAllIncomeCategories.triggered.connect(
            self.incomeCategoriesTreeView.expandAll
        )
        self.actionExpandAllExpenseCategories.triggered.connect(
            self.expenseCategoriesTreeView.expandAll
        )
        self.actionExpandAllIncomeAndExpenseCategories.triggered.connect(
            self.incomeAndExpenseCategoriesTreeView.expandAll
        )
        self.actionCollapseAllAccounts.triggered.connect(
            self.accountsTreeView.collapseAll
        )
        self.actionCollapseAllIncomeCategories.triggered.connect(
            self.incomeCategoriesTreeView.collapseAll
        )
        self.actionCollapseAllExpenseCategories.triggered.connect(
            self.expenseCategoriesTreeView.collapseAll
        )
        self.actionCollapseAllIncomeAndExpenseCategories.triggered.connect(
            self.incomeAndExpenseCategoriesTreeView.collapseAll
        )

        self.accountsFilterExpandAllToolButton.setDefaultAction(
            self.actionExpandAllAccounts
        )
        self.incomeCategoriesExpandAllToolButton.setDefaultAction(
            self.actionExpandAllIncomeCategories
        )
        self.expenseCategoriesExpandAllToolButton.setDefaultAction(
            self.actionExpandAllExpenseCategories
        )
        self.incomeAndExpenseCategoriesExpandAllToolButton.setDefaultAction(
            self.actionExpandAllIncomeAndExpenseCategories
        )
        self.accountsFilterCollapseAllToolButton.setDefaultAction(
            self.actionCollapseAllAccounts
        )
        self.incomeCategoriesCollapseAllToolButton.setDefaultAction(
            self.actionCollapseAllIncomeCategories
        )
        self.expenseCategoriesCollapseAllToolButton.setDefaultAction(
            self.actionCollapseAllExpenseCategories
        )
        self.incomeAndExpenseCategoriesCollapseAllToolButton.setDefaultAction(
            self.actionCollapseAllIncomeAndExpenseCategories
        )

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

    def _date_filter_mode_changed(self) -> None:
        mode = self.date_filter_mode
        self.dateFilterStartDateEdit.setEnabled(mode != FilterMode.OFF)
        self.dateFilterEndDateEdit.setEnabled(mode != FilterMode.OFF)

    def _description_filter_mode_changed(self) -> None:
        mode = self.description_filter_mode
        self.descriptionFilterPatternLineEdit.setEnabled(mode != FilterMode.OFF)

    def _account_filter_mode_changed(self) -> None:
        mode = self.account_filter_mode
        self.accountsFilterGroupBox.setEnabled(mode == AccountFilterMode.SELECTION)

    def _tagless_filter_mode_changed(self) -> None:
        mode = self.tagless_filter_mode
        self.specificTagsFilterGroupBox.setEnabled(mode != FilterMode.KEEP)
        if mode == FilterMode.KEEP:
            self.splitTagsFilterModeComboBox.setCurrentText(FilterMode.OFF.name)
        self.splitTagsFilterModeComboBox.setEnabled(mode != FilterMode.KEEP)

    def _initialize_account_filter_actions(self) -> None:
        self.actionSelectAllCashAccountsBelow = QAction(
            "Select All Cash Accounts Below", self
        )
        self.actionSelectAllSecurityAccountsBelow = QAction(
            "Select All Security Accounts Below", self
        )
        self.actionExpandAllAccountItemsBelow = QAction("Expand All Below", self)

        self.actionSelectAllCashAccountsBelow.setIcon(icons.cash_account)
        self.actionSelectAllSecurityAccountsBelow.setIcon(icons.security_account)
        self.actionExpandAllAccountItemsBelow.setIcon(icons.expand_below)

        self.actionSelectAllCashAccountsBelow.triggered.connect(
            self.signal_accounts_select_all_cash_accounts_below.emit
        )
        self.actionSelectAllSecurityAccountsBelow.triggered.connect(
            self.signal_accounts_select_all_security_accounts_below.emit
        )
        self.actionExpandAllAccountItemsBelow.triggered.connect(
            self.signal_accounts_expand_all_below.emit
        )

    def _create_account_filter_context_menu(self, event: QContextMenuEvent) -> None:
        del event
        self.menu = QMenu(self)
        self.menu.addAction(self.actionSelectAllCashAccountsBelow)
        self.menu.addAction(self.actionSelectAllSecurityAccountsBelow)
        self.menu.addSeparator()
        self.menu.addAction(self.actionExpandAllAccountItemsBelow)
        self.menu.popup(QCursor.pos())

    def _initialize_context_menu_events(self) -> None:
        self.accountsTreeView.contextMenuEvent = (
            self._create_account_filter_context_menu
        )

    def set_account_filter_action_states(self, *, account_group_selected: bool) -> None:
        self.actionSelectAllCashAccountsBelow.setEnabled(account_group_selected)
        self.actionSelectAllSecurityAccountsBelow.setEnabled(account_group_selected)
        self.actionExpandAllAccountItemsBelow.setEnabled(account_group_selected)
