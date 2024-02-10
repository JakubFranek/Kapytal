import logging

from src.models.base_classes.account import Account
from src.models.custom_exceptions import NotFoundError
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import CashAccount
from src.models.record_keeper import RecordKeeper
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.account_tree_model import AccountTreeModel
from src.views.dialogs.cash_account_dialog import CashAccountDialog
from src.views.utilities.handle_exception import display_error_message
from src.views.widgets.account_tree_widget import AccountTreeWidget


class CashAccountDialogPresenter:
    def __init__(
        self,
        view: AccountTreeWidget,
        model: AccountTreeModel,
        record_keeper: RecordKeeper,
    ) -> None:
        self._view = view
        self._record_keeper = record_keeper
        self._model = model
        self.event_update_model = Event()
        self.event_selection_changed = Event()
        self.event_data_changed = Event()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper

    def run_add_dialog(self) -> None:
        if len(self._record_keeper.currencies) == 0:
            display_error_message(
                "Create at least one Currency before creating a CashAccount.",
                title="Warning",
            )
            return

        account_group_paths = self._get_account_group_paths()
        code_decimals_pairs = [
            (currency.code, currency.decimals)
            for currency in self._record_keeper.currencies
        ]
        self._dialog = CashAccountDialog(
            parent=self._view,
            paths=account_group_paths,
            code_decimals_pairs=code_decimals_pairs,
            edit=False,
        )
        self._dialog.signal_ok.connect(self.add_cash_account)
        self._dialog.signal_path_changed.connect(self._update_dialog_position_limits)

        selected_item = self._model.get_selected_item()
        if selected_item is None:
            self._dialog.path = ""
            self._update_dialog_position_limits("")
        else:
            self._dialog.path = selected_item.path + "/"
        self._dialog.position = self._dialog.positionSpinBox.maximum()

        logging.debug("Running CashAccountDialog (edit=False)")
        self._dialog.exec()

    def run_edit_dialog(self) -> None:
        selected_item = self._model.get_selected_item()
        if not isinstance(selected_item, CashAccount):
            raise TypeError(f"Expected CashAccount, received {type(selected_item)}")

        account_group_paths = self._get_account_group_paths()
        code_decimals_pairs = (
            (selected_item.currency.code, selected_item.currency.decimals),
        )
        self._dialog = CashAccountDialog(
            parent=self._view,
            paths=account_group_paths,
            code_decimals_pairs=code_decimals_pairs,
            edit=True,
        )
        self._dialog.signal_ok.connect(self.edit_cash_account)
        self._dialog.signal_path_changed.connect(self._update_dialog_position_limits)

        self._dialog.initial_balance = selected_item.initial_balance.value_rounded

        if selected_item is None:
            raise ValueError("Cannot edit an unselected item.")
        self._dialog.current_path = selected_item.path
        self._dialog.path = selected_item.path
        self._dialog.position = self._get_item_index(selected_item) + 1

        logging.debug("Running CashAccountDialog (edit=True)")
        self._dialog.exec()

    def add_cash_account(self) -> None:
        path = self._dialog.path
        index = self._dialog.position - 1
        currency_code = self._dialog.currency_code
        initial_balance = self._dialog.initial_balance

        logging.info(
            f"Adding CashAccount: {path=}, {index=}, "
            f"initial_balance={initial_balance} {currency_code}"
        )
        try:
            self._record_keeper.add_cash_account(
                path, currency_code, initial_balance, index
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        parent = self._get_parent_from_path(path)
        new_account = self._record_keeper.get_account(path, CashAccount)
        index_actual = self._get_item_index(new_account)

        self._model.pre_add(parent, index_actual)
        self.event_update_model()
        self._model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def edit_cash_account(self) -> None:
        item = self._model.get_selected_item()
        if not isinstance(item, CashAccount):
            raise TypeError(f"Expected CashAccount, received {type(item)}")
        previous_parent = item.parent
        previous_path = self._dialog.current_path
        previous_index = self._get_item_index(item)
        new_path = self._dialog.path
        new_parent_path, _, _ = new_path.rpartition("/")
        try:
            new_parent = self._record_keeper.get_account_group_or_none(new_parent_path)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return
        new_index = self._dialog.position - 1
        initial_balance = self._dialog.initial_balance

        logging.info(
            f"Editing CashAccount at path='{item.path}', index={previous_index}, "
            f"initial_balance={item.initial_balance.to_str_rounded()}: "
            f"new path={new_path}, new index={new_index}, "
            f"new initial_balance={initial_balance} {item.currency.code}"
        )
        try:
            self._record_keeper.edit_cash_account(
                current_path=previous_path,
                new_path=new_path,
                initial_balance=initial_balance,
                index=new_index,
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        edit_account = self._record_keeper.get_account(new_path, CashAccount)
        new_index_actual = self._get_item_index(edit_account)

        move = new_parent != previous_parent or new_index_actual != previous_index

        if move:
            self._model.pre_move_item(
                previous_parent=previous_parent,
                previous_index=previous_index,
                new_parent=new_parent,
                new_index=new_index_actual,
            )
        self.event_update_model()
        if move:
            self._model.post_move_item()
        self._dialog.close()
        self.event_data_changed()

    def _update_dialog_position_limits(self, path: str) -> None:
        if self._dialog.edit:
            self._update_edit_dialog_position_limits(path)
        else:
            self._update_add_dialog_position_limits(path)

    def _update_add_dialog_position_limits(self, path: str) -> None:
        parent_path, _, _ = path.rpartition("/")

        if not parent_path:
            maximum_position = len(self._record_keeper.root_account_items) + 1
        else:
            try:
                parent = self._record_keeper.get_account_group(parent_path)
                maximum_position = len(parent.children) + 1
            except NotFoundError:
                maximum_position = 1

        self._dialog.maximum_position = maximum_position

    def _update_edit_dialog_position_limits(self, path: str) -> None:
        current_path = self._dialog.current_path
        try:
            current_account = self._record_keeper.get_account(current_path, CashAccount)
        except NotFoundError:
            return
        parent_path, _, _ = path.rpartition("/")

        if not parent_path:
            maximum_position = len(self._record_keeper.root_account_items)
            if current_account not in self._record_keeper.root_account_items:
                maximum_position += 1
        else:
            try:
                parent = self._record_keeper.get_account_group(parent_path)
                maximum_position = len(parent.children)
                if current_account not in parent.children:
                    maximum_position += 1
            except NotFoundError:
                maximum_position = 1

        self._dialog.maximum_position = maximum_position

    def _get_account_group_paths(self) -> tuple[str, ...]:
        return tuple(
            account_group.path + "/"
            for account_group in self._record_keeper.account_groups
        )

    def _get_parent_from_path(self, path: str) -> AccountGroup | None:
        if "/" not in path:
            return None
        parent_path, _, _ = path.rpartition("/")
        try:
            return self._record_keeper.get_account_group_or_none(parent_path)
        except NotFoundError:
            return None

    def _get_item_index(self, item: AccountGroup | Account | None) -> int:
        if item is None:
            raise NotImplementedError
        parent = item.parent
        if parent is None:
            return self._record_keeper.root_account_items.index(item)
        return parent.children.index(item)
