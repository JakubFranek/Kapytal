import logging

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.model_objects.attributes import Attribute
from src.models.record_keeper import RecordKeeper
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.payee_filter import PayeeFilter
from src.presenters.utilities.event import Event
from src.view_models.checkable_list_model import CheckableListModel
from src.views.forms.transaction_filter_form import TransactionFilterForm


class PayeeFilterPresenter:
    event_filter_changed = Event()

    def __init__(
        self, form: TransactionFilterForm, record_keeper: RecordKeeper
    ) -> None:
        self._form = form
        self._record_keeper = record_keeper
        self._initialize_model_and_proxy()
        self._connect_to_signals()

    @property
    def checked_payees(self) -> tuple[Attribute, ...]:
        return self._payee_list_model.checked_items

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._payee_list_model.pre_reset_model()
        self._payee_list_model.items = record_keeper.payees
        self._payee_list_model.checked_items = record_keeper.payees
        self._payee_list_model.post_reset_model()

    def load_from_payee_filter(
        self,
        payee_filter: PayeeFilter,
    ) -> None:
        self._payee_list_model.pre_reset_model()
        if payee_filter.mode == FilterMode.KEEP:
            self._payee_list_model.checked_items = payee_filter.payees
        elif payee_filter.mode == FilterMode.OFF:
            self._payee_list_model.checked_items = self._record_keeper.payees
        else:
            self._payee_list_model.checked_items = [
                payee
                for payee in self._record_keeper.payees
                if payee not in payee_filter.payees
            ]
        self._payee_list_model.post_reset_model()

    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        logging.debug(f"Filtering Payees: {pattern=}")
        self._payee_list_proxy.setFilterWildcard(pattern)

    def _select_all(self) -> None:
        self._payee_list_model.pre_reset_model()
        self._payee_list_model.checked_items = self._record_keeper.payees
        self._payee_list_model.post_reset_model()

    def _unselect_all(self) -> None:
        self._payee_list_model.pre_reset_model()
        self._payee_list_model.checked_items = ()
        self._payee_list_model.post_reset_model()

    def _initialize_model_and_proxy(self) -> None:
        self._payee_list_proxy = QSortFilterProxyModel()
        self._payee_list_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._payee_list_proxy.setSortCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )
        self._payee_list_proxy.setFilterCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )

        self._payee_list_model = CheckableListModel(
            self._form.payee_list_view,
            self._record_keeper.payees,
            self._record_keeper.payees,
            self._payee_list_proxy,
        )

        self._payee_list_proxy.sort(0, Qt.SortOrder.AscendingOrder)
        self._payee_list_proxy.setSourceModel(self._payee_list_model)

        self._form.payee_list_view.setModel(self._payee_list_proxy)

    def _connect_to_signals(self) -> None:
        self._form.signal_payees_search_text_changed.connect(
            lambda pattern: self._filter(pattern)
        )
        self._form.signal_payees_select_all.connect(self._select_all)
        self._form.signal_payees_unselect_all.connect(self._unselect_all)
