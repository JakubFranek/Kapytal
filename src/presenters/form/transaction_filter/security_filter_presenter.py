from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.model_objects.security_objects import Security
from src.models.record_keeper import RecordKeeper
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.security_filter import SecurityFilter
from src.presenters.utilities.event import Event
from src.view_models.checkable_list_model import CheckableListModel
from src.views.forms.transaction_filter_form import TransactionFilterForm


class SecurityFilterPresenter:
    event_filter_changed = Event()

    def __init__(
        self, form: TransactionFilterForm, record_keeper: RecordKeeper
    ) -> None:
        self._form = form
        self._record_keeper = record_keeper
        self._initialize_model_and_proxy()
        self._connect_to_signals()

    @property
    def security_filter_mode(self) -> FilterMode:
        return self._form.security_filter_mode

    @property
    def checked_securities(self) -> tuple[Security, ...]:
        return self._model.checked_items

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._model.pre_reset_model()
        self._model.load_items(record_keeper.securities)
        self._model.load_checked_items(record_keeper.securities)
        self._model.post_reset_model()

    def load_from_security_filter(
        self,
        security_filter: SecurityFilter,
    ) -> None:
        self._form.security_filter_mode = security_filter.mode
        if security_filter.mode == FilterMode.OFF:
            return

        self._model.load_checked_items(security_filter.securities)

    def _select_all(self) -> None:
        self._model.load_checked_items(self._record_keeper.securities)

    def _unselect_all(self) -> None:
        self._model.load_checked_items(())

    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        self._proxy.setFilterWildcard(pattern)

    def _initialize_model_and_proxy(self) -> None:
        self._proxy = QSortFilterProxyModel()
        self._proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self._model = CheckableListModel(
            self._form.security_list_view,
            self._proxy,
        )
        self._model.event_checked_items_changed.append(self._update_checked_number)

        self._proxy.sort(0, Qt.SortOrder.AscendingOrder)
        self._proxy.setSourceModel(self._model)

        self._form.security_list_view.setModel(self._proxy)
        self._update_checked_number()

    def _connect_to_signals(self) -> None:
        self._form.signal_securities_search_text_changed.connect(self._filter)
        self._form.signal_securities_select_all.connect(self._select_all)
        self._form.signal_securities_unselect_all.connect(self._unselect_all)
        self._form.signal_securities_update_number_selected.connect(
            self._update_checked_number
        )

    def _update_checked_number(self) -> None:
        selected = len(self._model.checked_items)
        total = len(self._record_keeper.securities)
        self._form.set_selected_securities_number(selected, total)
