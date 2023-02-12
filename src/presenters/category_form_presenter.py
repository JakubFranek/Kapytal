import logging

from src.models.base_classes.account import Account
from src.models.model_objects.account_group import AccountGroup
from src.models.record_keeper import RecordKeeper
from src.presenters.utilities.event import Event
from src.presenters.view_models.category_tree_model import CategoryTreeModel
from src.views.forms.category_form import CategoryForm


class CategoryFormPresenter:
    event_data_changed = Event()

    def __init__(self, view: CategoryForm, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper
        self._model = CategoryTreeModel(
            view=view.treeView,
            root_items=record_keeper.root_categories,
            base_currency=record_keeper.base_currency,
        )
        self._view.treeView.setModel(self._model)

        self._setup_signals()
        self._view.finalize_setup()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._model.pre_reset_model()
        self._record_keeper = record_keeper
        self.update_model_data()
        self._model.post_reset_model()

    def update_model_data(self) -> None:
        self._model.root_items = self._record_keeper.root_categories
        self._model.base_currency = self._record_keeper.base_currency

    def show_form(self) -> None:
        self.update_model_data()
        self._view.show_form()

    def expand_all_below(self) -> None:
        indexes = self._view.treeView.selectedIndexes()
        item = self._model.get_selected_item()
        logging.debug(f"Expanding all nodes below {item}")
        if len(indexes) == 0:
            raise ValueError("No index to expand recursively selected.")
        self._view.treeView.expandRecursively(indexes[0])

    def _get_max_child_position(self, item: AccountGroup | None) -> int:
        if isinstance(item, AccountGroup):
            return len(item.children) + 1
        if item is None:
            return len(self._record_keeper.root_account_items) + 1
        raise ValueError("Invalid selection.")

    def _get_max_parent_position(self, item: AccountGroup | Account) -> int:
        parent = item.parent
        if parent is None:
            return len(self._record_keeper.root_account_items)
        return len(parent.children)

    def _get_current_index(self, item: AccountGroup | Account | None) -> int:
        if item is None:
            raise NotImplementedError
        parent = item.parent
        if parent is None:
            return self._record_keeper.root_account_items.index(item)
        return parent.children.index(item)

    def _setup_signals(self) -> None:
        # self._view.signal_selection_changed.connect(self._selection_changed)
        # self._view.signal_expand_below.connect(self.expand_all_below)
        # self._view.signal_delete_item.connect(self.remove_item)
        # self._view.signal_add_account_group.connect(
        #     lambda: self.run_add_dialog(
        #         setup_dialog=self.setup_account_group_dialog,
        #     )
        # )
        # self._view.signal_add_security_account.connect(
        #     lambda: self.run_add_dialog(
        #         setup_dialog=self.setup_security_account_dialog,
        #     )
        # )
        # self._view.signal_add_cash_account.connect(
        #     lambda: self.run_add_dialog(
        #         setup_dialog=self.setup_cash_account_dialog,
        #     )
        # )
        # self._view.signal_edit_item.connect(self.edit_item)

        self._selection_changed()  # called to ensure context menu is OK at start of run

    def _selection_changed(self) -> None:
        item = self._model.get_selected_item()

        enable_modify_object = item is not None
        enable_add_objects = item is None or isinstance(item, AccountGroup)
        enable_expand_below = isinstance(item, AccountGroup)

        # self._view.enable_accounts_tree_actions(
        #     enable_add_objects=enable_add_objects,
        #     enable_modify_object=enable_modify_object,
        #     enable_expand_below=enable_expand_below,
        # )
