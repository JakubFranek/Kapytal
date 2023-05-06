import copy
import logging

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.model_objects.attributes import Category, CategoryType
from src.models.record_keeper import RecordKeeper
from src.models.utilities.calculation import CategoryStats, get_category_stats
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.category_tree_model import CategoryTreeModel
from src.views.dialogs.category_dialog import CategoryDialog
from src.views.forms.category_form import CategoryForm

# TODO: Have 3 separate treeviews and models?


class CategoryFormPresenter:
    event_data_changed = Event()

    def __init__(self, view: CategoryForm, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper
        self._proxy_model = QSortFilterProxyModel(self._view.category_tree)
        self._model = CategoryTreeModel(
            tree_view=view.category_tree,
            root_categories=record_keeper.root_income_categories,
            category_stats=[],
            base_currency=record_keeper.base_currency,
            proxy=self._proxy_model,
        )

        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy_model.setRecursiveFilteringEnabled(True)  # noqa: FBT003
        self._view.category_tree.setModel(self._proxy_model)

        self._view.incomeRadioButton.setChecked(True)  # noqa: FBT003

        self._setup_signals()
        self._view.finalize_setup()
        self.update_model_data()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self.reset_model()

    def update_model_data(self) -> None:
        type_ = self._view.checked_type
        if type_ == CategoryType.INCOME:
            self._model.root_categories = self._record_keeper.root_income_categories
        elif type_ == CategoryType.EXPENSE:
            self._model.root_categories = self._record_keeper.root_expense_categories
        else:
            self._model.root_categories = (
                self._record_keeper.root_income_and_expense_categories
            )
        self._model.base_currency = self._record_keeper.base_currency

        category_stats: list[CategoryStats] = []
        for category in self._record_keeper.categories:
            category_stats.append(
                get_category_stats(
                    category,
                    self._record_keeper.transactions,
                    self._record_keeper.base_currency,
                )
            )
        self._model.category_stats = tuple(category_stats)

    def reset_model(self) -> None:
        self._model.pre_reset_model()
        self.update_model_data()
        self._model.post_reset_model()
        if self._view.isVisible():
            self._view.category_tree.expand_all()

    def show_form(self) -> None:
        self._model.pre_reset_model()
        self.update_model_data()
        self._model.post_reset_model()
        self._view.category_tree.expand_all()
        self._view.show_form()

    def expand_all_below(self) -> None:
        indexes = self._view.category_tree.selectedIndexes()
        if len(indexes) == 0:
            raise ValueError("No index to expand recursively selected.")
        item = self._model.get_selected_item()
        logging.debug(f"Expanding all nodes below {item}")
        self._view.category_tree.expandRecursively(indexes[0])

    def run_dialog(self, *, edit: bool) -> None:
        item = self._model.get_selected_item()
        type_ = self._view.checked_type
        paths = [category.path + "/" for category in self._record_keeper.categories]
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
            item = self._model.get_selected_item()
            if item is None:
                raise ValueError("Cannot edit an unselected item.")
            self._dialog.signal_ok.connect(self.edit_category)
            self._dialog.path = item.path
            self._dialog.current_path = item.path
            if item.parent is None:
                index = self._model.root_categories.index(item)
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
        record_keeper_copy = copy.deepcopy(self._record_keeper)
        try:
            logging.disable(logging.INFO)
            record_keeper_copy.add_category(path, type_, index)
            logging.disable(logging.NOTSET)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        item = self._model.get_selected_item()
        self._model.pre_add(item)
        logging.disable(logging.INFO)
        self._record_keeper.add_category(path, type_, index)
        logging.disable(logging.NOTSET)
        self.update_model_data()
        self._model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def edit_category(self) -> None:
        item: Category = self._model.get_selected_item()
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
            self._model.pre_move_item(
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
            self._model.post_move_item()
        self._dialog.close()
        self._tree_selection_changed()
        self.event_data_changed()

    def delete_category(self) -> None:
        item = self._model.get_selected_item()
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
        self._model.pre_remove_item(item)
        self._record_keeper.remove_category(item.path)
        self.update_model_data()
        self._model.post_remove_item()
        self.event_data_changed()

    def _get_max_child_position(self, item: Category | None) -> int:
        if isinstance(item, Category):
            return len(item.children) + 1
        if item is None:
            return len(self._model.root_categories) + 1
        raise ValueError("Invalid selection.")

    def _get_max_parent_position(self, item: Category) -> int:
        parent = item.parent
        if parent is None:
            return len(self._model.category_stats)
        return len(parent.children)

    def _get_current_index(self, item: Category | None) -> int:
        if item is None:
            raise NotImplementedError
        parent = item.parent
        if parent is None:
            return self._model.root_categories.index(item)
        return parent.children.index(item)

    def _setup_signals(self) -> None:
        self._view.signal_tree_selection_changed.connect(self._tree_selection_changed)
        self._view.signal_expand_all_below.connect(self.expand_all_below)
        self._view.signal_add_category.connect(lambda: self.run_dialog(edit=False))
        self._view.signal_edit_category.connect(lambda: self.run_dialog(edit=True))
        self._view.signal_delete_category.connect(self.delete_category)
        self._view.signal_type_selection_changed.connect(self._type_changed)
        self._view.signal_search_text_changed.connect(self._filter)

        self._tree_selection_changed()  # called to ensure context menu is OK at start

    def _tree_selection_changed(self) -> None:
        item = self._model.get_selected_item()

        enable_modify_object = item is not None
        enable_add_objects = True
        enable_expand_below = isinstance(item, Category) and len(item.children) > 0

        self._view.category_tree.enable_actions(
            enable_add_objects=enable_add_objects,
            enable_modify_object=enable_modify_object,
            enable_expand_below=enable_expand_below,
        )

    # TODO: refactor methods like this to get pattern from the signal
    def _filter(self) -> None:
        pattern = self._view.search_bar_text
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        logging.debug(f"Filtering Categories: {pattern=}")
        self._proxy_model.setFilterWildcard(pattern)
        self._view.category_tree.expand_all()

    def _type_changed(self) -> None:
        type_ = self._view.checked_type.name
        logging.debug(f"CategoryType selection changed: {type_}")
        self.reset_model()
