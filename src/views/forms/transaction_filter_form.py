from collections.abc import Collection
from datetime import datetime, time, timedelta
from decimal import Decimal
from enum import Enum, auto

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QContextMenuEvent, QCursor
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
from src.models.model_objects.cash_objects import (
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.security_objects import (
    SecurityTransactionType,
)
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.user_settings import user_settings
from src.view_models.checkable_category_tree_model import CategorySelectionMode
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.constants import monospace_font
from src.views.ui_files.forms.Ui_transaction_filter_form import Ui_TransactionFilterForm
from src.views.utilities.helper_functions import (
    convert_datetime_format_to_qt,
    get_spinbox_value_as_decimal,
)


class AccountFilterMode(Enum):
    ACCOUNT_TREE = auto()
    SELECTION = auto()


class TransactionFilterForm(CustomWidget, Ui_TransactionFilterForm):
    signal_ok = pyqtSignal()
    signal_restore_defaults = pyqtSignal()
    signal_close = pyqtSignal()

    signal_accounts_search_text_changed = pyqtSignal(str)
    signal_tags_search_text_changed = pyqtSignal(str)
    signal_payees_search_text_changed = pyqtSignal(str)
    signal_income_categories_search_text_changed = pyqtSignal(str)
    signal_expense_categories_search_text_changed = pyqtSignal(str)
    signal_income_and_expense_categories_search_text_changed = pyqtSignal(str)
    signal_currencies_search_text_changed = pyqtSignal(str)
    signal_securities_search_text_changed = pyqtSignal(str)

    signal_types_select_all = pyqtSignal()
    signal_types_unselect_all = pyqtSignal()

    signal_accounts_select_all = pyqtSignal()
    signal_accounts_unselect_all = pyqtSignal()
    signal_accounts_select_all_cash_accounts_below = pyqtSignal()
    signal_accounts_select_all_security_accounts_below = pyqtSignal()
    signal_accounts_expand_all_below = pyqtSignal()

    signal_tags_select_all = pyqtSignal()
    signal_tags_unselect_all = pyqtSignal()
    signal_tags_update_number_selected = pyqtSignal()

    signal_payees_select_all = pyqtSignal()
    signal_payees_unselect_all = pyqtSignal()
    signal_payees_update_number_selected = pyqtSignal()

    signal_category_selection_mode_changed = pyqtSignal()
    signal_income_categories_select_all = pyqtSignal()
    signal_income_categories_unselect_all = pyqtSignal()
    signal_expense_categories_select_all = pyqtSignal()
    signal_expense_categories_unselect_all = pyqtSignal()
    signal_income_and_expense_categories_select_all = pyqtSignal()
    signal_income_and_expense_categories_unselect_all = pyqtSignal()
    signal_categories_update_number_selected = pyqtSignal()

    signal_currencies_select_all = pyqtSignal()
    signal_currencies_unselect_all = pyqtSignal()
    signal_currencies_update_number_selected = pyqtSignal()

    signal_securities_select_all = pyqtSignal()
    signal_securities_unselect_all = pyqtSignal()
    signal_securities_update_number_selected = pyqtSignal()

    signal_help = pyqtSignal()

    def __init__(
        self,
        parent: QWidget,
        base_currency_code: str,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.resize(550, 620)

        self._initialize_window()
        self._initialize_search_boxes()
        self._initialize_buttons()
        self._initialize_signals()
        self._initialize_mode_comboboxes()
        self._initialize_category_filter_selection_mode_combobox()
        self._initialize_account_filter_actions()
        self._initialize_context_menu_events()
        self.base_currency_code = base_currency_code
        self._description_filter_mode_changed()
        self._date_filter_mode_changed()
        self._account_filter_mode_changed()
        self._specific_categories_filter_mode_changed()
        self._tagless_filter_mode_changed()
        self._specific_tags_filter_mode_changed()
        self._payee_filter_mode_changed()
        self._currency_filter_mode_changed()
        self._security_filter_mode_changed()
        self._uuid_filter_mode_changed()
        self.uuidFilterPlainTextEdit.setFont(monospace_font)

    @property
    def types_list_view(self) -> QListView:
        return self.typeFilterListView

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
    def description_filter_ignore_case(self) -> bool:
        return not self.descriptionFilterMatchCaseCheckBox.isChecked()

    @description_filter_ignore_case.setter
    def description_filter_ignore_case(self, value: bool) -> None:
        self.descriptionFilterMatchCaseCheckBox.setChecked(not value)

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
    def specific_tags_filter_mode(self) -> FilterMode:
        return TransactionFilterForm._get_filter_mode_from_combobox(
            self.specificTagsFilterModeComboBox
        )

    @specific_tags_filter_mode.setter
    def specific_tags_filter_mode(self, mode: FilterMode) -> None:
        self.specificTagsFilterModeComboBox.setCurrentText(mode.name)

    @property
    def split_tags_filter_mode(self) -> FilterMode:
        return TransactionFilterForm._get_filter_mode_from_combobox(
            self.splitTagsFilterModeComboBox
        )

    @split_tags_filter_mode.setter
    def split_tags_filter_mode(self, mode: FilterMode) -> None:
        self.splitTagsFilterModeComboBox.setCurrentText(mode.name)

    @property
    def payee_filter_mode(self) -> bool:
        return TransactionFilterForm._get_filter_mode_from_combobox(
            self.payeesFilterModeComboBox
        )

    @payee_filter_mode.setter
    def payee_filter_mode(self, mode: FilterMode) -> None:
        self.payeesFilterModeComboBox.setCurrentText(mode.name)

    @property
    def security_filter_mode(self) -> bool:
        return TransactionFilterForm._get_filter_mode_from_combobox(
            self.securityFilterModeComboBox
        )

    @security_filter_mode.setter
    def security_filter_mode(self, mode: FilterMode) -> None:
        self.securityFilterModeComboBox.setCurrentText(mode.name)

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
        return get_spinbox_value_as_decimal(self.cashAmountFilterMinimumDoubleSpinBox)

    @cash_amount_filter_minimum.setter
    def cash_amount_filter_minimum(self, amount: Decimal) -> None:
        self.cashAmountFilterMinimumDoubleSpinBox.setValue(amount)

    @property
    def cash_amount_filter_maximum(self) -> Decimal:
        return get_spinbox_value_as_decimal(self.cashAmountFilterMaximumDoubleSpinBox)

    @cash_amount_filter_maximum.setter
    def cash_amount_filter_maximum(self, amount: Decimal) -> None:
        self.cashAmountFilterMaximumDoubleSpinBox.setValue(amount)

    @property
    def currency_filter_mode(self) -> FilterMode:
        return TransactionFilterForm._get_filter_mode_from_combobox(
            self.currencyFilterModeComboBox
        )

    @currency_filter_mode.setter
    def currency_filter_mode(self, mode: FilterMode) -> None:
        self.currencyFilterModeComboBox.setCurrentText(mode.name)

    @property
    def specific_categories_filter_mode(self) -> FilterMode:
        return TransactionFilterForm._get_filter_mode_from_combobox(
            self.specificCategoryFilterModeComboBox
        )

    @specific_categories_filter_mode.setter
    def specific_categories_filter_mode(self, mode: FilterMode) -> None:
        self.specificCategoryFilterModeComboBox.setCurrentText(mode.name)

    @property
    def category_selection_mode(self) -> CategorySelectionMode:
        if (
            self.specificCategoryFilterSelectionModeComboBox.currentText()
            == "Hierarchical"
        ):
            return CategorySelectionMode.HIERARCHICAL
        if (
            self.specificCategoryFilterSelectionModeComboBox.currentText()
            == "Individual"
        ):
            return CategorySelectionMode.INDIVIDUAL
        raise ValueError("Unknown selection mode")

    @category_selection_mode.setter
    def category_selection_mode(self, mode: CategorySelectionMode) -> None:
        if mode == CategorySelectionMode.HIERARCHICAL:
            self.specificCategoryFilterSelectionModeComboBox.setCurrentText(
                "Hierarchical"
            )
        else:
            self.specificCategoryFilterSelectionModeComboBox.setCurrentText(
                "Individual"
            )

    @property
    def multiple_categories_filter_mode(self) -> FilterMode:
        return TransactionFilterForm._get_filter_mode_from_combobox(
            self.multipleCategoriesFilterModeComboBox
        )

    @multiple_categories_filter_mode.setter
    def multiple_categories_filter_mode(self, mode: FilterMode) -> None:
        self.multipleCategoriesFilterModeComboBox.setCurrentText(mode.name)

    @property
    def uuid_filter_mode(self) -> FilterMode:
        return TransactionFilterForm._get_filter_mode_from_combobox(
            self.uuidFilterModeComboBox
        )

    @uuid_filter_mode.setter
    def uuid_filter_mode(self, mode: FilterMode) -> None:
        self.uuidFilterModeComboBox.setCurrentText(mode.name)

    @property
    def uuids(self) -> tuple[str]:
        uuids = self.uuidFilterPlainTextEdit.toPlainText().split(",")
        uuids = [uuid.strip() for uuid in uuids if uuid.strip()]
        return tuple(uuids)

    @uuids.setter
    def uuids(self, uuids: Collection[str]) -> None:
        self.uuidFilterPlainTextEdit.setPlainText(",\n".join(uuids))

    def show_form(self) -> None:
        self._update_date_edit_display_format()
        super().show_form()

    def _update_cash_amount_filter_state(self) -> None:
        if self._base_currency_code:
            self.cashAmountGroupBox.setEnabled(True)
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
        self.currencyFilterSearchLineEdit.textChanged.connect(
            self.signal_currencies_search_text_changed.emit
        )
        self.securityFilterSearchLineEdit.textChanged.connect(
            self.signal_securities_search_text_changed.emit
        )

        self.typeFilterSelectAllPushButton.clicked.connect(
            self.signal_types_select_all.emit
        )
        self.typeFilterUnselectAllPushButton.clicked.connect(
            self.signal_types_unselect_all.emit
        )

        self.specificCategoryFilterSelectionModeComboBox.currentTextChanged.connect(
            self.signal_category_selection_mode_changed.emit
        )
        self.specificCategoryFilterModeComboBox.currentTextChanged.connect(
            self._specific_categories_filter_mode_changed
        )

        self.tagLessFilterModeComboBox.currentTextChanged.connect(
            self._tagless_filter_mode_changed
        )
        self.specificTagsFilterModeComboBox.currentTextChanged.connect(
            self._specific_tags_filter_mode_changed
        )

        self.payeesFilterModeComboBox.currentTextChanged.connect(
            self._payee_filter_mode_changed
        )

        self.cashAmountFilterModeComboBox.currentTextChanged.connect(
            self._update_cash_amount_filter_state
        )
        self.cashAmountFilterMaximumDoubleSpinBox.valueChanged.connect(
            self._update_cash_amount_filter_minimum
        )

        self.currencyFilterModeComboBox.currentTextChanged.connect(
            self._currency_filter_mode_changed
        )
        self.securityFilterModeComboBox.currentTextChanged.connect(
            self._security_filter_mode_changed
        )
        self.uuidFilterModeComboBox.currentTextChanged.connect(
            self._uuid_filter_mode_changed
        )

    def _initialize_window(self) -> None:
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle("Filter Transactions")
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
        self.currencyFilterSearchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )
        self.securityFilterSearchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )

    def _initialize_mode_comboboxes(self) -> None:
        self._initialize_mode_combobox(self.dateFilterModeComboBox)
        self._initialize_mode_combobox(self.descriptionFilterModeComboBox)
        self._initialize_mode_combobox(self.tagLessFilterModeComboBox)
        self._initialize_mode_combobox(self.splitTagsFilterModeComboBox)
        self._initialize_mode_combobox(self.multipleCategoriesFilterModeComboBox)
        self._initialize_mode_combobox(self.cashAmountFilterModeComboBox)
        self._initialize_mode_combobox(self.specificTagsFilterModeComboBox)
        self._initialize_mode_combobox(self.specificCategoryFilterModeComboBox)
        self._initialize_mode_combobox(self.currencyFilterModeComboBox)
        self._initialize_mode_combobox(self.uuidFilterModeComboBox)
        self._initialize_mode_combobox(self.securityFilterModeComboBox)
        self._initialize_mode_combobox(self.payeesFilterModeComboBox)

    def _initialize_category_filter_selection_mode_combobox(self) -> None:
        self.specificCategoryFilterSelectionModeComboBox.addItem("Hierarchical")
        self.specificCategoryFilterSelectionModeComboBox.addItem("Individual")

    @staticmethod
    def _initialize_mode_combobox(combobox: QComboBox) -> None:
        with QSignalBlocker(combobox):
            for mode in FilterMode:
                combobox.addItem(mode.name)

    def _initialize_buttons(self) -> None:
        self.thisMonthPushButton.clicked.connect(self._set_this_month)
        self.lastMonthPushButton.clicked.connect(self._set_last_month)
        self.thisYearPushButton.clicked.connect(self._set_this_year)
        self.lastYearPushButton.clicked.connect(self._set_last_year)

        self.actionSelectAllAccounts = QAction("Select All", self)
        self.actionUnselectAllAccounts = QAction("Unselect All", self)
        self.actionExpandAllAccounts = QAction("Expand All", self)
        self.actionExpandAllIncomeCategories = QAction("Expand All", self)
        self.actionExpandAllExpenseCategories = QAction("Expand All", self)
        self.actionExpandAllIncomeAndExpenseCategories = QAction("Expand All", self)
        self.actionCollapseAllAccounts = QAction("Collapse All", self)
        self.actionCollapseAllIncomeCategories = QAction("Collapse All", self)
        self.actionCollapseAllExpenseCategories = QAction("Collapse All", self)
        self.actionCollapseAllIncomeAndExpenseCategories = QAction("Collapse All", self)
        self.actionSelectAllIncomeCategories = QAction("Select All", self)
        self.actionUnselectAllIncomeCategories = QAction("Unselect All", self)
        self.actionSelectAllExpenseCategories = QAction("Select All", self)
        self.actionUnselectAllExpenseCategories = QAction("Unselect All", self)
        self.actionSelectAllIncomeAndExpenseCategories = QAction("Select All", self)
        self.actionUnselectAllIncomeAndExpenseCategories = QAction("Unselect All", self)
        self.actionSelectAllTags = QAction("Select All", self)
        self.actionUnselectAllTags = QAction("Unselect All", self)
        self.actionSelectAllPayees = QAction("Select All", self)
        self.actionUnselectAllPayees = QAction("Unselect All", self)
        self.actionSelectAllCurrencies = QAction("Select All", self)
        self.actionUnselectAllCurrencies = QAction("Unselect All", self)
        self.actionSelectAllSecurities = QAction("Select All", self)
        self.actionUnselectAllSecurities = QAction("Unselect All", self)

        self.actionSelectAllAccounts.setIcon(icons.select_all)
        self.actionUnselectAllAccounts.setIcon(icons.unselect_all)
        self.actionExpandAllAccounts.setIcon(icons.expand)
        self.actionExpandAllIncomeCategories.setIcon(icons.expand)
        self.actionExpandAllExpenseCategories.setIcon(icons.expand)
        self.actionExpandAllIncomeAndExpenseCategories.setIcon(icons.expand)
        self.actionCollapseAllAccounts.setIcon(icons.collapse)
        self.actionCollapseAllIncomeCategories.setIcon(icons.collapse)
        self.actionCollapseAllExpenseCategories.setIcon(icons.collapse)
        self.actionCollapseAllIncomeAndExpenseCategories.setIcon(icons.collapse)
        self.actionSelectAllIncomeCategories.setIcon(icons.select_all)
        self.actionUnselectAllIncomeCategories.setIcon(icons.unselect_all)
        self.actionSelectAllExpenseCategories.setIcon(icons.select_all)
        self.actionUnselectAllExpenseCategories.setIcon(icons.unselect_all)
        self.actionSelectAllIncomeAndExpenseCategories.setIcon(icons.select_all)
        self.actionUnselectAllIncomeAndExpenseCategories.setIcon(icons.unselect_all)
        self.actionSelectAllTags.setIcon(icons.select_all)
        self.actionUnselectAllTags.setIcon(icons.unselect_all)
        self.actionSelectAllPayees.setIcon(icons.select_all)
        self.actionUnselectAllPayees.setIcon(icons.unselect_all)
        self.typeFilterSelectAllPushButton.setIcon(icons.select_all)
        self.typeFilterUnselectAllPushButton.setIcon(icons.unselect_all)
        self.actionSelectAllCurrencies.setIcon(icons.select_all)
        self.actionUnselectAllCurrencies.setIcon(icons.unselect_all)
        self.actionSelectAllSecurities.setIcon(icons.select_all)
        self.actionUnselectAllSecurities.setIcon(icons.unselect_all)

        self.actionSelectAllAccounts.triggered.connect(
            self.signal_accounts_select_all.emit
        )
        self.actionUnselectAllAccounts.triggered.connect(
            self.signal_accounts_unselect_all.emit
        )
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
        self.actionSelectAllIncomeCategories.triggered.connect(
            self.signal_income_categories_select_all.emit
        )
        self.actionUnselectAllIncomeCategories.triggered.connect(
            self.signal_income_categories_unselect_all.emit
        )
        self.actionSelectAllExpenseCategories.triggered.connect(
            self.signal_expense_categories_select_all.emit
        )
        self.actionUnselectAllExpenseCategories.triggered.connect(
            self.signal_expense_categories_unselect_all.emit
        )
        self.actionSelectAllIncomeAndExpenseCategories.triggered.connect(
            self.signal_income_and_expense_categories_select_all.emit
        )
        self.actionUnselectAllIncomeAndExpenseCategories.triggered.connect(
            self.signal_income_and_expense_categories_unselect_all.emit
        )
        self.actionSelectAllTags.triggered.connect(self.signal_tags_select_all.emit)
        self.actionUnselectAllTags.triggered.connect(self.signal_tags_unselect_all.emit)
        self.actionSelectAllPayees.triggered.connect(self.signal_payees_select_all.emit)
        self.actionUnselectAllPayees.triggered.connect(
            self.signal_payees_unselect_all.emit
        )
        self.actionSelectAllCurrencies.triggered.connect(
            self.signal_currencies_select_all.emit
        )
        self.actionUnselectAllCurrencies.triggered.connect(
            self.signal_currencies_unselect_all.emit
        )
        self.actionSelectAllSecurities.triggered.connect(
            self.signal_securities_select_all.emit
        )
        self.actionUnselectAllSecurities.triggered.connect(
            self.signal_securities_unselect_all.emit
        )

        self.accountsFilterSelectAllToolButton.setDefaultAction(
            self.actionSelectAllAccounts
        )
        self.accountsFilterUnselectAllToolButton.setDefaultAction(
            self.actionUnselectAllAccounts
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
        self.incomeCategoriesSelectAllToolButton.setDefaultAction(
            self.actionSelectAllIncomeCategories
        )
        self.incomeCategoriesUnselectAllToolButton.setDefaultAction(
            self.actionUnselectAllIncomeCategories
        )
        self.expenseCategoriesSelectAllToolButton.setDefaultAction(
            self.actionSelectAllExpenseCategories
        )
        self.expenseCategoriesUnselectAllToolButton.setDefaultAction(
            self.actionUnselectAllExpenseCategories
        )
        self.incomeAndExpenseCategoriesSelectAllToolButton.setDefaultAction(
            self.actionSelectAllIncomeAndExpenseCategories
        )
        self.incomeAndExpenseCategoriesUnselectAllToolButton.setDefaultAction(
            self.actionUnselectAllIncomeAndExpenseCategories
        )
        self.specificTagsFilterSelectAllToolButton.setDefaultAction(
            self.actionSelectAllTags
        )
        self.specificTagsFilterUnselectAllToolButton.setDefaultAction(
            self.actionUnselectAllTags
        )
        self.payeesSelectAllToolButton.setDefaultAction(self.actionSelectAllPayees)
        self.payeesUnselectAllToolButton.setDefaultAction(self.actionUnselectAllPayees)
        self.currencyFilterSelectAllToolButton.setDefaultAction(
            self.actionSelectAllCurrencies
        )
        self.currencyFilterUnselectAllToolButton.setDefaultAction(
            self.actionUnselectAllCurrencies
        )
        self.securityFilterSelectAllToolButton.setDefaultAction(
            self.actionSelectAllSecurities
        )
        self.securityFilterUnselectAllToolButton.setDefaultAction(
            self.actionUnselectAllSecurities
        )

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_ok.emit()
        elif role == QDialogButtonBox.ButtonRole.ResetRole:
            self.signal_restore_defaults.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.signal_close.emit()
        elif role == QDialogButtonBox.ButtonRole.HelpRole:
            self.signal_help.emit()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")

    def _date_filter_mode_changed(self) -> None:
        mode = self.date_filter_mode
        self.dateFilterStartDateEdit.setEnabled(mode != FilterMode.OFF)
        self.dateFilterEndDateEdit.setEnabled(mode != FilterMode.OFF)
        self.thisMonthPushButton.setEnabled(mode != FilterMode.OFF)
        self.lastMonthPushButton.setEnabled(mode != FilterMode.OFF)
        self.thisYearPushButton.setEnabled(mode != FilterMode.OFF)
        self.lastYearPushButton.setEnabled(mode != FilterMode.OFF)

    def _description_filter_mode_changed(self) -> None:
        mode = self.description_filter_mode
        self.descriptionFilterPatternLineEdit.setEnabled(mode != FilterMode.OFF)
        self.descriptionFilterMatchCaseCheckBox.setEnabled(mode != FilterMode.OFF)

    def _account_filter_mode_changed(self) -> None:
        mode = self.account_filter_mode
        self.accountsFilterGroupBox.setEnabled(mode == AccountFilterMode.SELECTION)

    def _specific_categories_filter_mode_changed(self) -> None:
        mode = self.specific_categories_filter_mode
        self.specificCategoryFilterSelectionModeLabel.setEnabled(mode != FilterMode.OFF)
        self.specificCategoryFilterSelectionModeComboBox.setEnabled(
            mode != FilterMode.OFF
        )
        self.categoriesTypeTabWidget.setEnabled(mode != FilterMode.OFF)
        self.signal_categories_update_number_selected.emit()

    def _tagless_filter_mode_changed(self) -> None:
        mode = self.tagless_filter_mode
        self.specificTagsFilterGroupBox.setEnabled(mode != FilterMode.KEEP)
        if mode == FilterMode.KEEP:
            self.splitTagsFilterModeComboBox.setCurrentText(FilterMode.OFF.name)
        self.splitTagsFilterModeComboBox.setEnabled(mode != FilterMode.KEEP)

    def _specific_tags_filter_mode_changed(self) -> None:
        mode = self.specific_tags_filter_mode
        self.actionSelectAllTags.setEnabled(mode != FilterMode.OFF)
        self.actionUnselectAllTags.setEnabled(mode != FilterMode.OFF)
        self.tagsSearchLineEdit.setEnabled(mode != FilterMode.OFF)
        self.tagsListView.setEnabled(mode != FilterMode.OFF)
        self.signal_tags_update_number_selected.emit()

    def _payee_filter_mode_changed(self) -> None:
        mode = self.payee_filter_mode
        self.actionSelectAllPayees.setEnabled(mode != FilterMode.OFF)
        self.actionUnselectAllPayees.setEnabled(mode != FilterMode.OFF)
        self.payeesListView.setEnabled(mode != FilterMode.OFF)
        self.payeesSearchLineEdit.setEnabled(mode != FilterMode.OFF)
        self.signal_payees_update_number_selected.emit()

    def _currency_filter_mode_changed(self) -> None:
        mode = self.currency_filter_mode
        self.actionSelectAllCurrencies.setEnabled(mode != FilterMode.OFF)
        self.actionUnselectAllCurrencies.setEnabled(mode != FilterMode.OFF)
        self.currencyFilterSearchLineEdit.setEnabled(mode != FilterMode.OFF)
        self.currencyListView.setEnabled(mode != FilterMode.OFF)
        self.signal_currencies_update_number_selected.emit()

    def _security_filter_mode_changed(self) -> None:
        mode = self.security_filter_mode
        self.actionSelectAllSecurities.setEnabled(mode != FilterMode.OFF)
        self.actionUnselectAllSecurities.setEnabled(mode != FilterMode.OFF)
        self.securityListView.setEnabled(mode != FilterMode.OFF)
        self.securityFilterSearchLineEdit.setEnabled(mode != FilterMode.OFF)
        self.signal_securities_update_number_selected.emit()

    def _uuid_filter_mode_changed(self) -> None:
        mode = self.uuid_filter_mode
        self.uuidFilterPlainTextEdit.setEnabled(mode != FilterMode.OFF)

    def _initialize_account_filter_actions(self) -> None:
        self.actionSelectAllCashAccountsBelow = QAction(
            "Select All Cash Accounts Below", self
        )
        self.actionSelectAllSecurityAccountsBelow = QAction(
            "Select All Security Accounts Below", self
        )
        self.actionExpandAllAccountItemsBelow = QAction("Expand All Below", self)

        self.actionSelectAllCashAccountsBelow.setIcon(icons.select_cash_accounts)
        self.actionSelectAllSecurityAccountsBelow.setIcon(
            icons.select_security_accounts
        )
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

    def _create_account_filter_context_menu(
        self,
        event: QContextMenuEvent,  # noqa: ARG002
    ) -> None:
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

    def _update_cash_amount_filter_minimum(self) -> None:
        self.cashAmountFilterMinimumDoubleSpinBox.setMaximum(
            self.cash_amount_filter_maximum
        )

    def set_selected_category_numbers(
        self,
        income_selected: int,
        income_total: int,
        expense_selected: int,
        expense_total: int,
        income_and_expense_selected: int,
        income_and_expense_total: int,
    ) -> None:
        """Set the number of currently selected categories in tab names.
        Pass a negative number if no number is to be shown."""

        if self.specific_categories_filter_mode != FilterMode.OFF:
            income_text = f"Income ({income_selected} / {income_total})"
            expense_text = f"Expense ({expense_selected} / {expense_total})"
            income_and_expense_text = (
                f"Income and Expense ({income_and_expense_selected} "
                f"/ {income_and_expense_total})"
            )
        else:
            income_text = "Income"
            expense_text = "Expense"
            income_and_expense_text = "Income and Expense"

        self.categoriesTypeTabWidget.setTabText(0, income_text)
        self.categoriesTypeTabWidget.setTabText(1, expense_text)
        self.categoriesTypeTabWidget.setTabText(2, income_and_expense_text)

    def set_selected_tags_number(self, selected: int, total: int) -> None:
        if self.specific_tags_filter_mode != FilterMode.OFF:
            self.specificTagsFilterGroupBox.setTitle(
                f"Specific Tags Filter ({selected:n} / {total:n})"
            )
        else:
            self.specificTagsFilterGroupBox.setTitle("Specific Tags Filter")

    def set_selected_payees_number(self, selected: int, total: int) -> None:
        if self.payee_filter_mode != FilterMode.OFF:
            self.payeeFilterGroupBox.setTitle(
                f"Payee Filter ({selected:n} / {total:n})"
            )
        else:
            self.payeeFilterGroupBox.setTitle("Payee Filter")

    def set_selected_currencies_number(self, selected: int, total: int) -> None:
        if self.currency_filter_mode != FilterMode.OFF:
            self.currencyFilterGroupBox.setTitle(
                f"Currency Filter ({selected:n} / {total:n})"
            )
        else:
            self.currencyFilterGroupBox.setTitle("Currency Filter")

    def set_selected_securities_number(self, selected: int, total: int) -> None:
        if self.security_filter_mode != FilterMode.OFF:
            self.securityFilterGroupBox.setTitle(
                f"Security Filter ({selected:n} / {total:n})"
            )
        else:
            self.securityFilterGroupBox.setTitle("Security Filter")

    def _update_date_edit_display_format(self) -> None:
        display_format = convert_datetime_format_to_qt(
            user_settings.settings.general_date_format
        )
        self.dateFilterStartDateEdit.setDisplayFormat(display_format)
        self.dateFilterEndDateEdit.setDisplayFormat(display_format)

    def _set_this_month(self) -> None:
        today = datetime.now(user_settings.settings.time_zone)
        self.dateFilterStartDateEdit.setDate(today.replace(day=1))
        self.dateFilterEndDateEdit.setDate(today)

    def _set_last_month(self) -> None:
        today = datetime.now(user_settings.settings.time_zone)
        last_day_of_last_month = today.replace(day=1) - timedelta(days=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1)
        self.dateFilterStartDateEdit.setDate(first_day_of_last_month)
        self.dateFilterEndDateEdit.setDate(last_day_of_last_month)

    def _set_this_year(self) -> None:
        today = datetime.now(user_settings.settings.time_zone)
        self.dateFilterStartDateEdit.setDate(today.replace(month=1, day=1))
        self.dateFilterEndDateEdit.setDate(today)

    def _set_last_year(self) -> None:
        today = datetime.now(user_settings.settings.time_zone)
        last_day_of_last_year = today.replace(day=1, month=1) - timedelta(days=1)
        first_day_of_last_year = last_day_of_last_year.replace(day=1, month=1)
        self.dateFilterStartDateEdit.setDate(first_day_of_last_year)
        self.dateFilterEndDateEdit.setDate(last_day_of_last_year)
