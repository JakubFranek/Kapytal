import logging

from src.models.record_keeper import RecordKeeper
from src.presenters.utilities.event import Event
from src.presenters.view_models.currency_table_model import CurrencyTableModel
from src.utilities.general import get_exception_display_info
from src.views.currency_dialog import CurrencyDialog
from src.views.currency_form import CurrencyForm
from src.views.utilities.handle_exception import display_error_message


class CurrencyFormPresenter:
    event_data_changed = Event()

    def __init__(self, view: CurrencyForm, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        self._currency_table_model = CurrencyTableModel(
            self._view.currencyTable, record_keeper.currencies
        )
        self._view.currencyTable.setModel(self._currency_table_model)

        self._view.signal_add_currency.connect(self.run_add_currency_dialog)
        self._view.signal_remove_currency.connect(self.remove_currency)

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._currency_table_model.pre_reset_model()
        self._record_keeper = record_keeper
        self._currency_table_model._data = record_keeper.currencies
        self._currency_table_model.post_reset_model()

    def show_form(self) -> None:
        logging.info("Showing CurrencyForm")
        self._view.show_form()

    def run_add_currency_dialog(self) -> None:
        self._dialog = CurrencyDialog(self._view)
        self._dialog.signal_OK.connect(self.add_currency)
        logging.info("Running CurrencyDialog")
        self._dialog.exec()

    def add_currency(self) -> None:
        code = self._dialog.currency_code
        places = self._dialog.currency_places

        logging.info(f"Adding Currency(code='{code}', places='{places}')")
        try:
            self._record_keeper.add_currency(code, places)
        except Exception:
            self._handle_exception()
            return

        self._currency_table_model.pre_add()
        self._currency_table_model._data = self._record_keeper.currencies
        self._currency_table_model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def remove_currency(self) -> None:
        currency = self._currency_table_model.get_selected_item()
        if currency is None:
            return

        logging.info(f"Removing Currency code='{currency.code}'")
        try:
            self._record_keeper.remove_currency(currency.code)
        except Exception:
            self._handle_exception()
            return

        index = self._currency_table_model.get_index_from_item(currency)
        self._currency_table_model.pre_delete_item(index)
        self._currency_table_model._data = self._record_keeper.currencies
        self._currency_table_model.post_delete_item()
        self.event_data_changed()

    def _handle_exception(self) -> None:
        display_text, display_details = get_exception_display_info()  # type: ignore
        display_error_message(display_text, display_details)
