import logging

from src.models.base_classes.account import Account
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.security_objects import SecurityAccount
from src.models.record_keeper import RecordKeeper
from src.presenters.view_models.account_tree_model import AccountTreeModel
from src.views.account_group_dialog import AccountGroupDialog
from src.views.account_tree import AccountTree
from src.views.security_account_dialog import SecurityAccountDialog
from src.views.utilities.handle_exception import get_exception_info


# TODO: view should be QTreeView, not MainView
# TODO: create MainPresenter
class AccountTreePresenter:
    def __init__(self, view: AccountTree, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper
        self._model = AccountTreeModel(
            view=view, data=record_keeper.root_account_objects
        )
        self._view.setModel(self._model)

        self._setup_signals()
        self._view.finalize_setup()

    def _setup_signals(self) -> None:
        self._view.signal_selection_changed.connect(self.selection_changed)
        self._view.signal_expand_below.connect(self.expand_all_below)
        self._view.signal_delete_item.connect(self.delete_item)
        self._view.signal_add_account_group.connect(
            lambda: self.run_account_group_dialog(
                item=self._model.get_selected_item(), edit=False
            )
        )
        self._view.signal_add_security_account.connect(
            lambda: self.run_security_account_dialog(
                item=self._model.get_selected_item(), edit=False
            )
        )
        self._view.signal_edit_item.connect(self.edit_item)

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
        indexes = self._view.selectedIndexes()
        if len(indexes) == 0:
            raise ValueError("No index to expand recursively selected.")
        self._view.expandRecursively(indexes[0])

    def edit_item(self) -> None:
        item = self._model.get_selected_item()
        if isinstance(item, AccountGroup):
            self.run_account_group_dialog(item=item, edit=True)
        if isinstance(item, SecurityAccount):
            self.run_security_account_dialog(item=item, edit=True)

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

    def run_account_group_dialog(self, edit: bool, item: AccountGroup | None) -> None:
        if edit:
            if item is None:
                raise ValueError("Cannot edit an unselected item.")
            max_position = self._get_max_parent_position(item)
            self._dialog = AccountGroupDialog(max_position=max_position, edit=edit)
            self._dialog.signal_OK.connect(self.edit_account_group)
            self._dialog.current_path = item.path
            self._dialog.path = item.path
            if item.parent is None:
                position = self._record_keeper.root_account_objects.index(item) + 1
            else:
                position = item.parent.children.index(item) + 1
            self._dialog.position = position
        else:
            max_position = self._get_max_child_position(item)
            self._dialog = AccountGroupDialog(max_position=max_position, edit=edit)
            self._dialog.signal_OK.connect(self.add_account_group)
            self._dialog.path = "" if item is None else item.path + "/"
            self._dialog.position = max_position
        logging.info(f"Running AccountGroupDialog ({edit=})")
        self._dialog.exec()

    def add_account_group(self) -> None:
        path = self._dialog.path
        index = self._dialog.position - 1

        logging.info(f"Adding AccountGroup at path='{path}', index={index}")
        try:
            item = self._model.get_selected_item()
            self._model.pre_add(item)
            self._record_keeper.add_account_group(path, index)
            self._model._data = self._record_keeper.root_account_objects
            self._model.post_add()
            self._dialog.close()
        except Exception:
            self._handle_exception()

    def edit_account_group(self) -> None:
        item = self._model.get_selected_item()
        current_path = self._dialog.current_path
        new_path = self._dialog.path
        current_index = self._get_current_index(item)
        index = self._dialog.position - 1
        logging.info(
            f"Editing AccountGroup: old path='{current_path}', "
            f"old index={current_index}, new path='{new_path}', new index={index}"
        )
        try:
            self._model.pre_reset_model()
            self._record_keeper.edit_account_group(
                current_path=current_path, new_path=new_path, index=index
            )
            self._model._data = self._record_keeper.root_account_objects
            self._model.post_reset_model()
            self._dialog.close()
        except Exception:
            self._handle_exception()

    def run_security_account_dialog(
        self, edit: bool, item: SecurityAccount | None
    ) -> None:
        if edit:
            if item is None:
                raise ValueError("Cannot edit an unselected item.")
            max_position = self._get_max_parent_position(item)
            self._dialog = SecurityAccountDialog(max_position=max_position, edit=edit)
            self._dialog.signal_OK.connect(self.edit_security_account)
            self._dialog.current_path = item.path
            self._dialog.path = item.path
            if item.parent is None:
                position = self._record_keeper.root_account_objects.index(item) + 1
            else:
                position = item.parent.children.index(item) + 1
            self._dialog.position = position
        else:
            max_position = self._get_max_child_position(item)
            self._dialog = SecurityAccountDialog(max_position=max_position, edit=edit)
            self._dialog.signal_OK.connect(self.add_security_account)
            self._dialog.path = "" if item is None else item.path + "/"
            self._dialog.position = max_position
        logging.info(f"Running SecurityAccountDialog ({edit=})")
        self._dialog.exec()

    def add_security_account(self) -> None:
        path = self._dialog.path
        index = self._dialog.position - 1

        logging.info(f"Adding SecurityAccount at path='{path}', index={index}")
        try:
            item = self._model.get_selected_item()
            self._model.pre_add(item)
            self._record_keeper.add_security_account(path, index)
            self._model._data = self._record_keeper.root_account_objects
            self._model.post_add()
            self._dialog.close()
        except Exception:
            self._model.post_add()
            self._handle_exception()

    def edit_security_account(self) -> None:
        item = self._model.get_selected_item()
        current_path = self._dialog.current_path
        new_path = self._dialog.path
        current_index = self._get_current_index(item)
        index = self._dialog.position - 1
        logging.info(
            f"Editing SecurityAccount: old path='{current_path}', "
            f"old index={current_index}, new path='{new_path}', new index={index}"
        )
        try:
            self._model.pre_reset_model()
            self._record_keeper.edit_account(
                current_path=current_path, new_path=new_path, index=index
            )
            self._model._data = self._record_keeper.root_account_objects
            self._model.post_reset_model()
            self._dialog.close()
        except Exception:
            self._model.post_reset_model()
            self._handle_exception()

    def _handle_exception(self) -> None:
        display_text, display_details = get_exception_info()  # type: ignore
        self._view.display_error(display_text, display_details)

    def _get_max_child_position(self, item: AccountGroup | None) -> int:
        if isinstance(item, AccountGroup):
            return len(item.children) + 1
        if item is None:
            return len(self._record_keeper.root_account_objects) + 1
        raise ValueError("Invalid selection.")

    def _get_max_parent_position(self, item: AccountGroup | Account) -> int:
        parent = item.parent
        if parent is None:
            return len(self._record_keeper.root_account_objects)
        return len(parent.children)

    def _get_current_index(self, item: AccountGroup | Account | None) -> int:
        if item is None:
            raise NotImplementedError
        parent = item.parent
        if parent is None:
            return self._record_keeper.root_account_objects.index(item)
        return parent.children.index(item)
