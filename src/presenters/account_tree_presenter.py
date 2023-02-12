import copy
import logging
from collections.abc import Callable

from src.models.base_classes.account import Account
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.security_objects import SecurityAccount
from src.models.record_keeper import RecordKeeper
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.presenters.view_models.account_tree_model import AccountTreeModel
from src.views.account_tree import AccountTree
from src.views.dialogs.account_group_dialog import AccountGroupDialog
from src.views.dialogs.cash_account_dialog import CashAccountDialog
from src.views.dialogs.security_account_dialog import SecurityAccountDialog


class AccountTreePresenter:
    # Definition of custom Callable type for setting up dialogs
    SetupDialogCallable = Callable[[bool, AccountGroup | Account | None, int], None]

    event_data_changed = Event()

    def __init__(self, view: AccountTree, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper
        self._model = AccountTreeModel(
            view=view,
            root_items=record_keeper.root_account_items,
            base_currency=record_keeper.base_currency,
        )
        self._view.setModel(self._model)

        self._setup_signals()
        self._view.finalize_setup()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._model.pre_reset_model()
        self._record_keeper = record_keeper
        self.update_model_data()
        self._model.post_reset_model()

    def update_model_data(self) -> None:
        self._model.root_items = self._record_keeper.root_account_items
        self._model.base_currency = self._record_keeper.base_currency

    def expand_all_below(self) -> None:
        indexes = self._view.selectedIndexes()
        item = self._model.get_selected_item()
        logging.debug(f"Expanding all nodes below {item}")
        if len(indexes) == 0:
            raise ValueError("No index to expand recursively selected.")
        self._view.expandRecursively(indexes[0])

    def edit_item(self) -> None:
        item = self._model.get_selected_item()
        setup_dialog: AccountTreePresenter.SetupDialogCallable
        if isinstance(item, AccountGroup):
            setup_dialog = self.setup_account_group_dialog
        elif isinstance(item, SecurityAccount):
            setup_dialog = self.setup_security_account_dialog
        elif isinstance(item, CashAccount):
            setup_dialog = self.setup_cash_account_dialog
        else:
            raise TypeError("Unexpected selected item type.")
        self.run_edit_dialog(item=item, setup_dialog=setup_dialog)

    def remove_item(self) -> None:
        item = self._model.get_selected_item()
        if item is None:
            raise ValueError("Cannot delete non-existent item.")
        logging.info(f"Removing {item.__class__.__name__} at path='{item.path}'")

        # Attempt deletion on a RecordKeeper copy
        record_keeper_copy = copy.deepcopy(self._record_keeper)
        try:
            if isinstance(item, AccountGroup):
                record_keeper_copy.remove_account_group(item.path)
            else:
                record_keeper_copy.remove_account(item.path)
        except Exception:
            handle_exception()
            return

        # Perform the deletion on the "real" RecordKeeper if it went fine
        self._model.pre_remove_item(item)
        if isinstance(item, AccountGroup):
            self._record_keeper.remove_account_group(item.path)
        else:
            self._record_keeper.remove_account(item.path)
        self.update_model_data()
        self._model.post_remove_item()
        self.event_data_changed()

    def run_add_dialog(self, setup_dialog: SetupDialogCallable) -> None:
        item = self._model.get_selected_item()
        max_position = self._get_max_child_position(item)
        setup_dialog(False, item, max_position)
        self._dialog.path = "" if item is None else item.path + "/"
        self._dialog.position = self._dialog.positionSpinBox.maximum()
        logging.debug(f"Running {self._dialog.__class__.__name__} (edit=False)")
        self._dialog.exec()

    def run_edit_dialog(
        self,
        item: AccountGroup | Account | None,
        setup_dialog: SetupDialogCallable,
    ) -> None:
        if item is None:
            raise ValueError("Cannot edit an unselected item.")
        max_position = self._get_max_parent_position(item)
        setup_dialog(True, item, max_position)
        self._dialog.current_path = item.path
        self._dialog.path = item.path
        if item.parent is None:
            index = self._record_keeper.root_account_items.index(item)
        else:
            index = item.parent.get_child_index(item)
        self._dialog.position = index + 1
        logging.debug(f"Running {self._dialog.__class__.__name__} (edit=True)")
        self._dialog.exec()

    def setup_account_group_dialog(
        self, edit: bool, item: AccountGroup, max_position: int  # noqa: U100
    ) -> None:
        account_group_paths = self._get_account_group_paths()
        if edit:
            self._dialog = AccountGroupDialog(
                parent=self._view,
                max_position=max_position,
                paths=account_group_paths,
                edit=edit,
            )
            self._dialog.signal_OK.connect(self.edit_account_group)
        else:
            self._dialog = AccountGroupDialog(
                parent=self._view,
                max_position=max_position,
                paths=account_group_paths,
                edit=edit,
            )
            self._dialog.signal_OK.connect(self.add_account_group)

    def add_account_group(self) -> None:
        path = self._dialog.path
        index = self._dialog.position - 1

        logging.info("Adding AccountGroup")
        try:
            self._record_keeper.add_account_group(path, index)
        except Exception:
            handle_exception()
            return

        item = self._model.get_selected_item()
        parent = item.parent if item is not None else None
        self._model.pre_add(parent)
        self.update_model_data()
        self._model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def edit_account_group(self) -> None:
        item: AccountGroup = self._model.get_selected_item()
        previous_parent = item.parent
        previous_path = self._dialog.current_path
        previous_index = self._get_current_index(item)
        new_path = self._dialog.path
        new_parent_path, _, _ = new_path.rpartition("/")
        new_parent = self._record_keeper.get_account_parent_or_none(new_parent_path)
        new_index = self._dialog.position - 1

        logging.info(f"Editing AccountGroup at path='{item.path}'")
        record_keeper_copy = copy.deepcopy(self._record_keeper)
        try:
            logging.disable(logging.INFO)
            record_keeper_copy.edit_account_group(
                current_path=previous_path, new_path=new_path, index=new_index
            )
            logging.disable(logging.NOTSET)
        except Exception:
            handle_exception()
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
        self._record_keeper.edit_account_group(
            current_path=previous_path, new_path=new_path, index=new_index
        )
        self.update_model_data()
        if move:
            self._model.post_move_item()
        self._dialog.close()
        self._selection_changed()
        self.event_data_changed()

    def setup_security_account_dialog(
        self, edit: bool, item: SecurityAccount, max_position: int  # noqa: U100
    ) -> None:
        account_group_paths = self._get_account_group_paths()
        if edit:
            self._dialog = SecurityAccountDialog(
                parent=self._view,
                max_position=max_position,
                paths=account_group_paths,
                edit=edit,
            )
            self._dialog.signal_OK.connect(self.edit_security_account)
        else:
            self._dialog = SecurityAccountDialog(
                parent=self._view,
                max_position=max_position,
                paths=account_group_paths,
                edit=edit,
            )
            self._dialog.signal_OK.connect(self.add_security_account)

    def add_security_account(self) -> None:
        path = self._dialog.path
        index = self._dialog.position - 1

        logging.info("Adding SecurityAccount")
        try:
            self._record_keeper.add_security_account(path, index)
        except Exception:
            handle_exception()
            return

        item = self._model.get_selected_item()
        parent = item.parent if item is not None else None
        self._model.pre_add(parent)
        self.update_model_data()
        self._model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def edit_security_account(self) -> None:
        item: SecurityAccount = self._model.get_selected_item()
        previous_parent = item.parent
        previous_path = self._dialog.current_path
        previous_index = self._get_current_index(item)
        new_path = self._dialog.path
        new_parent_path, _, _ = new_path.rpartition("/")
        new_parent = self._record_keeper.get_account_parent_or_none(new_parent_path)
        new_index = self._dialog.position - 1

        logging.info(f"Editing SecurityAccount at path='{item.path}'")
        record_keeper_deepcopy = copy.deepcopy(self._record_keeper)
        try:
            logging.disable(logging.INFO)
            record_keeper_deepcopy.edit_security_account(
                current_path=previous_path, new_path=new_path, index=previous_index
            )
            logging.disable(logging.NOTSET)
        except Exception:
            handle_exception()
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
        self._record_keeper.edit_security_account(
            current_path=previous_path, new_path=new_path, index=new_index
        )
        self.update_model_data()
        if move:
            self._model.post_move_item()
        self._dialog.close()
        self.event_data_changed()

    def setup_cash_account_dialog(
        self, edit: bool, item: CashAccount, max_position: int
    ) -> None:
        account_group_paths = self._get_account_group_paths()
        if edit:
            code_places_pairs = [(item.currency.code, item.currency.places)]
            self._dialog = CashAccountDialog(
                parent=self._view,
                max_position=max_position,
                paths=account_group_paths,
                code_places_pairs=code_places_pairs,
                edit=edit,
            )
            self._dialog.signal_OK.connect(self.edit_cash_account)
            self._dialog.initial_balance = item.initial_balance.value_rounded
        else:
            code_places_pairs = [
                (currency.code, currency.places)
                for currency in self._record_keeper.currencies
            ]
            self._dialog = CashAccountDialog(
                parent=self._view,
                max_position=max_position,
                paths=account_group_paths,
                code_places_pairs=code_places_pairs,
                edit=edit,
            )
            self._dialog.signal_OK.connect(self.add_cash_account)

    def add_cash_account(self) -> None:
        path = self._dialog.path
        index = self._dialog.position - 1
        currency_code = self._dialog.currency_code
        initial_balance = self._dialog.initial_balance

        logging.info("Adding CashAccount")
        try:
            self._record_keeper.add_cash_account(
                path, currency_code, initial_balance, index
            )
        except Exception:
            handle_exception()
            return

        item = self._model.get_selected_item()
        parent = item.parent if item is not None else None
        self._model.pre_add(parent)
        self.update_model_data()
        self._model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def edit_cash_account(self) -> None:
        item: CashAccount = self._model.get_selected_item()
        previous_parent = item.parent
        previous_path = self._dialog.current_path
        previous_index = self._get_current_index(item)
        new_path = self._dialog.path
        new_parent_path, _, _ = new_path.rpartition("/")
        new_parent = self._record_keeper.get_account_parent_or_none(new_parent_path)
        new_index = self._dialog.position - 1
        initial_balance = self._dialog.initial_balance

        logging.info(f"Editing CashAccount at path='{item.path}'")
        record_keeper_deepcopy = copy.deepcopy(self._record_keeper)
        try:
            logging.disable(logging.INFO)
            record_keeper_deepcopy.edit_cash_account(
                current_path=previous_path,
                new_path=new_path,
                initial_balance=initial_balance,
                index=new_index,
            )
            logging.disable(logging.NOTSET)
        except Exception:
            handle_exception()
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
        self._record_keeper.edit_cash_account(
            current_path=previous_path,
            new_path=new_path,
            initial_balance=initial_balance,
            index=new_index,
        )
        self.update_model_data()
        if move:
            self._model.post_move_item()
        self._dialog.close()
        self.event_data_changed()

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
        self._view.signal_selection_changed.connect(self._selection_changed)
        self._view.signal_expand_below.connect(self.expand_all_below)
        self._view.signal_delete_item.connect(self.remove_item)
        self._view.signal_add_account_group.connect(
            lambda: self.run_add_dialog(
                setup_dialog=self.setup_account_group_dialog,
            )
        )
        self._view.signal_add_security_account.connect(
            lambda: self.run_add_dialog(
                setup_dialog=self.setup_security_account_dialog,
            )
        )
        self._view.signal_add_cash_account.connect(
            lambda: self.run_add_dialog(
                setup_dialog=self.setup_cash_account_dialog,
            )
        )
        self._view.signal_edit_item.connect(self.edit_item)

        self._selection_changed()  # called to ensure context menu is OK at start of run

    def _selection_changed(self) -> None:
        item = self._model.get_selected_item()

        enable_modify_object = item is not None
        enable_add_objects = item is None or isinstance(item, AccountGroup)
        enable_expand_below = isinstance(item, AccountGroup)

        self._view.enable_actions(
            enable_add_objects=enable_add_objects,
            enable_modify_object=enable_modify_object,
            enable_expand_below=enable_expand_below,
        )

    def _get_account_group_paths(self) -> list[str]:
        return [
            account_group.path + "/"
            for account_group in self._record_keeper.account_groups
        ]
