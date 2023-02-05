import logging

from src.models.model_objects.attributes import AttributeType
from src.models.record_keeper import RecordKeeper
from src.presenters.utilities.event import Event
from src.presenters.view_models.payee_list_model import PayeeListModel
from src.utilities.general import get_exception_display_info
from src.views.payee_dialog import PayeeDialog
from src.views.payee_form import PayeeForm
from src.views.utilities.handle_exception import display_error_message


class PayeeFormPresenter:
    event_data_changed = Event()

    def __init__(self, view: PayeeForm, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        self._model = PayeeListModel(self._view.listView, record_keeper.payees)
        self._view.listView.setModel(self._model)

        self._view.signal_add_payee.connect(lambda: self.run_payee_dialog(edit=False))
        self._view.signal_remove_payee.connect(self.remove_payee)
        self._view.signal_rename_payee.connect(lambda: self.run_payee_dialog(edit=True))
        self._view.signal_select_payee.connect(self.select_payee)

        self._view.listView.selectionModel().selectionChanged.connect(
            self._selection_changed
        )
        self._selection_changed()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._model.pre_reset_model()
        self._record_keeper = record_keeper
        self._model.payees = record_keeper.payees
        self._model.post_reset_model()

    def show_form(self) -> None:
        self._view.selectButton.setVisible(False)
        self._view.show_form()

    def run_payee_dialog(self, edit: bool) -> None:
        self._dialog = PayeeDialog(self._view, edit)
        if edit:
            item = self._model.get_selected_item()
            if item is None:
                raise ValueError("Cannot edit an unselected item.")
            self._dialog.signal_OK.connect(self.rename_payee)
            self._dialog.name = item.name
        else:
            self._dialog.signal_OK.connect(self.add_payee)
        logging.debug(f"Running PayeeDialog ({edit=})")
        self._dialog.exec()

    def add_payee(self) -> None:
        name = self._dialog.name

        logging.info("Adding Payee")
        try:
            self._record_keeper.add_payee(name)
        except Exception:
            self._handle_exception()
            return

        self._model.pre_add()
        self._model.payees = self._record_keeper.payees
        self._model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def rename_payee(self) -> None:
        payee = self._model.get_selected_item()
        if payee is None:
            raise ValueError("Cannot edit an unselected item.")
        current_name = payee.name
        new_name = self._dialog.name

        logging.info(f"Renaming Payee: {current_name=}, {new_name=}")
        try:
            self._record_keeper.edit_attribute(
                current_name, new_name, AttributeType.PAYEE
            )
        except Exception:
            self._handle_exception()
            return

        self._model.pre_add()
        self._model.payees = self._record_keeper.payees
        self._model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def remove_payee(self) -> None:
        payee = self._model.get_selected_item()
        if payee is None:
            return

        logging.info(f"Removing {payee}")
        try:
            self._record_keeper.remove_payee(payee.name)
        except Exception:
            self._handle_exception()
            return

        index = self._model.get_index_from_item(payee)
        self._model.pre_delete_item(index)
        self._model.payees = self._record_keeper.payees
        self._model.post_delete_item()
        self.event_data_changed()

    def select_payee(self) -> None:
        pass

    def _selection_changed(self) -> None:
        item = self._model.get_selected_item()
        is_payee_selected = item is not None
        self._view.removeButton.setEnabled(is_payee_selected)
        self._view.renameButton.setEnabled(is_payee_selected)
        self._view.selectButton.setEnabled(is_payee_selected)

    def _handle_exception(self) -> None:
        display_text, display_details = get_exception_display_info()  # type: ignore
        display_error_message(display_text, display_details)
