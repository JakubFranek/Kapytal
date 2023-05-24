from PyQt6.QtWidgets import QTableView, QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.view_models.exchange_rate_table_model import ExchangeRateTableModel
from tests.models.test_record_keeper import get_preloaded_record_keeper


def test_exchange_rate_table_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    parent = QWidget()
    qtbot.add_widget(parent)
    tree_view = QTableView(parent)
    record_keeper = get_preloaded_record_keeper()
    model = ExchangeRateTableModel(
        view=tree_view, exchange_rates=record_keeper.exchange_rates
    )

    qtmodeltester.check(model)