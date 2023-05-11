from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.model_objects.currency_objects import Currency
from src.models.record_keeper import RecordKeeper
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.currency_filter import CurrencyFilter
from src.view_models.checkable_list_model import CheckableListModel
from src.views.forms.transaction_filter_form import TransactionFilterForm


class CurrencyFilterPresenter:
    def __init__(
        self, form: TransactionFilterForm, record_keeper: RecordKeeper
    ) -> None:
        self._form = form
        self._record_keeper = record_keeper
        self._initialize_model_and_proxy()
        self._connect_to_signals()

    @property
    def currency_filter_mode(self) -> FilterMode:
        return FilterMode.KEEP if self._form.currency_filter_active else FilterMode.OFF

    @property
    def checked_currencies(self) -> tuple[Currency, ...]:
        return self._currency_list_model.checked_items

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._currency_list_model.pre_reset_model()
        self._currency_list_model.items = record_keeper.currencies
        self._currency_list_model.checked_items = record_keeper.currencies
        self._currency_list_model.post_reset_model()

    def load_from_currency_filter(
        self,
        currency_filter: CurrencyFilter,
    ) -> None:
        self._form.currency_filter_active = currency_filter.mode != FilterMode.OFF
        if currency_filter.mode == FilterMode.OFF:
            return

        self._currency_list_model.pre_reset_model()
        if currency_filter.mode == FilterMode.KEEP:
            self._form.currency_filter_active = True
            self._currency_list_model.checked_items = currency_filter.currencies
        else:
            self._currency_list_model.checked_items = [
                currency
                for currency in self._record_keeper.currencies
                if currency not in currency_filter.currencies
            ]
        self._currency_list_model.post_reset_model()

    def _select_all(self) -> None:
        self._currency_list_model.pre_reset_model()
        self._currency_list_model.checked_items = self._record_keeper.currencies
        self._currency_list_model.post_reset_model()

    def _unselect_all(self) -> None:
        self._currency_list_model.pre_reset_model()
        self._currency_list_model.checked_items = ()
        self._currency_list_model.post_reset_model()

    def _initialize_model_and_proxy(self) -> None:
        self._currency_list_proxy = QSortFilterProxyModel()
        self._currency_list_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._currency_list_proxy.setSortCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )

        self._currency_list_model = CheckableListModel(
            self._form.currency_list_view,
            self._record_keeper.currencies,
            self._record_keeper.currencies,
            self._currency_list_proxy,
        )

        self._currency_list_proxy.sort(0, Qt.SortOrder.AscendingOrder)
        self._currency_list_proxy.setSourceModel(self._currency_list_model)

        self._form.currency_list_view.setModel(self._currency_list_proxy)

    def _connect_to_signals(self) -> None:
        self._form.signal_currencies_select_all.connect(self._select_all)
        self._form.signal_currencies_unselect_all.connect(self._unselect_all)
