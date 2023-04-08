from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.model_objects.attributes import Attribute
from src.models.record_keeper import RecordKeeper
from src.models.transaction_filters.specific_tags_filter import SpecificTagsFilter
from src.presenters.utilities.event import Event
from src.view_models.checkable_list_model import CheckableListModel
from src.views.forms.transaction_filter_form import TransactionFilterForm

# TODO: select/unselect all
# TODO: split tags filter
# TODO: keep tagless filter
# TODO: search in list


class TagFilterPresenter:
    event_filter_changed = Event()

    def __init__(
        self, form: TransactionFilterForm, record_keeper: RecordKeeper
    ) -> None:
        self._form = form
        self._record_keeper = record_keeper

        self._tags_list_proxy = QSortFilterProxyModel()
        self._tags_list_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._tags_list_proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._tags_list_model = CheckableListModel(
            self._form.tags_list_view,
            record_keeper.tags,
            record_keeper.tags,
            self._tags_list_proxy,
        )
        self._tags_list_proxy.sort(0, Qt.SortOrder.AscendingOrder)
        self._tags_list_proxy.setSourceModel(self._tags_list_model)
        self._form.tags_list_view.setModel(self._tags_list_proxy)

    @property
    def checked_tags(self) -> tuple[Attribute, ...]:
        return self._tags_list_model.checked_items

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._tags_list_model.pre_reset_model()
        self._tags_list_model.items = record_keeper.tags
        self._tags_list_model.checked_items = record_keeper.tags
        self._tags_list_model.post_reset_model()

    def load_from_tag_filter(self, tag_filter: SpecificTagsFilter) -> None:
        self._tags_list_model.pre_reset_model()
        self._tags_list_model.checked_items = tag_filter.tags
        self._tags_list_model.post_reset_model()
