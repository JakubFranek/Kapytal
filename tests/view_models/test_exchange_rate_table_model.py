from pathlib import Path

from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QTableView, QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.presenters.form.currency_form_presenter import CurrencyFormPresenter
from src.utilities import constants
from src.view_models.exchange_rate_table_model import ExchangeRateTableModel
from src.views import icons
from src.views.forms.currency_form import CurrencyForm
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_exchange_rate_table_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    root_path = Path(__file__).parent.parent.parent
    constants.set_app_root_path(root_path)
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    form = CurrencyForm(parent)
    tree_view = QTableView(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    presenter = CurrencyFormPresenter(view=form, record_keeper=record_keeper)
    stats = presenter._calculate_exchange_rate_stats(record_keeper.exchange_rates)

    proxy = QSortFilterProxyModel(tree_view)
    model = ExchangeRateTableModel(view=tree_view, proxy=proxy)
    model.load_data(record_keeper.exchange_rates, stats)

    qtmodeltester.check(model)
