import logging
from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, auto

from PyQt6.QtCore import QSignalBlocker, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractButton,
    QComboBox,
    QCompleter,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from src.models.model_objects.cash_objects import CashAccount, CashTransactionType
from src.models.user_settings import user_settings
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.dialogs.select_item_dialog import ask_user_for_selection
from src.views.ui_files.dialogs.Ui_cash_transaction_dialog import (
    Ui_CashTransactionDialog,
)
from src.views.widgets.add_attribute_row_widget import AddAttributeRowWidget
from src.views.widgets.description_plain_text_edit import DescriptionPlainTextEdit
from src.views.widgets.label_widget import LabelWidget
from src.views.widgets.single_category_row_widget import SingleCategoryRowWidget
from src.views.widgets.single_tag_row_widget import SingleTagRowWidget
from src.views.widgets.smart_completer import SmartCompleter
from src.views.widgets.split_category_row_widget import SplitCategoryRowWidget
from src.views.widgets.split_tag_row_widget import SplitTagRowWidget


class EditMode(Enum):
    ADD = auto()
    EDIT_SINGLE = auto()
    EDIT_MULTIPLE = auto()
    EDIT_MULTIPLE_MIXED_CURRENCY = auto()

    @staticmethod
    def get_multiple_edit_values() -> tuple["EditMode", ...]:
        return (EditMode.EDIT_MULTIPLE, EditMode.EDIT_MULTIPLE_MIXED_CURRENCY)


# REFACTOR: refactor this dialog (messy code)


class CashTransactionDialog(CustomDialog, Ui_CashTransactionDialog):
    KEEP_CURRENT_VALUES = "Keep current values"

    signal_do_and_close = pyqtSignal()
    signal_do_and_continue = pyqtSignal()

    def __init__(  # noqa: PLR0913
        self,
        parent: QWidget,
        accounts: Collection[CashAccount],
        payees: Collection[str],
        categories_income: Collection[str],
        categories_expense: Collection[str],
        tag_names: Collection[str],
        descriptions: Collection[str],
        *,
        edit_mode: EditMode,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.split_categories_vertical_layout = None
        self.split_tags_vertical_layout = None

        self._edit_mode = edit_mode
        self._tag_names = tag_names
        self._accounts = accounts

        self.descriptionPlainTextEdit = DescriptionPlainTextEdit(descriptions)
        self.description_label = QLabel("Description")
        self.formLayout.insertRow(
            4, self.description_label, self.descriptionPlainTextEdit
        )

        self._type = CashTransactionType.INCOME
        self.incomeRadioButton.setChecked(True)

        self._categories_income = categories_income
        self._categories_expense = categories_expense

        self._initialize_single_category_row()
        self._initialize_single_tag_row()

        self.incomeRadioButton.toggled.connect(
            lambda: self._setup_categories_combobox(keep_text=False)
        )
        self.expenseRadioButton.toggled.connect(
            lambda: self._setup_categories_combobox(keep_text=False)
        )

        if edit_mode != EditMode.ADD:
            self.dateEdit.setSpecialValueText(self.KEEP_CURRENT_VALUES)
            self.dateEdit.setMinimumDate(date(1900, 1, 1))
            self.amountDoubleSpinBox.setSpecialValueText(self.KEEP_CURRENT_VALUES)

        self._payees = sorted(payees, key=str.lower)
        for payee in payees:
            self.payeeComboBox.addItem(payee)

        self._completer = SmartCompleter(self._payees, self)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.activated.connect(self._handle_payee_completion)
        self._completer.setWidget(self.payeeComboBox.lineEdit())
        self.payeeComboBox.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.payeeComboBox.editTextChanged.connect(self._handle_payee_text_changed)

        self._initialize_accounts_combobox(accounts)
        self._initialize_window()
        self._initialize_actions()
        self._initialize_placeholders()

        if edit_mode == EditMode.EDIT_MULTIPLE:
            self._disable_type()
            pass
        elif edit_mode == EditMode.EDIT_MULTIPLE_MIXED_CURRENCY:
            self._disable_type()
            self._disable_account()
            self._disable_amount()
            self._category_rows[0].enable_split(enable=False)
            self._tag_rows[0].enable_split(enable=False)
            pass

        self.amountDoubleSpinBox.valueChanged.connect(self._amount_changed)
        self._amount_changed()

        self._set_maximum_amounts(0)
        self._set_tab_order()

    @property
    def type_(self) -> CashTransactionType:
        if self.incomeRadioButton.isChecked():
            return CashTransactionType.INCOME
        if self.expenseRadioButton.isChecked():
            return CashTransactionType.EXPENSE
        raise ValueError("No radio button checked.")

    @type_.setter
    def type_(self, type_: CashTransactionType) -> None:
        if type_ == CashTransactionType.INCOME:
            self.incomeRadioButton.setChecked(True)
            return
        if type_ == CashTransactionType.EXPENSE:
            self.expenseRadioButton.setChecked(True)
            return
        raise ValueError("Invalid type_ value.")

    @property
    def account_path(self) -> str | None:
        text = self.accountsComboBox.currentText()
        if text == self.KEEP_CURRENT_VALUES:
            return None
        return text

    @account_path.setter
    def account_path(self, account: str) -> None:
        self.accountsComboBox.setCurrentText(account)

    @property
    def payee(self) -> str | None:
        text = self.payeeComboBox.currentText()
        return text if text else None

    @payee.setter
    def payee(self, payee: str) -> None:
        with QSignalBlocker(self.payeeComboBox):
            self.payeeComboBox.setCurrentText(payee)

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
        if self._edit_mode in EditMode.get_multiple_edit_values():
            return text if text else None
        return text

    @description.setter
    def description(self, description: str) -> None:
        self.descriptionPlainTextEdit.setPlainText(description)

    @property
    def amount(self) -> Decimal | None:
        text = self.amountDoubleSpinBox.cleanText().replace(",", "")
        if text == self.KEEP_CURRENT_VALUES:
            return None
        return Decimal(text)

    @amount.setter
    def amount(self, amount: Decimal) -> None:
        self.amountDoubleSpinBox.setValue(amount)

    @property
    def min_amount(self) -> Decimal:
        return Decimal(self.amountDoubleSpinBox.minimum())

    @property
    def currency_code(self) -> str:
        return self._currency_code

    @currency_code.setter
    def currency_code(self, code: str) -> None:
        self._currency_code = code
        self.amountDoubleSpinBox.setSuffix(" " + code)
        if len(self._category_rows) > 1:
            for row in self._category_rows:
                row.currency_code = code

    @property
    def amount_decimals(self) -> int:
        self.amountDoubleSpinBox.decimals()

    @amount_decimals.setter
    def amount_decimals(self, value: int) -> None:
        self._decimals = value
        self.amountDoubleSpinBox.setDecimals(value)
        if len(self._category_rows) > 1:
            for row in self._category_rows:
                row.amount_decimals = value

    @property
    def category_amount_pairs(
        self,
    ) -> tuple[tuple[str | None, Decimal | None], ...] | None:
        if len(self._category_rows) == 1:
            if self._category_rows[0].category is None:
                if self.amount is not None:
                    return ((None, self.amount),)
                return None
            return ((self._category_rows[0].category, self.amount),)
        return tuple((row.category, row.amount) for row in self._category_rows)

    @category_amount_pairs.setter
    def category_amount_pairs(
        self, pairs: Collection[tuple[str, Decimal | None]]
    ) -> None:
        if len(pairs) == 0:
            self._initialize_single_category_row()
        elif len(pairs) == 1:
            category, amount = pairs[0]
            self._initialize_single_category_row()
            row = self._category_rows[0]
            row.category = category
            if amount is not None:
                self.amount = amount
        else:
            no_of_pairs = len(pairs)
            total_amount = sum(amount for _, amount in pairs)
            self.amount = total_amount
            self._split_categories(user=False)
            remaining_rows = no_of_pairs - 2
            for _ in range(remaining_rows):
                self._add_split_category_row()
            for index in range(no_of_pairs):
                self._category_rows[index].category = pairs[index][0]
                self._category_rows[index].amount = pairs[index][1]

    @property
    def tag_amount_pairs(self) -> tuple[tuple[str, Decimal], ...] | None:
        if len(self._tag_rows) == 1:
            row = self._tag_rows[0]
            if isinstance(row, SingleTagRowWidget):
                if (
                    self._edit_mode in EditMode.get_multiple_edit_values()
                    and not row.tag_names
                ):
                    return None
                return tuple((tag, self.amount) for tag in row.tag_names)
        return tuple((row.tag_name, row.amount) for row in self._tag_rows)

    @tag_amount_pairs.setter
    def tag_amount_pairs(self, pairs: Collection[tuple[str, Decimal]]) -> None:
        single_row = all(amount == self.amount for _, amount in pairs)
        tags = [tag for tag, _ in pairs]
        if single_row:
            self._initialize_single_tag_row()
            self._tag_rows[0].tag_names = tags
        else:
            self._split_tags(user=False)
            remaining_rows = len(tags) - 1
            for _ in range(remaining_rows):
                self._add_split_tag_row()
            for index in range(len(tags)):
                self._tag_rows[index].tag_name = pairs[index][0]
                self._tag_rows[index].amount = pairs[index][1]

    def reject(self) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().reject()

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

    def _disable_type(self) -> None:
        self.incomeRadioButton.setEnabled(False)
        self.expenseRadioButton.setEnabled(False)

    def _disable_account(self) -> None:
        self.accountsComboBox.setCurrentText(self.KEEP_CURRENT_VALUES)
        self.accountsComboBox.setEnabled(False)

    def _disable_amount(self) -> None:
        self.amountDoubleSpinBox.setValue(0)
        self.amountDoubleSpinBox.setEnabled(False)

    def _initialize_window(self) -> None:
        if self._edit_mode != EditMode.ADD:
            if self._edit_mode in EditMode.get_multiple_edit_values():
                self.setWindowTitle("Edit Cash Transactions")
            else:
                self.setWindowTitle("Edit Cash Transaction")
            self.setWindowIcon(icons.edit_cash_transaction)
            self.buttonBox.addButton("OK", QDialogButtonBox.ButtonRole.AcceptRole)
        else:
            self.setWindowTitle("Add Cash Transaction")
            self.setWindowIcon(icons.add_cash_transaction)
            self.buttonBox.addButton(
                "Create && Continue", QDialogButtonBox.ButtonRole.ApplyRole
            )
            self.buttonBox.addButton(
                "Create && Close", QDialogButtonBox.ButtonRole.AcceptRole
            )
        self.buttonBox.clicked.connect(self._handle_button_box_click)
        self.buttonBox.addButton("Close", QDialogButtonBox.ButtonRole.RejectRole)

    def _initialize_actions(self) -> None:
        self.actionSelect_Account.setIcon(icons.cash_account)
        self.actionSelect_Account.triggered.connect(self._get_account)
        self.accountsToolButton.setDefaultAction(self.actionSelect_Account)

    def _initialize_accounts_combobox(self, accounts: Collection[CashAccount]) -> None:
        if (
            self._edit_mode == EditMode.EDIT_MULTIPLE
            or self._edit_mode == EditMode.EDIT_MULTIPLE_MIXED_CURRENCY
        ):
            self.accountsComboBox.addItem(self.KEEP_CURRENT_VALUES)
        for account in accounts:
            self.accountsComboBox.addItem(icons.cash_account, account.path)

        self.accountsComboBox.currentTextChanged.connect(self._account_changed)
        self._account_changed()

    def _initialize_placeholders(self) -> None:
        if self._edit_mode in EditMode.get_multiple_edit_values():
            self.descriptionPlainTextEdit.setPlaceholderText(
                "Leave empty to keep current values"
            )
            self.payeeComboBox.lineEdit().setPlaceholderText(
                "Leave empty to keep current values"
            )
            if len(self._tag_rows) == 1:
                self._tag_rows[0].set_placeholder_text(
                    "Leave empty to keep current values"
                )
        else:
            self.payeeComboBox.lineEdit().setPlaceholderText("Enter Payee name")
        self.payeeComboBox.setCurrentIndex(-1)

    def _setup_categories_combobox(self, *, keep_text: bool) -> None:
        for row in self._category_rows:
            if self.type_ == CashTransactionType.INCOME:
                row.load_categories(
                    self._categories_income, keep_current_text=keep_text
                )
            else:
                row.load_categories(
                    self._categories_expense, keep_current_text=keep_text
                )

    def _initialize_single_category_row(self) -> None:
        if hasattr(self, "_category_rows") and len(self._category_rows) == 1:
            return

        edit = self._edit_mode != EditMode.ADD
        row = SingleCategoryRowWidget(self, edit=edit)
        self._category_rows = [row]
        self.formLayout.insertRow(6, LabelWidget(self, "Category"), row)
        self._setup_categories_combobox(keep_text=True)
        row.signal_split_categories.connect(lambda: self._split_categories(user=True))
        self._set_tab_order()

    def _split_categories(self, *, user: bool) -> None:
        if hasattr(self, "_category_rows") and len(self._category_rows) > 1:
            return

        if user:
            logging.debug("Splitting Category rows")

        current_category = self._category_rows[0].category

        self.formLayout.removeRow(6)
        self.split_categories_vertical_layout = QVBoxLayout(None)

        self._category_rows = []
        for _ in range(2):
            row = SplitCategoryRowWidget(self)
            row.amount_decimals = self._decimals
            row.maximum_amount = self.amount
            row.currency_code = self._currency_code
            self._category_rows.append(row)
            self.split_categories_vertical_layout.addWidget(row)

        self.formLayout.insertRow(
            6, LabelWidget(self, "Categories"), self.split_categories_vertical_layout
        )

        self._setup_categories_combobox(keep_text=True)
        self._category_rows[0].category = current_category

        for row in self._category_rows:
            row.signal_remove_row.connect(self._remove_split_category_row)
            row.signal_amount_changed.connect(self._split_category_amount_changed)

        self.add_row_widget = AddAttributeRowWidget(self)
        self.add_row_widget.signal_add_row.connect(self._add_split_category_row)
        self.split_categories_vertical_layout.addWidget(self.add_row_widget)

        self._fixed_split_category_rows: list[SplitCategoryRowWidget] = []
        self._equalize_split_category_amounts()
        self._set_tab_order()

    def _add_split_category_row(self) -> None:
        logging.debug("Adding split Category row")

        if self.split_categories_vertical_layout is None:
            raise ValueError("Vertical split Categories Layout is None.")

        row = SplitCategoryRowWidget(self)
        row.amount_decimals = self._decimals
        row.maximum_amount = self.amount
        row.currency_code = self._currency_code
        self._category_rows.append(row)
        index = self.split_categories_vertical_layout.count() - 1
        self.split_categories_vertical_layout.insertWidget(index, row)
        self._setup_categories_combobox(keep_text=True)
        row.signal_remove_row.connect(self._remove_split_category_row)
        row.signal_amount_changed.connect(self._split_category_amount_changed)
        self._equalize_split_category_amounts()
        self._set_tab_order()

    def _remove_split_category_row(self, removed_row: SplitCategoryRowWidget) -> None:
        logging.debug("Removing single Category row")

        if self.split_categories_vertical_layout is None:
            raise ValueError("Vertical split Categories Layout is None.")

        no_of_rows = self.split_categories_vertical_layout.count() - 1
        if no_of_rows == 2:  # noqa: PLR2004
            self._category_rows.remove(removed_row)
            remaining_category = self._category_rows[0].category
            logging.debug("Resetting Category rows, initializing single row")
            self._reset_category_rows()
            self._initialize_single_category_row()
            self._category_rows[0].category = remaining_category
            return

        self.split_categories_vertical_layout.removeWidget(removed_row)
        self._category_rows.remove(removed_row)
        if removed_row in self._fixed_split_category_rows:
            self._fixed_split_category_rows.remove(removed_row)
        removed_row.deleteLater()
        self._equalize_split_category_amounts()
        self._set_tab_order()

    def _reset_category_rows(self) -> None:
        self.formLayout.removeRow(6)
        self.split_categories_vertical_layout = None
        self._category_rows: list[SplitCategoryRowWidget | SingleCategoryRowWidget] = []

    def _initialize_single_tag_row(self) -> None:
        if (
            hasattr(self, "_tag_rows")
            and len(self._tag_rows) == 1
            and isinstance(self._tag_rows[0], SingleTagRowWidget)
        ):
            return

        row = SingleTagRowWidget(self, self._tag_names)
        self._tag_rows: list[SingleTagRowWidget | SplitTagRowWidget] = [row]
        self.formLayout.insertRow(7, LabelWidget(self, "Tags"), row)
        row.signal_split_tags.connect(lambda: self._split_tags(user=True))
        self._set_tab_order()

    def _split_tags(self, *, user: bool) -> None:
        if hasattr(self, "_tag_rows") and len(self._tag_rows) > 1:
            return

        if user:
            logging.debug("Splitting Tag rows")

        current_tags = self._tag_rows[0].tag_names
        if len(current_tags) == 0:
            current_tags = [""]

        self.formLayout.removeRow(7)
        self.split_tags_vertical_layout = QVBoxLayout(None)
        self._tag_rows: list[SingleTagRowWidget | SplitTagRowWidget] = []
        for tag in current_tags:
            row = SplitTagRowWidget(self, self._tag_names, self.amount)
            row.amount_decimals = self._decimals
            row.maximum_amount = self.amount
            row.currency_code = self._currency_code
            row.tag_name = tag
            row.amount = self.amount
            self._tag_rows.append(row)
            self.split_tags_vertical_layout.addWidget(row)

        self.formLayout.insertRow(
            7, LabelWidget(self, "Tags"), self.split_tags_vertical_layout
        )

        for row in self._tag_rows:
            row.signal_remove_row.connect(self._remove_split_tag_row)

        self.add_row_widget = AddAttributeRowWidget(self)
        self.add_row_widget.signal_add_row.connect(self._add_split_tag_row)
        self.split_tags_vertical_layout.addWidget(self.add_row_widget)
        self._set_tab_order()

    def _add_split_tag_row(self) -> None:
        logging.debug("Adding split Tag row")

        if self.split_tags_vertical_layout is None:
            raise ValueError("Vertical split Tags Layout is None.")

        row = SplitTagRowWidget(self, self._tag_names, self.amount)
        row.amount_decimals = self._decimals
        row.currency_code = self._currency_code
        row.maximum_amount = self.amount
        row.amount = self.amount
        self._tag_rows.append(row)
        index = self.split_tags_vertical_layout.count() - 1
        self.split_tags_vertical_layout.insertWidget(index, row)
        row.signal_remove_row.connect(self._remove_split_tag_row)
        self._set_tab_order()

    def _remove_split_tag_row(self, removed_row: SplitTagRowWidget) -> None:
        logging.debug("Removing split Tag row")

        if self.split_tags_vertical_layout is None:
            raise ValueError("Vertical split Tags Layout is None.")

        no_of_rows = self.split_tags_vertical_layout.count() - 1
        if no_of_rows == 1:
            remaining_tag = self._tag_rows[0].tag_name
            logging.debug("Resetting split Tag rows, initializing single row")
            self._reset_tag_rows()
            self._initialize_single_tag_row()
            self._tag_rows[0].tag_names = [remaining_tag]
            return

        self.split_tags_vertical_layout.removeWidget(removed_row)
        self._tag_rows.remove(removed_row)
        removed_row.deleteLater()
        self._set_tab_order()

    def _reset_tag_rows(self) -> None:
        self.formLayout.removeRow(7)
        self.split_tags_vertical_layout = None
        self._tag_rows: list[SingleTagRowWidget | SplitTagRowWidget] = []

    def _get_account(self) -> None:
        account_paths = [account.path for account in self._accounts]
        account = ask_user_for_selection(
            self,
            account_paths,
            "Select Account",
            icons.cash_account,
        )
        self.account_path = account if account else self.account_path

    def _set_maximum_amounts(self, max_amount: Decimal) -> None:
        split_category_rows = [
            row
            for row in self._category_rows
            if isinstance(row, SplitCategoryRowWidget)
        ]
        for row in split_category_rows:
            row.maximum_amount = max_amount

        split_tag_rows = [
            row for row in self._tag_rows if isinstance(row, SplitTagRowWidget)
        ]
        for row in split_tag_rows:
            row.maximum_amount = max_amount

    def _equalize_split_category_amounts(self) -> None:
        no_of_rows = len(self._category_rows)
        if self.amount is None:
            raise ValueError("Expected Decimal, received None.")
        portion = self.amount / no_of_rows
        for row in self._category_rows:
            row.amount = portion

        row_sum = sum(row.amount for row in self._category_rows)
        difference = self.amount - row_sum
        self._category_rows[0].amount += difference

    def _amount_changed(self) -> None:
        new_amount = self.amount

        if self._edit_mode == EditMode.EDIT_MULTIPLE:
            if new_amount is None and len(self._category_rows) > 1:
                self._reset_category_rows()
                self._initialize_single_category_row()
            if new_amount is None and not isinstance(
                self._tag_rows[0], SingleTagRowWidget
            ):
                self._reset_tag_rows()
                self._initialize_single_tag_row()
            is_amount_none = new_amount is None
            if len(self._category_rows) == 1:
                self._category_rows[0].enable_split(enable=not is_amount_none)
                self._category_rows[0].require_category(required=not is_amount_none)
            if len(self._tag_rows) == 1:
                self._tag_rows[0].enable_split(enable=not is_amount_none)

        if new_amount is not None:
            self._set_maximum_amounts(new_amount)
        if len(self._category_rows) > 1:
            self._equalize_split_category_amounts()
        if isinstance(self._tag_rows[0], SplitTagRowWidget):
            for row in self._tag_rows:
                row.set_total_amount(self.amount)

    def _split_category_amount_changed(self, row: SplitCategoryRowWidget) -> None:
        no_of_rows = len(self._category_rows)

        if row not in self._fixed_split_category_rows:
            self._fixed_split_category_rows.append(row)
        if len(self._fixed_split_category_rows) == no_of_rows:
            self._fixed_split_category_rows.pop(0)

        no_of_fixed_rows = len(self._fixed_split_category_rows)
        no_of_adjusted_rows = no_of_rows - no_of_fixed_rows

        remaining_amount = self.amount - sum(
            row.amount for row in self._fixed_split_category_rows
        )
        adjust_amounts = remaining_amount / no_of_adjusted_rows

        adjustable_rows = [
            row
            for row in self._category_rows
            if row not in self._fixed_split_category_rows
        ]
        for row in adjustable_rows:
            row.amount = adjust_amounts

        row_sum = sum(row.amount for row in self._category_rows)
        difference = self.amount - row_sum
        adjustable_rows[0].amount += difference

    def _set_tab_order(self) -> None:
        self.setTabOrder(self.incomeRadioButton, self.expenseRadioButton)
        self.setTabOrder(self.expenseRadioButton, self.accountsComboBox)
        self.setTabOrder(self.accountsComboBox, self.accountsToolButton)
        self.setTabOrder(self.accountsToolButton, self.payeeComboBox)
        self.setTabOrder(self.payeeComboBox, self.dateEdit)
        self.setTabOrder(self.dateEdit, self.descriptionPlainTextEdit)
        self.setTabOrder(self.descriptionPlainTextEdit, self.amountDoubleSpinBox)

        if hasattr(self, "_category_rows"):
            self.setTabOrder(self.amountDoubleSpinBox, self._category_rows[0])

            if len(self._category_rows) > 1:
                if self.split_categories_vertical_layout is None:
                    raise ValueError("Vertical split Categories Layout is None.")

                index = 0

                while index + 1 < len(self._category_rows):
                    self.setTabOrder(
                        self._category_rows[index], self._category_rows[index + 1]
                    )
                    index += 1

                vertical_layout_count = self.split_categories_vertical_layout.count()
                last_widget = self.split_categories_vertical_layout.itemAt(
                    vertical_layout_count - 1
                ).widget()
                self.setTabOrder(self._category_rows[index], last_widget)
            else:
                last_widget = self._category_rows[0]
        else:
            last_widget = self.amountDoubleSpinBox

        if hasattr(self, "_tag_rows"):
            self.setTabOrder(last_widget, self._tag_rows[0])

            if self.split_tags_vertical_layout is not None:
                index = 0

                while index + 1 < len(self._tag_rows):
                    self.setTabOrder(self._tag_rows[index], self._tag_rows[index + 1])
                    index += 1

                vertical_layout_count = self.split_tags_vertical_layout.count()
                last_widget = self.split_tags_vertical_layout.itemAt(
                    vertical_layout_count - 1
                ).widget()
                self.setTabOrder(self._tag_rows[index], last_widget)

        # FIXME: tab order is stuck at the end in the dialog buttons

    def _account_changed(self) -> None:
        account_path = self.account_path
        if account_path is None:
            return

        for account in self._accounts:
            if account.path == account_path:
                _account = account
                break
        else:
            raise ValueError(f"Invalid Account path: {account_path}")
        self.currency_code = _account.currency.code
        self.amount_decimals = _account.currency.places

    def _handle_payee_text_changed(self) -> None:
        prefix = self.payeeComboBox.lineEdit().text()
        if len(prefix) > 0:
            self._completer.update(prefix)
            return
        self._completer.popup().hide()

    def _handle_payee_completion(self, text: str) -> None:
        with QSignalBlocker(self.payeeComboBox):
            self.payeeComboBox.setCurrentText(text)
