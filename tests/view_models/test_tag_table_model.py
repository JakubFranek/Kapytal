from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.models.statistics.attribute_stats import calculate_attribute_stats
from src.view_models.tag_table_model import TagTableModel
from src.views import icons
from src.views.forms.tag_form import TagForm
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_tag_table_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    tag_form = TagForm(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()
    relevant_transactions = (
        record_keeper.cash_transactions + record_keeper.refund_transactions
    )
    tag_stats = calculate_attribute_stats(
        relevant_transactions,
        record_keeper.base_currency,
        record_keeper.tags,
    ).values()

    proxy = QSortFilterProxyModel(parent)
    model = TagTableModel(
        view=tag_form.tableView,
        proxy=proxy,
    )
    model.load_tag_stats(tag_stats)
    proxy.setSourceModel(model)
    tag_form.tableView.setModel(proxy)

    qtmodeltester.check(model)
