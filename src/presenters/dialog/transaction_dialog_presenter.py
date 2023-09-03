from PyQt6.QtWidgets import QWidget
from src.models.record_keeper import RecordKeeper
from src.presenters.utilities.event import Event


class TransactionDialogPresenter:
    """Base class for Transaction dialogs. Not meant to be instantiated."""

    def __init__(
        self,
        parent_view: QWidget,
        record_keeper: RecordKeeper,
    ) -> None:
        self._parent_view = parent_view
        self._record_keeper = record_keeper
        self.event_update_model = Event()
        self.event_data_changed = Event()
        self.event_pre_add = Event()
        self.event_post_add = Event()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
