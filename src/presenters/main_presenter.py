import logging

from src.models.record_keeper import RecordKeeper
from src.presenters.account_tree_presenter import AccountTreePresenter
from src.presenters.currency_form_presenter import CurrencyFormPresenter
from src.views.main_view import MainView


class MainPresenter:
    def __init__(self, view: MainView, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        logging.info("Creating AccountTreePresenter")
        self._account_tree_presenter = AccountTreePresenter(
            view.account_tree, record_keeper
        )
        logging.info("Creating CurrencyFormPresenter")
        self._currency_form_presenter = CurrencyFormPresenter(view, record_keeper)

        self._view.signal_open_currency_form.connect(
            self._currency_form_presenter.show_form
        )

        logging.info("Showing MainView")
        self._view.show()
