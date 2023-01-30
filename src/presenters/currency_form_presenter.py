from PyQt6.QtWidgets import QWidget

from src.models.record_keeper import RecordKeeper
from src.views.currency_form import CurrencyForm


class CurrencyFormPresenter:
    def __init__(self, parent_view: QWidget, record_keeper: RecordKeeper) -> None:
        self._view = CurrencyForm(parent=parent_view)
        self._record_keeper = record_keeper

    def show_form(self) -> None:
        self._view.show_form()
