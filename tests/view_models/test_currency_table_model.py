from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QTableView, QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.view_models.currency_table_model import CurrencyTableModel
from tests.models.test_record_keeper import get_preloaded_record_keeper


def test_currency_table_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    parent = QWidget()
    qtbot.add_widget(parent)
    tree_view = QTableView(parent)
    record_keeper = get_preloaded_record_keeper()
    proxy = QSortFilterProxyModel(tree_view)
    model = CurrencyTableModel(
        view=tree_view,
        proxy=proxy,
        currencies=record_keeper.currencies,
        base_currency=record_keeper.base_currency,
    )

    qtmodeltester.check(model)
