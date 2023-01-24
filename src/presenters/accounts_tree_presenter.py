import logging

from src.models.model_objects.account_group import AccountGroup
from src.models.record_keeper import RecordKeeper
from src.presenters.view_models.accounts_tree_model import AccountsTreeModel
from src.views.main_view import MainView
from src.views.utilities.handle_exception import get_exception_info


class AccountsTreePresenter:
    def __init__(self, view: MainView, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper
        self._model = AccountsTreeModel(
            view=view.accountsTree, data=record_keeper.account_objects
        )
        self._view.accountsTree.setModel(self._model)

        self._setup_signals()
        self._view.finalize_setup()
        logging.info("Showing MainView")
        self._view.show()

    def _setup_signals(self) -> None:
        self._view.signal_tree_selection_changed.connect(self.selection_changed)
        self._view.signal_tree_expand_below.connect(self.expand_all_below)
        self._view.signal_tree_delete_item.connect(self.delete_item)

        self.selection_changed()  # called to ensure context menu is OK at start of run

    def selection_changed(self) -> None:
        item = self._model.get_selected_item()

        enable_modify_object = item is not None
        enable_add_objects = item is None or isinstance(item, AccountGroup)
        enable_expand_below = isinstance(item, AccountGroup)

        self._view.enable_accounts_tree_actions(
            enable_add_objects=enable_add_objects,
            enable_modify_object=enable_modify_object,
            enable_expand_below=enable_expand_below,
        )

    def expand_all_below(self) -> None:
        indexes = self._view.accountsTree.selectedIndexes()
        if len(indexes) == 0:
            raise ValueError("No index to expand recursively selected.")
        self._view.accountsTree.expandRecursively(indexes[0])

    def delete_item(self) -> None:
        item = self._model.get_selected_item()
        if item is None:
            raise ValueError("Cannot delete non-existent item.")
        path = item.path
        logging.info(f"Removing Account Tree item at path='{path}'")

        index = self._model.get_selected_item_index()
        try:
            self._model.pre_delete_item(index)
            if isinstance(item, AccountGroup):
                self._record_keeper.remove_account_group(path)
            else:
                self._record_keeper.remove_account(path)
            self._model._data = self._record_keeper.account_objects
            self._model.post_delete_item()
        except Exception:
            self._model.post_delete_item()
            self.handle_exception()

    def handle_exception(self) -> None:
        display_text, display_details = get_exception_info()  # type: ignore
        self._view.display_error(display_text, display_details)
