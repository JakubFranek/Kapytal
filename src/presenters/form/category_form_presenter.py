import copy
import logging

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QApplication
from src.models.model_objects.attributes import Category, CategoryType
from src.models.record_keeper import RecordKeeper
from src.models.utilities.calculation import (
    calculate_category_stats,
)
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.category_tree_model import CategoryTreeModel
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.dialogs.category_dialog import CategoryDialog
from src.views.forms.category_form import CategoryForm


class CategoryFormPresenter:
    event_data_changed = Event()

    def __init__(self, view: CategoryForm, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        self._initialize_models()
        self._setup_signals()
        self._view.finalize_setup()
        self.update_model_data()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper

    def update_model_data(self) -> None:
        relevant_transactions = (
            self._record_keeper.cash_transactions
            + self._record_keeper.refund_transactions
        )
        category_stats = calculate_category_stats(
            relevant_transactions,
            self._record_keeper.base_currency,
            self._record_keeper.categories,
        )

        self._model_income.root_categories = self._record_keeper.root_income_categories
        self._model_income.category_stats_dict = category_stats
        self._model_expense.root_categories = (
            self._record_keeper.root_expense_categories
        )
        self._model_expense.category_stats_dict = category_stats
        self._model_income_and_expense.root_categories = (
            self._record_keeper.root_income_and_expense_categories
        )
        self._model_income_and_expense.category_stats_dict = category_stats

    def reset_model(self) -> None:
        self._model_income.pre_reset_model()
        self._model_expense.pre_reset_model()
        self._model_income_and_expense.pre_reset_model()
        self.update_model_data()
        self._model_income.post_reset_model()
        self._model_expense.post_reset_model()
        self._model_income_and_expense.post_reset_model()

    def show_form(self) -> None:
        self._busy_dialog = create_simple_busy_indicator(
            self._view, "Calculating Category stats, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()
        try:
            self.reset_model()
        except:  # noqa: TRY302
            raise
        finally:
            self._busy_dialog.close()

        self._view.incomeTreeView.expandAll()
        self._view.expenseTreeView.expandAll()
        self._view.incomeAndExpenseTreeView.expandAll()
        self._view.show_form()

    def expand_all_below(self) -> None:
        tree_view = self._view.get_current_tree_view()
        indexes = tree_view.selectedIndexes()
        if len(indexes) == 0:
            raise ValueError("No index to expand recursively selected.")
        tree_view.expandRecursively(indexes[0])

    def run_dialog(self, *, edit: bool) -> None:
        item = self._model_income.get_selected_item()
        type_ = self._view.category_type
        if type_ == CategoryType.INCOME:
            paths = [
                category.path + "/"
                for category in self._record_keeper.income_categories
            ]
        elif type_ == CategoryType.EXPENSE:
            paths = [
                category.path + "/"
                for category in self._record_keeper.expense_categories
            ]
        else:
            paths = [
                category.path + "/"
                for category in self._record_keeper.income_and_expense_categories
            ]
        max_position = (
            self._get_max_child_position(item)
            if edit is False
            else self._get_max_parent_position(item)
        )
        self._dialog = CategoryDialog(
            parent=self._view,
            type_=type_.value,
            paths=paths,
            max_position=max_position,
            edit=edit,
        )
        if edit:
            item = self._model_income.get_selected_item()
            if item is None:
                raise ValueError("Cannot edit an unselected item.")
            self._dialog.signal_ok.connect(self.edit_category)
            self._dialog.path = item.path
            self._dialog.current_path = item.path
            if item.parent is None:
                index = self._model_income.root_categories.index(item)
            else:
                index = item.parent.get_child_index(item)
            self._dialog.position = index + 1
        else:
            if item is not None:
                self._dialog.path = item.path + "/"
            self._dialog.position = self._dialog.positionSpinBox.maximum()
            self._dialog.signal_ok.connect(self.add_category)
        logging.debug(f"Running CategoryDialog ({edit=})")
        self._dialog.exec()

    def add_category(self) -> None:
        path = self._dialog.path
        type_ = CategoryType(self._dialog.type_)
        index = self._dialog.position - 1

        logging.info(f"Adding Category('{path}', {type_.name}, {index=})")
        # TODO: get rid of the deep copy due to performance
        record_keeper_copy = copy.deepcopy(self._record_keeper)
        try:
            logging.disable(logging.INFO)
            record_keeper_copy.add_category(path, type_, index)
            logging.disable(logging.NOTSET)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        item = self._model_income.get_selected_item()
        self._model_income.pre_add(item)
        logging.disable(logging.INFO)
        self._record_keeper.add_category(path, type_, index)
        logging.disable(logging.NOTSET)
        self.update_model_data()
        self._model_income.post_add()
        self._dialog.close()
        self.event_data_changed()

    def edit_category(self) -> None:
        item: Category = self._model_income.get_selected_item()
        previous_parent = item.parent
        previous_path = self._dialog.current_path
        previous_index = self._get_current_index(item)
        new_path = self._dialog.path
        if "/" in new_path:
            new_parent_path, _, _ = new_path.rpartition("/")
            new_parent = self._record_keeper.get_category(new_parent_path)
        else:
            new_parent = None
        new_index = self._dialog.position - 1

        logging.info(f"Editing Category at path='{item.path}'")
        record_keeper_copy = copy.deepcopy(self._record_keeper)
        try:
            logging.disable(logging.INFO)
            record_keeper_copy.edit_category(
                current_path=previous_path, new_path=new_path, index=new_index
            )
            logging.disable(logging.NOTSET)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        if new_parent == previous_parent and new_index == previous_index:
            move = False
        else:
            move = True

        if move:
            self._model_income.pre_move_item(
                previous_parent=previous_parent,
                previous_index=previous_index,
                new_parent=new_parent,
                new_index=new_index,
            )
        self._record_keeper.edit_category(
            current_path=previous_path, new_path=new_path, index=new_index
        )
        self.update_model_data()
        if move:
            self._model_income.post_move_item()
        self._dialog.close()
        self._tree_selection_changed()
        self.event_data_changed()

    def delete_category(self) -> None:
        item = self._model_income.get_selected_item()
        if item is None:
            raise ValueError("Cannot delete non-existent item.")
        logging.info(f"Removing {item.__class__.__name__} at path='{item.path}'")

        # Attempt deletion on a RecordKeeper copy
        record_keeper_copy = copy.deepcopy(self._record_keeper)
        try:
            record_keeper_copy.remove_category(item.path)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        # Perform the deletion on the "real" RecordKeeper if it went fine
        self._model_income.pre_remove_item(item)
        self._record_keeper.remove_category(item.path)
        self.update_model_data()
        self._model_income.post_remove_item()
        self.event_data_changed()

    def _get_max_child_position(self, item: Category | None) -> int:
        model = self._get_current_model()
        if isinstance(item, Category):
            return len(item.children) + 1
        if item is None:
            return len(model.root_categories) + 1
        raise ValueError("Invalid selection.")

    def _get_max_parent_position(self, item: Category) -> int:
        model = self._get_current_model()
        parent = item.parent
        if parent is None:
            return len(model.root_categories)
        return len(parent.children)

    def _get_current_index(self, item: Category | None) -> int:
        if item is None:
            raise NotImplementedError
        parent = item.parent
        if parent is None:
            return self._model_income.root_categories.index(item)
        return parent.children.index(item)

    def _setup_signals(self) -> None:
        self._view.signal_tree_selection_changed.connect(self._tree_selection_changed)
        self._view.signal_expand_all_below.connect(self.expand_all_below)
        self._view.signal_add.connect(lambda: self.run_dialog(edit=False))
        self._view.signal_edit.connect(lambda: self.run_dialog(edit=True))
        self._view.signal_delete.connect(self.delete_category)
        self._view.signal_income_search_text_changed.connect(
            self._filter_income_categories
        )
        self._view.signal_expense_search_text_changed.connect(
            self._filter_expense_categories
        )
        self._view.signal_income_and_expense_search_text_changed.connect(
            self._filter_income_and_expense_categories
        )

        self._tree_selection_changed()  # called to ensure context menu is OK at start

    def _tree_selection_changed(self) -> None:
        model = self._get_current_model()
        item = model.get_selected_item()

        enable_modify_object = item is not None
        enable_add_objects = True
        enable_expand_below = isinstance(item, Category) and len(item.children) > 0

        self._view.enable_actions(
            enable_add_objects=enable_add_objects,
            enable_modify_object=enable_modify_object,
            enable_expand_below=enable_expand_below,
        )

    def _filter_income_categories(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        logging.debug(f"Filtering Income Categories: {pattern=}")
        self._proxy_income.setFilterWildcard(pattern)
        self._view.incomeTreeView.expandAll()

    def _filter_expense_categories(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        logging.debug(f"Filtering Expense Categories: {pattern=}")
        self._proxy_expense.setFilterWildcard(pattern)
        self._view.expenseTreeView.expandAll()

    def _filter_income_and_expense_categories(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        logging.debug(f"Filtering Income and Expense Categories: {pattern=}")
        self._proxy_income_and_expense.setFilterWildcard(pattern)
        self._view.incomeAndExpenseTreeView.expandAll()

    def _initialize_models(self) -> None:
        self._proxy_income = QSortFilterProxyModel(self._view.incomeTreeView)
        self._model_income = CategoryTreeModel(
            tree_view=self._view.incomeTreeView,
            root_categories=(),
            category_stats={},
            proxy=self._proxy_income,
        )
        self._proxy_income.setSourceModel(self._model_income)
        self._proxy_income.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy_income.setRecursiveFilteringEnabled(True)  # noqa: FBT003
        self._proxy_income.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy_income.setFilterRole(Qt.ItemDataRole.UserRole + 1)
        self._view.incomeTreeView.setModel(self._proxy_income)

        self._proxy_expense = QSortFilterProxyModel(self._view.expenseTreeView)
        self._model_expense = CategoryTreeModel(
            tree_view=self._view.expenseTreeView,
            root_categories=(),
            category_stats={},
            proxy=self._proxy_expense,
        )
        self._proxy_expense.setSourceModel(self._model_expense)
        self._proxy_expense.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy_expense.setRecursiveFilteringEnabled(True)  # noqa: FBT003
        self._proxy_expense.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy_expense.setFilterRole(Qt.ItemDataRole.UserRole + 1)
        self._view.expenseTreeView.setModel(self._proxy_expense)

        self._proxy_income_and_expense = QSortFilterProxyModel(
            self._view.incomeAndExpenseTreeView
        )
        self._model_income_and_expense = CategoryTreeModel(
            tree_view=self._view.incomeAndExpenseTreeView,
            root_categories=(),
            category_stats={},
            proxy=self._proxy_income_and_expense,
        )
        self._proxy_income_and_expense.setSourceModel(self._model_income_and_expense)
        self._proxy_income_and_expense.setFilterCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )
        self._proxy_income_and_expense.setRecursiveFilteringEnabled(
            True  # noqa: FBT003
        )
        self._proxy_income_and_expense.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy_income_and_expense.setFilterRole(Qt.ItemDataRole.UserRole + 1)
        self._view.incomeAndExpenseTreeView.setModel(self._proxy_income_and_expense)

    def _get_current_model(self) -> CategoryTreeModel:
        type_ = self._view.category_type
        if type_ == CategoryType.INCOME:
            return self._model_income
        if type_ == CategoryType.EXPENSE:
            return self._model_expense
        return self._model_income_and_expense
