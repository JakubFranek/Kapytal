import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QLineEdit, QWidget
from src.models.model_objects.attributes import CategoryType
from src.views import icons
from src.views.ui_files.forms.Ui_category_form import Ui_CategoryForm
from src.views.widgets.category_tree import CategoryTree


class CategoryForm(QWidget, Ui_CategoryForm):
    signal_add_category = pyqtSignal()
    signal_edit_category = pyqtSignal()
    signal_delete_category = pyqtSignal()
    signal_select_category = pyqtSignal()
    signal_search_text_changed = pyqtSignal(str)
    signal_tree_selection_changed = pyqtSignal()
    signal_type_selection_changed = pyqtSignal()
    signal_expand_all_below = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.category_tree = CategoryTree(self)
        self.verticalLayout.addWidget(self.category_tree)

        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.category)

        self.searchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )
        self.searchLineEdit.textChanged.connect(self.signal_search_text_changed.emit)
        self.category_tree.signal_add_category.connect(self.signal_add_category.emit)
        self.category_tree.signal_edit_category.connect(self.signal_edit_category.emit)
        self.category_tree.signal_delete_category.connect(
            self.signal_delete_category.emit
        )
        self.category_tree.signal_expand_below.connect(
            self.signal_expand_all_below.emit
        )
        self.category_tree.signal_selection_changed.connect(
            self.signal_tree_selection_changed.emit
        )

        self.incomeRadioButton.toggled.connect(
            lambda checked: self._radio_button_toggled(checked=checked)
        )
        self.expenseRadioButton.toggled.connect(
            lambda checked: self._radio_button_toggled(checked=checked)
        )
        self.incomeAndExpenseRadioButton.toggled.connect(
            lambda checked: self._radio_button_toggled(checked=checked)
        )

        self.expandAllToolButton.setDefaultAction(self.category_tree.actionExpand_All)
        self.collapseAllToolButton.setDefaultAction(
            self.category_tree.actionCollapse_All
        )
        self.addToolButton.setDefaultAction(self.category_tree.actionAdd_Category)

    @property
    def search_bar_text(self) -> str:
        return self.searchLineEdit.text()

    @property
    def checked_type(self) -> CategoryType:
        if self.incomeRadioButton.isChecked():
            return CategoryType.INCOME
        if self.expenseRadioButton.isChecked():
            return CategoryType.EXPENSE
        if self.incomeAndExpenseRadioButton.isChecked():
            return CategoryType.INCOME_AND_EXPENSE
        raise ValueError("No radio button checked.")

    def show_form(self) -> None:
        logging.debug(f"Showing {self.__class__.__name__}")
        self.show()

    def closeEvent(self, a0: QCloseEvent) -> None:  # noqa: N802
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().closeEvent(a0)

    def finalize_setup(self) -> None:
        self.category_tree.finalize_setup()

    def _radio_button_toggled(self, *, checked: bool) -> None:
        if not checked:
            return  # don't care about un-checking of radio button
        self.signal_type_selection_changed.emit()
