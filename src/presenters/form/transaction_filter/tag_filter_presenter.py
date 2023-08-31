from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.model_objects.attributes import Attribute
from src.models.record_keeper import RecordKeeper
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.specific_tags_filter import SpecificTagsFilter
from src.models.transaction_filters.split_tags_filter import SplitTagsFilter
from src.models.transaction_filters.tagless_filter import TaglessFilter
from src.presenters.utilities.event import Event
from src.view_models.checkable_list_model import CheckableListModel
from src.views.forms.transaction_filter_form import TransactionFilterForm


class TagFilterPresenter:
    event_filter_changed = Event()

    def __init__(
        self, form: TransactionFilterForm, record_keeper: RecordKeeper
    ) -> None:
        self._form = form
        self._record_keeper = record_keeper
        self._initialize_model_and_proxy()
        self._connect_to_signals()

    @property
    def tagless_filter_mode(self) -> FilterMode:
        return self._form.tagless_filter_mode

    @property
    def specific_tag_filter_mode(self) -> FilterMode:
        return self._form.specific_tags_filter_mode

    @property
    def checked_tags(self) -> tuple[Attribute, ...]:
        return self._model.checked_items

    @property
    def split_tags_filter_mode(self) -> FilterMode:
        return self._form.split_tags_filter_mode

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._model.pre_reset_model()
        self._model.load_items(record_keeper.tags)
        self._model.load_checked_items(record_keeper.tags)
        self._model.post_reset_model()

    def load_from_tag_filters(
        self,
        specific_tag_filter: SpecificTagsFilter,
        tagless_filter: TaglessFilter,
        split_tags_filter: SplitTagsFilter,
    ) -> None:
        if specific_tag_filter.mode != FilterMode.OFF:
            self._model.pre_reset_model()
            self._model.load_checked_items(specific_tag_filter.tags)
            self._model.post_reset_model()

        self._form.specific_tags_filter_mode = specific_tag_filter.mode
        self._form.tagless_filter_mode = tagless_filter.mode
        self._form.split_tags_filter_mode = split_tags_filter.mode

    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        self._proxy.setFilterWildcard(pattern)

    def _set_all_checks(self, *, checked: bool) -> None:
        checks = self._record_keeper.tags if checked else ()
        self._model.pre_reset_model()
        self._model.load_checked_items(checks)
        self._model.post_reset_model()

    def _initialize_model_and_proxy(self) -> None:
        self._proxy = QSortFilterProxyModel()
        self._proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self._model = CheckableListModel(
            self._form.tags_list_view,
            self._proxy,
        )
        self._model.event_checked_items_changed.append(self._update_checked_tags_number)

        self._proxy.sort(0, Qt.SortOrder.AscendingOrder)
        self._proxy.setSourceModel(self._model)

        self._form.tags_list_view.setModel(self._proxy)
        self._update_checked_tags_number()

    def _connect_to_signals(self) -> None:
        self._form.signal_tags_search_text_changed.connect(self._filter)
        self._form.signal_tags_select_all.connect(
            lambda: self._set_all_checks(checked=True)
        )
        self._form.signal_tags_unselect_all.connect(
            lambda: self._set_all_checks(checked=False)
        )

    def _update_checked_tags_number(self) -> None:
        selected = len(self._model.checked_items)
        total = len(self._record_keeper.tags)
        self._form.set_selected_tags_numbers(selected, total)
