import logging

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
    def checked_tags(self) -> tuple[Attribute, ...]:
        return self._tags_list_model.checked_items

    @property
    def tagless_filter_mode(self) -> FilterMode:
        return self._form.tagless_filter_mode

    @property
    def split_tags_filter_mode(self) -> FilterMode:
        return self._form.split_tags_filter_mode

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._tags_list_model.pre_reset_model()
        self._tags_list_model.items = record_keeper.tags
        self._tags_list_model.checked_items = record_keeper.tags
        self._tags_list_model.post_reset_model()

    def load_from_tag_filters(
        self,
        specific_tag_filter: SpecificTagsFilter,
        tagless_filter: TaglessFilter,
        split_tags_filter: SplitTagsFilter,
    ) -> None:
        self._tags_list_model.pre_reset_model()
        if specific_tag_filter.mode == FilterMode.KEEP:
            self._tags_list_model.checked_items = specific_tag_filter.tags
        elif specific_tag_filter.mode == FilterMode.OFF:
            self._tags_list_model.checked_items = self._record_keeper.tags
        else:
            self._tags_list_model.checked_items = [
                tag
                for tag in self._record_keeper.tags
                if tag not in specific_tag_filter.tags
            ]
        self._tags_list_model.post_reset_model()

        self._form.tagless_filter_mode = tagless_filter.mode
        self._form.split_tags_filter_mode = split_tags_filter.mode

    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        logging.debug(f"Filtering Tags: {pattern=}")
        self._tags_list_proxy.setFilterWildcard(pattern)

    def _select_all(self) -> None:
        self._tags_list_model.pre_reset_model()
        self._tags_list_model.checked_items = self._record_keeper.tags
        self._tags_list_model.post_reset_model()

    def _unselect_all(self) -> None:
        self._tags_list_model.pre_reset_model()
        self._tags_list_model.checked_items = ()
        self._tags_list_model.post_reset_model()

    def _initialize_model_and_proxy(self) -> None:
        self._tags_list_proxy = QSortFilterProxyModel()
        self._tags_list_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._tags_list_proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._tags_list_proxy.setFilterCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )

        self._tags_list_model = CheckableListModel(
            self._form.tags_list_view,
            self._record_keeper.tags,
            self._record_keeper.tags,
            self._tags_list_proxy,
        )

        self._tags_list_proxy.sort(0, Qt.SortOrder.AscendingOrder)
        self._tags_list_proxy.setSourceModel(self._tags_list_model)

        self._form.tags_list_view.setModel(self._tags_list_proxy)

    def _connect_to_signals(self) -> None:
        self._form.signal_tags_search_text_changed.connect(
            lambda pattern: self._filter(pattern)
        )
        self._form.signal_tags_select_all.connect(self._select_all)
        self._form.signal_tags_unselect_all.connect(self._unselect_all)
