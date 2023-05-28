import logging

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QApplication
from src.models.custom_exceptions import NotFoundError
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

BUSY_DIALOG_TRANSACTION_LIMIT = 20_000


class CategoryFormPresenter:
    event_data_changed = Event()

    def __init__(self, view: CategoryForm, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        self._initialize_models()
        self._setup_signals()
        self._view.finalize_setup()
        self._update_model_data()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._recalculate_data = True

    def data_changed(self) -> None:
        self._recalculate_data = True

    def show_form(self) -> None:
        if self._recalculate_data:
            self._reset_model()

        self._view.incomeTreeView.expandAll()
        self._view.expenseTreeView.expandAll()
        self._view.incomeAndExpenseTreeView.expandAll()
        self._view.show_form()

    def _reset_model(self) -> None:
        self._model_income.pre_reset_model()
        self._model_expense.pre_reset_model()
        self._model_income_and_expense.pre_reset_model()
        self._update_model_data_with_busy_dialog()
        self._model_income.post_reset_model()
        self._model_expense.post_reset_model()
        self._model_income_and_expense.post_reset_model()

    def _update_model_data_with_busy_dialog(self) -> None:
        no_of_transactions = len(self._record_keeper.transactions)
        if no_of_transactions >= BUSY_DIALOG_TRANSACTION_LIMIT:
            self._busy_dialog = create_simple_busy_indicator(
                self._view, "Calculating Category stats, please wait..."
            )
            self._busy_dialog.open()
            QApplication.processEvents()
        try:
            self._update_model_data()
        except:  # noqa: TRY302
            raise
        finally:
            if no_of_transactions >= BUSY_DIALOG_TRANSACTION_LIMIT:
                self._busy_dialog.close()

    def _update_model_data(self) -> None:
        relevant_transactions = (
            self._record_keeper.cash_transactions
            + self._record_keeper.refund_transactions
        )
        category_stats = calculate_category_stats(
            relevant_transactions,
            self._record_keeper.base_currency,
            self._record_keeper.categories,
        )

        self._model_income.load_data(
            self._record_keeper.income_categories, category_stats
        )
        self._model_expense.load_data(
            self._record_keeper.expense_categories, category_stats
        )
        self._model_income_and_expense.load_data(
            self._record_keeper.income_and_expense_categories, category_stats
        )

        self._recalculate_data = False

    def _expand_all_below(self) -> None:
        tree_view = self._view.get_current_tree_view()
        indexes = tree_view.selectedIndexes()
        if len(indexes) == 0:
            raise ValueError("No index to expand recursively selected.")
        tree_view.expandRecursively(indexes[0])

    def _run_dialog(self, *, edit: bool) -> None:
        model = self._get_current_model()
        selected_item = model.get_selected_item()
        type_ = self._view.category_type
        flat_categories = self._get_flat_categories_for_type(type_)
        paths = [category.path + "/" for category in flat_categories]

        self._dialog = CategoryDialog(
            parent=self._view,
            type_=type_.value,
            paths=paths,
            edit=edit,
        )
        self._dialog.signal_path_changed.connect(self._update_dialog_position_limits)

        if edit:
            if selected_item is None:
                raise ValueError("Cannot edit an unselected item.")
            self._dialog.signal_ok.connect(self._edit_category)
            self._dialog.current_path = selected_item.path
            self._dialog.path = selected_item.path
            self._dialog.position = self._get_category_index(selected_item) + 1
        else:
            if selected_item is not None:
                self._dialog.path = selected_item.path + "/"
            self._dialog.position = self._dialog.maximum_position
            self._dialog.signal_ok.connect(self._add_category)

        self._update_dialog_position_limits(self._dialog.path)
        logging.debug(f"Running CategoryDialog ({edit=})")
        self._dialog.exec()

    def _add_category(self) -> None:
        path = self._dialog.path
        type_ = CategoryType(self._dialog.type_)
        index = self._dialog.position - 1

        logging.info(f"Adding Category: {path=}, type={type_.name}, {index=}")
        try:
            self._record_keeper.add_category(path, type_, index)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        parent_category = self._get_parent_category_from_path(path)
        new_category = self._record_keeper.get_category(path)
        index_actual = self._get_category_index(new_category)

        model = self._get_current_model()
        model.pre_add(parent_category, index_actual)
        self._update_model_data_with_busy_dialog()
        model.post_add()
        self._dialog.close()
        self.event_data_changed()
        self._recalculate_data = False

    def _edit_category(self) -> None:
        model = self._get_current_model()
        item: Category = model.get_selected_item()
        previous_parent = item.parent
        previous_path = self._dialog.current_path
        previous_index = self._get_category_index(item)
        new_path = self._dialog.path
        new_parent = self._get_parent_category_from_path(new_path)
        new_index = self._dialog.position - 1

        logging.info(
            f"Editing Category at path='{item.path}', index={previous_index}: "
            f"new path='{new_path}', new index={new_index}"
        )
        try:
            self._record_keeper.edit_category(
                current_path=previous_path, new_path=new_path, index=new_index
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        move = new_parent != previous_parent or new_index != previous_index

        edited_category = self._record_keeper.get_category(new_path)
        new_index_actual = self._get_category_index(edited_category)

        if move:
            model.pre_move_item(
                previous_parent=previous_parent,
                previous_index=previous_index,
                new_parent=new_parent,
                new_index=new_index_actual,
            )
        self._update_model_data_with_busy_dialog()
        if move:
            model.post_move_item()
        self._dialog.close()
        self._tree_selection_changed()
        self.event_data_changed()
        self._recalculate_data = False

    def _delete_category(self) -> None:
        model = self._get_current_model()
        item = model.get_selected_item()
        if item is None:
            raise ValueError("Cannot delete non-existent item.")

        logging.info(f"Removing Category at path='{item.path}'")
        try:
            self._record_keeper.remove_category(item.path)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        model.pre_remove_item(item)
        self._update_model_data_with_busy_dialog()
        model.post_remove_item()
        self.event_data_changed()
        self._recalculate_data = False

    def _setup_signals(self) -> None:
        self._view.signal_tree_selection_changed.connect(self._tree_selection_changed)
        self._view.signal_tab_changed.connect(self._tree_selection_changed)
        self._view.signal_expand_all_below.connect(self._expand_all_below)
        self._view.signal_add.connect(lambda: self._run_dialog(edit=False))
        self._view.signal_edit.connect(lambda: self._run_dialog(edit=True))
        self._view.signal_delete.connect(self._delete_category)
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
        self._proxy_income.setFilterWildcard(pattern)
        self._view.incomeTreeView.expandAll()

    def _filter_expense_categories(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        self._proxy_expense.setFilterWildcard(pattern)
        self._view.expenseTreeView.expandAll()

    def _filter_income_and_expense_categories(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        self._proxy_income_and_expense.setFilterWildcard(pattern)
        self._view.incomeAndExpenseTreeView.expandAll()

    def _initialize_models(self) -> None:
        self._proxy_income = QSortFilterProxyModel(self._view.incomeTreeView)
        self._model_income = CategoryTreeModel(
            tree_view=self._view.incomeTreeView,
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

    def _update_dialog_position_limits(self, path: str) -> None:
        if self._dialog.edit:
            self._update_edit_dialog_position_limits(path)
        else:
            self._update_add_dialog_position_limits(path)

    def _update_add_dialog_position_limits(self, path: str) -> None:
        parent_path, _, _ = path.rpartition("/")

        if not parent_path:
            type_ = self._view.category_type
            root_categories = self._get_root_categories_for_type(type_)
            maximum_position = len(root_categories) + 1
        else:
            try:
                parent = self._record_keeper.get_category(parent_path)
                maximum_position = len(parent.children) + 1
            except NotFoundError:
                maximum_position = 1

        self._dialog.maximum_position = maximum_position

    def _update_edit_dialog_position_limits(self, path: str) -> None:
        current_path = self._dialog.current_path
        try:
            current_category = self._record_keeper.get_category(current_path)
        except NotFoundError:
            return
        parent_path, _, _ = path.rpartition("/")

        if not parent_path:
            type_ = self._view.category_type
            root_categories = self._get_root_categories_for_type(type_)
            maximum_position = len(root_categories)
            if current_category not in root_categories:
                maximum_position += 1
        else:
            try:
                parent = self._record_keeper.get_category(parent_path)
                maximum_position = len(parent.children)
                if current_category not in parent.children:
                    maximum_position += 1
            except NotFoundError:
                maximum_position = 1

        self._dialog.maximum_position = maximum_position

    def _get_flat_categories_for_type(
        self, type_: CategoryType
    ) -> tuple[Category, ...]:
        if type_ == CategoryType.INCOME:
            return self._record_keeper.income_categories
        if type_ == CategoryType.EXPENSE:
            return self._record_keeper.expense_categories
        return self._record_keeper.income_and_expense_categories

    def _get_root_categories_for_type(self, type_: CategoryType) -> list[Category]:
        if type_ == CategoryType.INCOME:
            return self._record_keeper.root_income_categories
        if type_ == CategoryType.EXPENSE:
            return self._record_keeper.root_expense_categories
        return self._record_keeper.root_income_and_expense_categories

    def _get_category_index(self, category: Category) -> int:
        if category.parent is not None:
            return category.parent.children.index(category)
        root_categories = self._get_root_categories_for_type(category.type_)
        return root_categories.index(category)

    def _get_parent_category_from_path(self, path: str) -> Category | None:
        if "/" not in path:
            return None
        parent_path, _, _ = path.rpartition("/")
        try:
            return self._record_keeper.get_category(parent_path)
        except NotFoundError:
            return None
