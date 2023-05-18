import logging

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.model_objects.attributes import AttributeType
from src.models.record_keeper import RecordKeeper
from src.models.utilities.calculation import calculate_payee_stats
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.payee_table_model import PayeeTableModel
from src.views.dialogs.payee_dialog import PayeeDialog
from src.views.forms.payee_form import PayeeForm


class PayeeFormPresenter:
    event_data_changed = Event()

    def __init__(self, view: PayeeForm, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        self._proxy_model = QSortFilterProxyModel(self._view.tableView)
        self._model = PayeeTableModel(self._view.tableView, [], self._proxy_model)
        self.update_model_data()
        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._view.tableView.setModel(self._proxy_model)

        self._view.signal_add_payee.connect(lambda: self.run_payee_dialog(edit=False))
        self._view.signal_remove_payee.connect(self.remove_payee)
        self._view.signal_rename_payee.connect(lambda: self.run_payee_dialog(edit=True))
        self._view.signal_search_text_changed.connect(self._filter)

        self._view.finalize_setup()
        self._view.signal_selection_changed.connect(self._selection_changed)
        self._selection_changed()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper

    def reset_model(self) -> None:
        # TODO: add busy indicator here
        self._model.pre_reset_model()
        self.update_model_data()
        self._model.post_reset_model()

    def update_model_data(self) -> None:
        relevant_transactions = (
            self._record_keeper.cash_transactions
            + self._record_keeper.refund_transactions
        )
        self._model.payee_stats = calculate_payee_stats(
            relevant_transactions, self._record_keeper.base_currency
        ).values()

    def show_form(self) -> None:
        self.reset_model()
        self._view.show_form()

    def run_payee_dialog(self, *, edit: bool) -> None:
        self._dialog = PayeeDialog(self._view, edit=edit)
        if edit:
            payees = self._model.get_selected_items()
            if len(payees) == 0:
                raise ValueError("Cannot edit an unselected item.")
            if len(payees) > 1:
                raise ValueError("Cannot edit more than one item.")
            payee = payees[0]
            self._dialog.signal_ok.connect(self.rename_payee)
            self._dialog.name = payee.name
        else:
            self._dialog.signal_ok.connect(self.add_payee)
        logging.debug(f"Running PayeeDialog ({edit=})")
        self._dialog.exec()

    def add_payee(self) -> None:
        name = self._dialog.name

        logging.info("Adding Payee")
        try:
            self._record_keeper.add_payee(name)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._model.pre_add()
        self.update_model_data()
        self._model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def rename_payee(self) -> None:
        payees = self._model.get_selected_items()
        if len(payees) == 0:
            raise ValueError("Cannot edit an unselected item.")
        if len(payees) > 1:
            raise ValueError("Cannot edit more than one item.")
        payee = payees[0]
        current_name = payee.name
        new_name = self._dialog.name

        logging.info("Renaming Payee")
        try:
            self._record_keeper.edit_attribute(
                current_name, new_name, AttributeType.PAYEE
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self.update_model_data()
        self._dialog.close()
        self.event_data_changed()

    def remove_payee(self) -> None:
        payees = self._model.get_selected_items()
        if len(payees) == 0:
            raise ValueError("Cannot remove an unselected item.")

        logging.info(f"Removing {payees}")
        any_deleted = False
        for payee in payees:
            try:
                self._record_keeper.remove_payee(payee.name)
                self._model.pre_remove_item(payee)
                self.update_model_data()
                self._model.post_remove_item()
                any_deleted = True
            except Exception as exception:  # noqa: BLE001
                handle_exception(exception)
            finally:
                if any_deleted:
                    self.event_data_changed()

    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        logging.debug(f"Filtering Payees: {pattern=}")
        self._proxy_model.setFilterWildcard(pattern)

    def _selection_changed(self) -> None:
        payees = self._model.get_selected_items()
        is_payee_selected = len(payees) > 0
        is_one_payee_selected = len(payees) == 1
        self._view.enable_actions(
            is_payee_selected=is_payee_selected,
            is_one_payee_selected=is_one_payee_selected,
        )
