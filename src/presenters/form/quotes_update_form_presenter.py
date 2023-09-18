import logging

from src.models.model_objects.currency_objects import ExchangeRate
from src.models.model_objects.security_objects import Security
from src.models.online_quotes.functions import get_latest_quote
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.quotes_update_table_model import QuotesUpdateTableModel
from src.views.forms.quotes_update_form import QuotesUpdateForm


class QuotesUpdateFormPresenter:
    event_data_changed = Event()

    def __init__(
        self,
        view: QuotesUpdateForm,
        record_keeper: RecordKeeper,
    ) -> None:
        self._view = view
        self._record_keeper = record_keeper
        self._initialize_models()
        self._connect_to_signals()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper

    def show_form(self) -> None:
        self._update_model_data()
        self._view.show_form()

    def _update_model_data(self) -> None:
        exchange_rates = list(self._record_keeper.exchange_rates)
        securities = [
            security for security in self._record_keeper.securities if security.symbol
        ]
        items = exchange_rates + securities
        data = [(item, "...", "...") for item in items]
        self._model.pre_reset_model()
        self._model.load_data(data)
        self._model.post_reset_model()

    def _initialize_models(self) -> None:
        self._model = QuotesUpdateTableModel(self._view.table_view)
        self._view.table_view.setModel(self._model)

    def _connect_to_signals(self) -> None:
        self._view.signal_save.connect(self._save)
        self._view.signal_download.connect(self._download_quotes)

    def _save(self) -> None:
        pass

    def _download_quotes(self) -> None:
        checked_items = self._model.checked_items
        for item in checked_items:
            data = (item, "Fetching...", "Fetching...")
            self._model.load_single_data(data)
            if isinstance(item, ExchangeRate):
                self._download_exchange_rate_quote(item)
            elif isinstance(item, Security):
                self._download_security_quote(item)

    def _download_security_quote(self, security: Security) -> None:
        try:
            date_, price = get_latest_quote(security.symbol)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        data = (
            security,
            date_.strftime(user_settings.settings.general_date_format),
            f"{price:,}",
        )
        self._model.load_single_data(data)

    def _download_exchange_rate_quote(self, exchange_rate: ExchangeRate) -> None:
        exchange_rate_ticker = (
            exchange_rate.primary_currency.code
            + exchange_rate.secondary_currency.code
            + "=X"
        )
        try:
            date_, rate = get_latest_quote(exchange_rate_ticker)
        except Exception:  # noqa: BLE001
            try:
                exchange_rate_ticker = (
                    exchange_rate.primary_currency.code
                    + "-"
                    + exchange_rate.secondary_currency.code
                )
                date_, rate = get_latest_quote(exchange_rate_ticker)
            except Exception as exception:  # noqa: BLE001
                handle_exception(exception)
                return

        data = (
            exchange_rate,
            date_.strftime(user_settings.settings.general_date_format),
            f"{rate:,}",
        )
        self._model.load_single_data(data)
