import copy
import logging
from typing import Protocol

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.base_classes.account import Account
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.currency_objects import (
    CashAmount,
    ConversionFactorNotFoundError,
)
from src.models.model_objects.security_objects import SecurityAccount
from src.models.record_keeper import RecordKeeper
from src.presenters.form.security_account_form_presenter import (
    SecurityAccountFormPresenter,
)
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.account_tree_model import AccountTreeModel
from src.views.constants import AccountTreeColumn
from src.views.dialogs.account_group_dialog import AccountGroupDialog
from src.views.dialogs.cash_account_dialog import CashAccountDialog
from src.views.dialogs.security_account_dialog import SecurityAccountDialog
from src.views.utilities.handle_exception import display_error_message
from src.views.widgets.account_tree_widget import AccountTreeWidget

# REFACTOR: split dialog presenters into separate classes?
# REFACTOR: remove RecordKeeper deepcopying somehow
# possibilities:
# 1. add RecordKeeper validation method to run before adding?


class SetupDialogCallable(Protocol):
    """Custom Callable type for setting up dialogs"""

    def __call__(
        self, item: Account | AccountGroup | None, max_position: int, *, edit: bool
    ) -> bool:
        ...


class AccountTreePresenter:
    event_data_changed = Event()
    event_check_state_changed = Event()

    def __init__(self, view: AccountTreeWidget, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        self._security_account_form_presenter = SecurityAccountFormPresenter(
            self._view, self._record_keeper
        )

        self._initialize_models()
        self._initialize_signals()
        self._view.finalize_setup()
        self._reset_sort_order()
        self.event_check_state_changed()

    @property
    def valid_accounts(self) -> tuple[Account, ...]:
        return self._model.checked_accounts

    def set_widget_visibility(self, *, visible: bool) -> None:
        if visible and self._view.isHidden():
            logging.debug("Showing AccountTreeWidget")
            self._view.show()
        elif not visible and not self._view.isHidden():
            logging.debug("Hiding AccountTreeWidget")
            self._view.hide()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._model.pre_reset_model()
        self._record_keeper = record_keeper
        self.update_model_data()
        self._model.post_reset_model()
        self._security_account_form_presenter.load_record_keeper(record_keeper)
        self.event_check_state_changed()

    def refresh_view(self) -> None:
        self._view.refresh()

    def update_geometries(self) -> None:
        self._view.treeView.updateGeometries()

    def update_model_data(self) -> None:
        self._model.flat_items = self._record_keeper.account_items
        self._model.base_currency = self._record_keeper.base_currency
        self.update_total_balance()

    def update_total_balance(self) -> None:
        try:
            total = sum(
                (
                    item.get_balance(self._record_keeper.base_currency)
                    for item in self._record_keeper.root_account_items
                ),
                CashAmount(0, self._record_keeper.base_currency),
            )
            total = total.to_str_rounded()
        except ConversionFactorNotFoundError:
            total = "Error!"
        self._view.set_total_base_balance(total)

    def expand_all_below(self) -> None:
        indexes = self._view.treeView.selectedIndexes()
        if len(indexes) == 0:
            raise ValueError("No index to expand recursively selected.")
        item = self._model.get_selected_item()
        logging.debug(f"Expanding all nodes below {item}")
        self._view.treeView.expandRecursively(indexes[0])  # view index required here

    def edit_item(self) -> None:
        item = self._model.get_selected_item()
        setup_dialog: SetupDialogCallable
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
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
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
        setup_ok = setup_dialog(item, max_position, edit=False)
        if not setup_ok:
            return
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
        setup_dialog(item, max_position, edit=True)
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
        self,
        item: AccountGroup,
        max_position: int,
        *,
        edit: bool,
    ) -> bool:
        del item
        account_group_paths = self._get_account_group_paths()
        if edit:
            self._dialog = AccountGroupDialog(
                parent=self._view,
                max_position=max_position,
                paths=account_group_paths,
                edit=edit,
            )
            self._dialog.signal_ok.connect(self.edit_account_group)
        else:
            self._dialog = AccountGroupDialog(
                parent=self._view,
                max_position=max_position,
                paths=account_group_paths,
                edit=edit,
            )
            self._dialog.signal_ok.connect(self.add_account_group)
        return True

    def add_account_group(self) -> None:
        path = self._dialog.path
        index = self._dialog.position - 1

        logging.info("Adding AccountGroup")
        record_keeper_copy = copy.deepcopy(self._record_keeper)
        try:
            logging.disable(logging.INFO)
            record_keeper_copy.add_account_group(path, index)
            logging.disable(logging.NOTSET)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        item = self._model.get_selected_item()
        self._model.pre_add(item)
        self._record_keeper.add_account_group(path, index)
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
        try:
            new_parent = self._record_keeper.get_account_parent_or_none(new_parent_path)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return
        new_index = self._dialog.position - 1

        logging.info(f"Editing AccountGroup at path='{item.path}'")
        record_keeper_copy = copy.deepcopy(self._record_keeper)
        try:
            logging.disable(logging.INFO)
            record_keeper_copy.edit_account_group(
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
        self,
        item: SecurityAccount,
        max_position: int,
        *,
        edit: bool,
    ) -> None:
        del item
        account_group_paths = self._get_account_group_paths()
        if edit:
            self._dialog = SecurityAccountDialog(
                parent=self._view,
                max_position=max_position,
                paths=account_group_paths,
                edit=edit,
            )
            self._dialog.signal_ok.connect(self.edit_security_account)
        else:
            self._dialog = SecurityAccountDialog(
                parent=self._view,
                max_position=max_position,
                paths=account_group_paths,
                edit=edit,
            )
            self._dialog.signal_ok.connect(self.add_security_account)
        return True

    def add_security_account(self) -> None:
        path = self._dialog.path
        index = self._dialog.position - 1

        logging.info("Adding SecurityAccount")
        record_keeper_copy = copy.deepcopy(self._record_keeper)
        try:
            logging.disable(logging.INFO)
            record_keeper_copy.add_security_account(path, index)
            logging.disable(logging.NOTSET)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        item = self._model.get_selected_item()
        self._model.pre_add(item)
        self._record_keeper.add_security_account(path, index)
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
        try:
            new_parent = self._record_keeper.get_account_parent_or_none(new_parent_path)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return
        new_index = self._dialog.position - 1

        logging.info(f"Editing SecurityAccount at path='{item.path}'")
        record_keeper_deepcopy = copy.deepcopy(self._record_keeper)
        try:
            logging.disable(logging.INFO)
            record_keeper_deepcopy.edit_security_account(
                current_path=previous_path, new_path=new_path, index=previous_index
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
        self._record_keeper.edit_security_account(
            current_path=previous_path, new_path=new_path, index=new_index
        )
        self.update_model_data()
        if move:
            self._model.post_move_item()
        self._dialog.close()
        self.event_data_changed()

    def setup_cash_account_dialog(
        self,
        item: CashAccount | None,
        max_position: int,
        *,
        edit: bool,
    ) -> None:
        if len(self._record_keeper.currencies) == 0:
            display_error_message(
                "Create at least one Currency before creating a CashAccount.",
                title="Warning",
            )
            return False

        account_group_paths = self._get_account_group_paths()
        if edit:
            if not isinstance(item, CashAccount):
                raise TypeError(f"Expected CashAccount, received {type(item)}")
            code_places_pairs = [(item.currency.code, item.currency.places)]
            self._dialog = CashAccountDialog(
                parent=self._view,
                max_position=max_position,
                paths=account_group_paths,
                code_places_pairs=code_places_pairs,
                edit=edit,
            )
            self._dialog.signal_ok.connect(self.edit_cash_account)
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
            self._dialog.signal_ok.connect(self.add_cash_account)
        return True

    def add_cash_account(self) -> None:
        path = self._dialog.path
        index = self._dialog.position - 1
        currency_code = self._dialog.currency_code
        initial_balance = self._dialog.initial_balance

        logging.info("Adding CashAccount")
        record_keeper_copy = copy.deepcopy(self._record_keeper)
        try:
            logging.disable(logging.INFO)
            record_keeper_copy.add_cash_account(
                path, currency_code, initial_balance, index
            )
            logging.disable(logging.NOTSET)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        item = self._model.get_selected_item()
        self._model.pre_add(item)
        self._record_keeper.add_cash_account(
            path, currency_code, initial_balance, index
        )
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
        try:
            new_parent = self._record_keeper.get_account_parent_or_none(new_parent_path)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return
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

    def _initialize_models(self) -> None:
        self._proxy = QSortFilterProxyModel(self._view)
        self._proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setFilterRole(Qt.ItemDataRole.UserRole + 1)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setRecursiveFilteringEnabled(True)  # noqa: FBT003
        self._model = AccountTreeModel(
            view=self._view.treeView,
            proxy=self._proxy,
            flat_items=self._record_keeper.root_account_items,
            base_currency=self._record_keeper.base_currency,
        )
        self._proxy.setSourceModel(self._model)
        self._view.treeView.setModel(self._proxy)

    def _initialize_signals(self) -> None:
        self._view.signal_selection_changed.connect(self._selection_changed)
        self._view.signal_expand_below.connect(self.expand_all_below)

        self._view.signal_reset_sort_order.connect(self._reset_sort_order)
        self._view.signal_sort.connect(lambda index: self._sort(index))

        self._view.signal_show_all.connect(
            lambda: self._set_check_state_all(visible=True)
        )
        self._view.signal_show_selection_only.connect(self._set_check_state_only)
        self._view.signal_hide_all.connect(
            lambda: self._set_check_state_all(visible=False)
        )
        self._view.signal_select_all_cash_accounts_below.connect(
            self._check_all_cash_accounts_below
        )
        self._view.signal_select_all_security_accounts_below.connect(
            self._check_all_security_accounts_below
        )

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
        self._view.signal_delete_item.connect(self.remove_item)

        self._view.signal_show_securities.connect(self._show_security_account_contents)

        self._view.signal_search_text_changed.connect(self._filter)

        self._model.signal_check_state_changed.connect(self.event_check_state_changed)

        self._selection_changed()  # called to ensure context menu is OK at start of run

    def _selection_changed(self) -> None:
        item = self._model.get_selected_item()

        enable_modify_object = item is not None
        enable_add_objects = item is None or isinstance(item, AccountGroup)
        enable_expand_below = isinstance(item, AccountGroup)
        enable_show_securities = isinstance(item, SecurityAccount)

        self._view.enable_actions(
            enable_add_objects=enable_add_objects,
            enable_modify_object=enable_modify_object,
            enable_expand_below=enable_expand_below,
            enable_show_securities=enable_show_securities,
        )

    def _get_account_group_paths(self) -> list[str]:
        return [
            account_group.path + "/"
            for account_group in self._record_keeper.account_groups
        ]

    def _set_check_state_all(self, *, visible: bool) -> None:
        self._model.set_check_state_all(checked=visible)
        self._view.refresh()
        self.event_check_state_changed()

    def _set_check_state_only(self) -> None:
        self._model.set_selected_check_state(checked=True, only=True)
        self._view.refresh()
        self.event_check_state_changed()

    def _check_all_cash_accounts_below(self) -> None:
        account_group = self._model.get_selected_item()
        if not isinstance(account_group, AccountGroup):
            raise TypeError(f"Selected item is not an AccountGroup: {account_group}")
        logging.debug(f"Selecting all Cash Accounts below path='{account_group.path}'")
        self._model.select_all_cash_accounts_below(account_group)
        self.event_check_state_changed()

    def _check_all_security_accounts_below(self) -> None:
        account_group = self._model.get_selected_item()
        if not isinstance(account_group, AccountGroup):
            raise TypeError(f"Selected item is not an AccountGroup: {account_group}")
        logging.debug(
            f"Selecting all Security Accounts below path='{account_group.path}'"
        )
        self._model.select_all_security_accounts_below(account_group)
        self.event_check_state_changed()

    def _sort(self, index: int) -> None:
        sort_order = self._view.sort_order
        logging.debug(
            f"Sorting AccountTree: column={AccountTreeColumn(index).name}, "
            f"order={sort_order.name}"
        )
        self._proxy.sort(index, sort_order)

    def _reset_sort_order(self) -> None:
        logging.debug("Resetting AccountTree sort order")
        self._proxy.sort(-1)
        self._view.treeView.header().setSortIndicatorShown(False)  # noqa: FBT003

    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        logging.debug(f"Filtering Accounts: {pattern=}")
        self._proxy.setFilterWildcard(pattern)
        self._view.treeView.expandAll()

    def _show_security_account_contents(self) -> None:
        selected_item = self._model.get_selected_item()
        if not isinstance(selected_item, SecurityAccount):
            raise TypeError(f"Selected item is not a SecurityAccount: {selected_item}")
        self._security_account_form_presenter.show(selected_item)
