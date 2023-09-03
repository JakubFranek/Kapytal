from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QContextMenuEvent, QCursor
from PyQt6.QtWidgets import QHeaderView, QLineEdit, QMenu, QTreeView, QWidget
from src.models.model_objects.attributes import CategoryType
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.constants import CategoryTreeColumn
from src.views.ui_files.forms.Ui_category_form import Ui_CategoryForm


class CategoryForm(CustomWidget, Ui_CategoryForm):
    signal_add = pyqtSignal()
    signal_edit = pyqtSignal()
    signal_delete = pyqtSignal()

    signal_tree_selection_changed = pyqtSignal()
    signal_expand_all_below = pyqtSignal()
    signal_show_transactions = pyqtSignal()

    signal_income_search_text_changed = pyqtSignal(str)
    signal_expense_search_text_changed = pyqtSignal(str)
    signal_income_and_expense_search_text_changed = pyqtSignal(str)

    signal_tab_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)

        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.category)

        self._initialize_search_bars()
        self._initialize_actions()
        self.incomeTreeView.contextMenuEvent = self._create_context_menu
        self.expenseTreeView.contextMenuEvent = self._create_context_menu
        self.incomeAndExpenseTreeView.contextMenuEvent = self._create_context_menu

        self.incomeTreeView.header().setSortIndicatorClearable(True)
        self.expenseTreeView.header().setSortIndicatorClearable(True)
        self.incomeAndExpenseTreeView.header().setSortIndicatorClearable(True)

        self.tabWidget.currentChanged.connect(self.signal_tab_changed.emit)

    @property
    def category_type(self) -> CategoryType:
        current_index = self.tabWidget.currentIndex()
        if current_index == 0:
            return CategoryType.INCOME
        if current_index == 1:
            return CategoryType.EXPENSE
        return CategoryType.INCOME_AND_EXPENSE

    def enable_actions(
        self,
        *,
        enable_add_objects: bool,
        enable_modify_object: bool,
        enable_show_transactions: bool,
        enable_expand_below: bool,
    ) -> None:
        self.actionAdd.setEnabled(enable_add_objects)
        self.actionEdit.setEnabled(enable_modify_object)
        self.actionRemove.setEnabled(enable_modify_object)
        self.actionShow_Transactions.setEnabled(enable_show_transactions)
        self.actionExpand_All_Below.setEnabled(enable_expand_below)

    def get_current_tree_view(self) -> QTreeView:
        type_ = self.category_type
        if type_ == CategoryType.INCOME:
            return self.incomeTreeView
        if type_ == CategoryType.EXPENSE:
            return self.expenseTreeView
        return self.incomeAndExpenseTreeView

    def finalize_setup(self) -> None:
        self.incomeTreeView.selectionModel().selectionChanged.connect(
            self.signal_tree_selection_changed.emit
        )
        self.expenseTreeView.selectionModel().selectionChanged.connect(
            self.signal_tree_selection_changed.emit
        )
        self.incomeAndExpenseTreeView.selectionModel().selectionChanged.connect(
            self.signal_tree_selection_changed.emit
        )

        self.incomeTreeView.header().setSectionResizeMode(
            CategoryTreeColumn.NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.incomeTreeView.header().setSectionResizeMode(
            CategoryTreeColumn.TRANSACTIONS,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.incomeTreeView.header().setSectionResizeMode(
            CategoryTreeColumn.BALANCE,
            QHeaderView.ResizeMode.Stretch,
        )
        self.expenseTreeView.header().setSectionResizeMode(
            CategoryTreeColumn.NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.expenseTreeView.header().setSectionResizeMode(
            CategoryTreeColumn.TRANSACTIONS,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.expenseTreeView.header().setSectionResizeMode(
            CategoryTreeColumn.BALANCE,
            QHeaderView.ResizeMode.Stretch,
        )
        self.incomeAndExpenseTreeView.header().setSectionResizeMode(
            CategoryTreeColumn.NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.incomeAndExpenseTreeView.header().setSectionResizeMode(
            CategoryTreeColumn.TRANSACTIONS,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.incomeAndExpenseTreeView.header().setSectionResizeMode(
            CategoryTreeColumn.BALANCE,
            QHeaderView.ResizeMode.Stretch,
        )

        self.incomeTreeView.sortByColumn(-1, Qt.SortOrder.AscendingOrder)
        self.expenseTreeView.sortByColumn(-1, Qt.SortOrder.AscendingOrder)
        self.incomeAndExpenseTreeView.sortByColumn(-1, Qt.SortOrder.AscendingOrder)

    def _initialize_search_bars(self) -> None:
        self.incomeSearchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )
        self.expenseSearchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )
        self.incomeAndExpenseSearchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )
        self.incomeSearchLineEdit.textChanged.connect(
            self.signal_income_search_text_changed.emit
        )
        self.expenseSearchLineEdit.textChanged.connect(
            self.signal_expense_search_text_changed.emit
        )
        self.incomeAndExpenseSearchLineEdit.textChanged.connect(
            self.signal_income_and_expense_search_text_changed.emit
        )

    def _initialize_actions(self) -> None:
        self.actionExpand_All.setIcon(icons.expand)
        self.actionExpand_All_Below.setIcon(icons.expand_below)
        self.actionCollapse_All.setIcon(icons.collapse)

        self.actionAdd.setIcon(icons.add)
        self.actionEdit.setIcon(icons.edit)
        self.actionRemove.setIcon(icons.remove)
        self.actionShow_Transactions.setIcon(icons.table)

        self.actionExpand_All.triggered.connect(self._expand_all)
        self.actionCollapse_All.triggered.connect(self._collapse_all)
        self.actionExpand_All_Below.triggered.connect(self.signal_expand_all_below.emit)

        self.actionAdd.triggered.connect(self.signal_add.emit)
        self.actionEdit.triggered.connect(self.signal_edit.emit)
        self.actionRemove.triggered.connect(self.signal_delete.emit)
        self.actionShow_Transactions.triggered.connect(
            self.signal_show_transactions.emit
        )

        self.incomeExpandAllToolButton.setDefaultAction(self.actionExpand_All)
        self.incomeCollapseAllToolButton.setDefaultAction(self.actionCollapse_All)
        self.incomeAddToolButton.setDefaultAction(self.actionAdd)
        self.incomeEditToolButton.setDefaultAction(self.actionEdit)
        self.incomeRemoveToolButton.setDefaultAction(self.actionRemove)
        self.incomeShowTransactionsToolButton.setDefaultAction(
            self.actionShow_Transactions
        )

        self.expenseExpandAllToolButton.setDefaultAction(self.actionExpand_All)
        self.expenseCollapseAllToolButton.setDefaultAction(self.actionCollapse_All)
        self.expenseAddToolButton.setDefaultAction(self.actionAdd)
        self.expenseEditToolButton.setDefaultAction(self.actionEdit)
        self.expenseRemoveToolButton.setDefaultAction(self.actionRemove)
        self.expenseShowTransactionsToolButton.setDefaultAction(
            self.actionShow_Transactions
        )

        self.incomeAndExpenseExpandAllToolButton.setDefaultAction(self.actionExpand_All)
        self.incomeAndExpenseCollapseAllToolButton.setDefaultAction(
            self.actionCollapse_All
        )
        self.incomeAndExpenseAddToolButton.setDefaultAction(self.actionAdd)
        self.incomeAndExpenseEditToolButton.setDefaultAction(self.actionEdit)
        self.incomeAndExpenseRemoveToolButton.setDefaultAction(self.actionRemove)
        self.incomeAndExpenseShowTransactionsToolButton.setDefaultAction(
            self.actionShow_Transactions
        )

    def _expand_all(self) -> None:
        category_type = self.category_type
        if category_type == CategoryType.INCOME:
            self.incomeTreeView.expandAll()
        elif category_type == CategoryType.EXPENSE:
            self.expenseTreeView.expandAll()
        else:
            self.incomeAndExpenseTreeView.expandAll()

    def _collapse_all(self) -> None:
        category_type = self.category_type
        if category_type == CategoryType.INCOME:
            self.incomeTreeView.collapseAll()
        elif category_type == CategoryType.EXPENSE:
            self.expenseTreeView.collapseAll()
        else:
            self.incomeAndExpenseTreeView.collapseAll()

    def _create_context_menu(self, event: QContextMenuEvent) -> None:  # noqa: ARG002
        self.menu = QMenu(self)
        self.menu.addAction(self.actionAdd)
        self.menu.addAction(self.actionEdit)
        self.menu.addAction(self.actionRemove)
        self.menu.addSeparator()
        self.menu.addAction(self.actionExpand_All_Below)
        self.menu.addSeparator()
        self.menu.addAction(self.actionShow_Transactions)
        self.menu.popup(QCursor.pos())
