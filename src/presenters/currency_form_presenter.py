import logging
from datetime import datetime
from decimal import Decimal

import src.models.user_settings.user_settings as user_settings
from src.models.custom_exceptions import InvalidOperationError
from src.models.record_keeper import RecordKeeper
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.currency_table_model import CurrencyTableModel
from src.view_models.exchange_rate_table_model import ExchangeRateTableModel
from src.views.dialogs.add_exchange_rate_dialog import AddExchangeRateDialog
from src.views.dialogs.currency_dialog import CurrencyDialog
from src.views.dialogs.set_exchange_rate_dialog import SetExchangeRateDialog
from src.views.forms.currency_form import CurrencyForm
from src.views.utilities.message_box_functions import ask_yes_no_question


class CurrencyFormPresenter:
    event_data_changed = Event()
    event_base_currency_changed = Event()

    def __init__(self, view: CurrencyForm, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        self._currency_table_model = CurrencyTableModel(
            self._view.currencyTable,
            record_keeper.currencies,
            record_keeper.base_currency,
        )
        self._view.currencyTable.setModel(self._currency_table_model)

        self._exchange_rate_table_model = ExchangeRateTableModel(
            self._view.exchangeRateTable, record_keeper.exchange_rates
        )
        self._view.exchangeRateTable.setModel(self._exchange_rate_table_model)

        self._view.signal_add_currency.connect(self.run_add_currency_dialog)
        self._view.signal_set_base_currency.connect(self.set_base_currency)
        self._view.signal_remove_currency.connect(self.remove_currency)
        self._view.signal_add_exchange_rate.connect(self.run_add_exchange_rate_dialog)
        self._view.signal_set_exchange_rate.connect(self.run_set_exchange_rate_dialog)
        self._view.signal_remove_exchange_rate.connect(self.remove_exchange_rate)

        self._view.finalize_setup()

        self._view.signal_exchange_rate_selection_changed.connect(
            self._exchange_rate_selection_changed
        )
        self._view.signal_currency_selection_changed.connect(
            self._currency_selection_changed
        )
        self._exchange_rate_selection_changed()
        self._currency_selection_changed()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._currency_table_model.pre_reset_model()
        self._exchange_rate_table_model.pre_reset_model()
        self._record_keeper = record_keeper
        self._currency_table_model.currencies = record_keeper.currencies
        self._currency_table_model.base_currency = record_keeper.base_currency
        self._exchange_rate_table_model.exchange_rates = record_keeper.exchange_rates
        self._currency_table_model.post_reset_model()
        self._exchange_rate_table_model.post_reset_model()

    def show_form(self) -> None:
        self._view.show_form()

    def run_add_currency_dialog(self) -> None:
        self._dialog = CurrencyDialog(self._view)
        self._dialog.signal_OK.connect(self.add_currency)
        logging.debug("Running CurrencyDialog")
        self._dialog.exec()

    def add_currency(self) -> None:
        previous_base_currency = self._record_keeper.base_currency
        code = self._dialog.currency_code
        places = self._dialog.currency_places

        logging.info(f"Adding Currency(code='{code}', places='{places}')")
        try:
            self._record_keeper.add_currency(code, places)
        except Exception:
            handle_exception()
            return

        self._currency_table_model.pre_add()
        self._currency_table_model.currencies = self._record_keeper.currencies
        self._currency_table_model.base_currency = self._record_keeper.base_currency
        self._currency_table_model.post_add()
        self._dialog.close()
        self.event_data_changed()
        if self._record_keeper.base_currency != previous_base_currency:
            self.event_base_currency_changed()

    def set_base_currency(self) -> None:
        currency = self._currency_table_model.get_selected_item()
        if currency is None:
            raise InvalidOperationError("Cannot set an unselected Currency as base.")

        logging.info(f"Setting {currency.code} as base currency")
        try:
            self._record_keeper.set_base_currency(currency.code)
        except Exception:
            handle_exception()
            return

        self._currency_table_model.currencies = self._record_keeper.currencies
        self._currency_table_model.base_currency = self._record_keeper.base_currency
        self.event_base_currency_changed()
        self.event_data_changed()
        self._view.refresh_currency_table()

    def remove_currency(self) -> None:
        previous_base_currency = self._record_keeper.base_currency
        currency = self._currency_table_model.get_selected_item()
        if currency is None:
            raise InvalidOperationError("Cannot remove an unselected Currency.")

        logging.info(f"Removing {currency}")
        try:
            self._record_keeper.remove_currency(currency.code)
        except Exception:
            handle_exception()
            return

        self._currency_table_model.pre_remove_item(currency)
        self._currency_table_model.currencies = self._record_keeper.currencies
        self._currency_table_model.base_currency = self._record_keeper.base_currency
        self._currency_table_model.post_remove_item()
        self.event_data_changed()
        if self._record_keeper.base_currency != previous_base_currency:
            self.event_base_currency_changed()

    def run_add_exchange_rate_dialog(self) -> None:
        codes = [currency.code for currency in self._record_keeper.currencies]
        self._dialog = AddExchangeRateDialog(currency_codes=codes, parent=self._view)
        self._dialog.signal_OK.connect(self.add_exchange_rate)
        logging.debug("Running AddExchangeRateDialog")
        self._dialog.exec()

    def add_exchange_rate(self) -> None:
        primary_code = self._dialog.primary_currency_code
        secondary_code = self._dialog.secondary_currency_code

        logging.info(f"Adding ExchangeRate({primary_code}/{secondary_code})")
        try:
            self._record_keeper.add_exchange_rate(primary_code, secondary_code)
        except Exception:
            handle_exception()
            return

        self._exchange_rate_table_model.pre_add()
        self._exchange_rate_table_model.exchange_rates = (
            self._record_keeper.exchange_rates
        )
        self._exchange_rate_table_model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def run_set_exchange_rate_dialog(self) -> None:
        exchange_rate = self._exchange_rate_table_model.get_selected_item()
        if exchange_rate is None:
            raise ValueError("An ExchangeRate must be selected to set its value.")
        exchange_rate_code = str(exchange_rate)
        last_value = exchange_rate.latest_rate
        last_value = last_value if last_value.is_finite() else Decimal(1)
        self._dialog = SetExchangeRateDialog(
            date_today=datetime.now(user_settings.settings.time_zone).date(),
            exchange_rate=exchange_rate_code,
            last_value=last_value,
            parent=self._view,
        )
        self._dialog.signal_OK.connect(self.set_exchange_rate)
        logging.debug("Running SetExchangeRateDialog")
        self._dialog.exec()

    def set_exchange_rate(self) -> None:
        value = self._dialog.value.normalize()
        date_ = self._dialog.date_
        exchange_rate_code = self._dialog.exchange_rate_code
        logging.info(f"Setting ExchangeRate({exchange_rate_code}): {value} on {date_}")
        try:
            self._record_keeper.set_exchange_rate(exchange_rate_code, value, date_)
        except Exception:
            handle_exception()
            return

        self._exchange_rate_table_model.exchange_rates = (
            self._record_keeper.exchange_rates
        )
        self._dialog.close()
        self.event_data_changed()

    def remove_exchange_rate(self) -> None:
        exchange_rate = self._exchange_rate_table_model.get_selected_item()
        if exchange_rate is None:
            raise InvalidOperationError("Cannot remove an unselected ExchangeRate.")

        logging.debug(
            "ExchangeRate deletion requested, asking the user for confirmation"
        )
        proceed_with_delete = ask_yes_no_question(
            self._view,
            question=f"Do you want to delete the {str(exchange_rate)} exchange rate?",
            title="Are you sure?",
        )
        if not proceed_with_delete:
            logging.debug("User cancelled the ExchangeRate deletion")
            return

        logging.info(f"Removing {repr(exchange_rate)}")
        try:
            self._record_keeper.remove_exchange_rate(str(exchange_rate))
        except Exception:
            handle_exception()
            return

        self._exchange_rate_table_model.pre_remove_item(exchange_rate)
        self._exchange_rate_table_model.exchange_rates = (
            self._record_keeper.exchange_rates
        )
        self._exchange_rate_table_model.post_remove_item()
        self.event_data_changed()

    def _exchange_rate_selection_changed(self) -> None:
        item = self._exchange_rate_table_model.get_selected_item()
        is_exchange_rate_selected = item is not None
        self._view.set_exchange_rate_buttons(is_exchange_rate_selected)

    def _currency_selection_changed(self) -> None:
        item = self._currency_table_model.get_selected_item()
        is_currency_selected = item is not None
        self._view.set_currency_buttons(is_currency_selected)
