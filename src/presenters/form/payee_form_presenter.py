import logging

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.model_objects.attributes import AttributeType
from src.models.record_keeper import RecordKeeper
from src.models.utilities.calculation import AttributeStats, get_payee_stats
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
        self._model.pre_reset_model()
        self._record_keeper = record_keeper
        self.update_model_data()
        self._model.post_reset_model()

    def update_model_data(self) -> None:
        payee_stats: list[AttributeStats] = []
        for payee in self._record_keeper.payees:
            payee_stats.append(
                get_payee_stats(
                    payee,
                    self._record_keeper.transactions,
                    self._record_keeper.base_currency,
                )
            )
        self._model.payee_stats = payee_stats

    def show_form(self) -> None:
        self._model.pre_reset_model()
        self.update_model_data()
        self._model.post_reset_model()
        self._view.selectButton.setVisible(False)  # noqa: FBT003
        self._view.show_form()

    def run_payee_dialog(self, *, edit: bool) -> None:
        self._dialog = PayeeDialog(self._view, edit=edit)
        if edit:
            item = self._model.get_selected_item()
            if item is None:
                raise ValueError("Cannot edit an unselected item.")
            self._dialog.signal_ok.connect(self.rename_payee)
            self._dialog.name = item.name
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
        payee = self._model.get_selected_item()
        if payee is None:
            raise ValueError("Cannot edit an unselected item.")
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
        payee = self._model.get_selected_item()
        if payee is None:
            return

        logging.info(f"Removing {payee}")
        try:
            self._record_keeper.remove_payee(payee.name)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._model.pre_remove_item(payee)
        self.update_model_data()
        self._model.post_remove_item()
        self.event_data_changed()

    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        logging.debug(f"Filtering Payees: {pattern=}")
        self._proxy_model.setFilterWildcard(pattern)

    def _selection_changed(self) -> None:
        item = self._model.get_selected_item()
        is_payee_selected = item is not None
        self._view.set_buttons(is_payee_selected=is_payee_selected)
