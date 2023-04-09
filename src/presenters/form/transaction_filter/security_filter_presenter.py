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
    def checked_securities(self) -> tuple[Security, ...]:
        return self._security_list_model.checked_items

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._security_list_model.pre_reset_model()
        self._security_list_model.items = record_keeper.securities
        self._security_list_model.checked_items = record_keeper.securities
        self._security_list_model.post_reset_model()

    def load_from_security_filter(
        self,
        security_filter: SecurityFilter,
    ) -> None:
        self._security_list_model.pre_reset_model()
        if security_filter.mode == FilterMode.KEEP:
            self._security_list_model.checked_items = security_filter.securities
        elif security_filter.mode == FilterMode.OFF:
            self._security_list_model.checked_items = self._record_keeper.securities
        else:
            self._security_list_model.checked_items = [
                security
                for security in self._record_keeper.securities
                if security not in security_filter.securities
            ]
        self._security_list_model.post_reset_model()

    def _select_all(self) -> None:
        self._security_list_model.pre_reset_model()
        self._security_list_model.checked_items = self._record_keeper.securities
        self._security_list_model.post_reset_model()

    def _unselect_all(self) -> None:
        self._security_list_model.pre_reset_model()
        self._security_list_model.checked_items = ()
        self._security_list_model.post_reset_model()

    def _initialize_model_and_proxy(self) -> None:
        self._security_list_proxy = QSortFilterProxyModel()
        self._security_list_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._security_list_proxy.setSortCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )

        self._security_list_model = CheckableListModel(
            self._form.security_list_view,
            self._record_keeper.securities,
            self._record_keeper.securities,
            self._security_list_proxy,
        )

        self._security_list_proxy.sort(0, Qt.SortOrder.AscendingOrder)
        self._security_list_proxy.setSourceModel(self._security_list_model)

        self._form.security_list_view.setModel(self._security_list_proxy)

    def _connect_to_signals(self) -> None:
        self._form.signal_securities_select_all.connect(self._select_all)
        self._form.signal_securities_unselect_all.connect(self._unselect_all)
