
from typing import TYPE_CHECKING

from src.models.model_objects.currency_objects import CashAmount, ExchangeRate
from src.models.model_objects.security_objects import Security
from src.models.online_quotes.functions import get_latest_quote
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.quotes_update_table_model import QuotesUpdateTableModel
from src.views.forms.quotes_update_form import QuotesUpdateForm
from src.views.utilities.message_box_functions import show_info_box

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal


class QuotesUpdateFormPresenter:
    event_data_changed = Event()

    def __init__(
        self,
        view: QuotesUpdateForm,
        record_keeper: RecordKeeper,
    ) -> None:
        self._view = view
        self._record_keeper = record_keeper
        self._quotes: dict[str, tuple[date, Decimal | CashAmount]] = {}
        self._initialize_models()
        self._connect_to_signals()
        self._view.set_button_state(download=True, save=False)

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
        data = [(item, "", "") for item in items]
        self._quotes = {}
        self._model.pre_reset_model()
        self._model.load_data(data)
        self._model.post_reset_model()
        self._unselect_all()

    def _initialize_models(self) -> None:
        self._model = QuotesUpdateTableModel(self._view.table_view)
        self._view.table_view.setModel(self._model)
        self._model.event_checked_items_changed.append(self._check_state_changed)

    def _connect_to_signals(self) -> None:
        self._view.signal_save.connect(self._save)
        self._view.signal_download.connect(self._download_quotes)
        self._view.signal_select_all.connect(self._select_all)
        self._view.signal_unselect_all.connect(self._unselect_all)

    def _save(self) -> None:
        checked_items = self._model.checked_items
        text = "The selected quotes have been saved:\n"
        for item in checked_items:
            try:
                date_, value = self._quotes[str(item)]
                if isinstance(item, Security):
                    item.set_price(date_, value)
                    text += (
                        f"- {item.symbol}: {value} on "
                        f"{date_.strftime(user_settings.settings.general_date_format)}\n"
                    )
                else:
                    item.set_rate(date_, value)
                    text += (
                        f"- {item}: {value:,} on "
                        f"{date_.strftime(user_settings.settings.general_date_format)}\n"
                    )
            except KeyError:  # noqa: PERF203
                pass
        self._view.set_button_state(download=True, save=False)
        self.event_data_changed()
        show_info_box(self._view, text.strip(), "Quotes saved")
        self._view.close()

    def _download_quotes(self) -> None:
        checked_items = self._model.checked_items
        for item in checked_items:
            data = (item, "Fetching...", "Fetching...")
            self._model.load_single_data(data)
            if isinstance(item, ExchangeRate):
                self._download_exchange_rate_quote(item)
            elif isinstance(item, Security):
                self._download_security_quote(item)
        self._view.set_button_state(download=True, save=True)

    def _download_security_quote(self, security: Security) -> None:
        try:
            date_, price = get_latest_quote(security.symbol)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        data = (
            security,
            date_.strftime(user_settings.settings.general_date_format),
            f"{price:,} {security.currency.code}",
        )
        self._model.load_single_data(data)
        self._quotes[str(security)] = (date_, CashAmount(price, security.currency))

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
        self._quotes[str(exchange_rate)] = (date_, rate)

    def _select_all(self) -> None:
        self._model.load_checked_items(self._model.items)

    def _unselect_all(self) -> None:
        self._model.load_checked_items([])

    def _check_state_changed(self) -> None:
        if len(self._model.checked_items) > 0:
            if all(str(item) in self._quotes for item in self._model.checked_items):
                self._view.set_button_state(download=True, save=True)
            else:
                self._view.set_button_state(download=True, save=False)
        else:
            self._view.set_button_state(download=False, save=False)
