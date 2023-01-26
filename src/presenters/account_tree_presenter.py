import logging

from src.models.model_objects.account_group import AccountGroup
from src.models.record_keeper import RecordKeeper
from src.presenters.view_models.account_tree_model import AccountTreeModel
from src.views.account_group_dialog import AccountGroupDialog
from src.views.main_view import MainView
from src.views.utilities.handle_exception import get_exception_info


class AccountTreePresenter:
    def __init__(self, view: MainView, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper
        self._model = AccountTreeModel(
            view=view.accountTree, data=record_keeper.root_account_objects
        )
        self._view.accountTree.setModel(self._model)

        self._setup_signals()
        self._view.finalize_setup()
        logging.info("Showing MainView")
        self._view.show()

    def _setup_signals(self) -> None:
        self._view.signal_tree_selection_changed.connect(self.selection_changed)
        self._view.signal_tree_expand_below.connect(self.expand_all_below)
        self._view.signal_tree_delete_item.connect(self.delete_item)
        self._view.signal_tree_add_account_group.connect(
            lambda: self.run_account_group_dialog(edit=False)
        )

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
        indexes = self._view.accountTree.selectedIndexes()
        if len(indexes) == 0:
            raise ValueError("No index to expand recursively selected.")
        self._view.accountTree.expandRecursively(indexes[0])

    def run_account_group_dialog(self, edit: bool) -> None:
        item = self._model.get_selected_item()
        if isinstance(item, AccountGroup):
            max_position = len(item.children) + 1
        elif item is None:
            if edit is True:
                raise ValueError("It is not allowed to edit an unselected object.")
            max_position = len(self._record_keeper.root_account_objects) + 1
        else:
            raise ValueError("Invalid selection.")
        self._dialog = AccountGroupDialog(max_position=max_position, edit=edit)
        self._dialog.signal_OK.connect(self.add_account_group)
        item = self._model.get_selected_item()
        self._dialog.path = "" if item is None else item.path + "/"
        logging.info(f"Running AccountGroupDialog ({edit=})")
        self._dialog.exec()

    def add_account_group(self) -> None:
        path = self._dialog.path
        index = self._dialog.position - 1
        if "/" in path:
            parent_path, _, name = path.rpartition("/")
        else:
            name = path
            parent_path = None

        logging.info(f"Adding AccountGroup at path='{path}'")
        try:
            item = self._model.get_selected_item()
            self._model.pre_add(item)
            self._record_keeper.add_account_group(name, parent_path, index)
            self._model._data = self._record_keeper.root_account_objects
            self._model.post_add()
        except Exception:
            self._model.post_add()
            self._handle_exception()

    def delete_item(self) -> None:
        item = self._model.get_selected_item()
        if item is None:
            raise ValueError("Cannot delete non-existent item.")
        path = item.path
        logging.info(f"Removing {item.__class__.__name__} at path='{path}'")

        index = self._model.get_index_from_item(item)
        try:
            self._model.pre_delete_item(index)
            if isinstance(item, AccountGroup):
                self._record_keeper.remove_account_group(path)
            else:
                self._record_keeper.remove_account(path)
            # REFACTOR: is the line below ok?
            self._model._data = self._record_keeper.root_account_objects
            self._model.post_delete_item()
        except Exception:
            self._model.post_delete_item()
            self._handle_exception()

    def _handle_exception(self) -> None:
        display_text, display_details = get_exception_info()  # type: ignore
        self._view.display_error(display_text, display_details)
