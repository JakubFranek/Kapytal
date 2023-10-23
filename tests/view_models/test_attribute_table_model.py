from pathlib import Path

from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.models.statistics.attribute_stats import calculate_attribute_stats
from src.utilities import constants
from src.view_models.attribute_table_model import AttributeTableModel
from src.views import icons
from src.views.forms.payee_form import PayeeForm
from src.views.forms.tag_form import TagForm
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_payee_table_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    root_path = Path(__file__).parent.parent.parent
    constants.set_app_root_path(root_path)
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    payee_form = PayeeForm(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    relevant_transactions = (
        record_keeper.cash_transactions + record_keeper.refund_transactions
    )
    payee_stats = calculate_attribute_stats(
        relevant_transactions,
        record_keeper.base_currency,
        record_keeper.payees,
    ).values()

    model = AttributeTableModel(
        view=payee_form.tableView,
        proxy=QSortFilterProxyModel(),
    )
    model.load_attribute_stats(payee_stats)

    qtmodeltester.check(model)


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
    model = AttributeTableModel(
        view=tag_form.tableView,
        proxy=proxy,
    )
    model.load_attribute_stats(tag_stats)
    proxy.setSourceModel(model)
    tag_form.tableView.setModel(proxy)

    qtmodeltester.check(model)
