from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.models.utilities.calculation import calculate_payee_stats
from src.view_models.payee_table_model import PayeeTableModel
from src.views import icons
from src.views.forms.payee_form import PayeeForm
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_payee_table_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    payee_form = PayeeForm(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    relevant_transactions = (
        record_keeper.cash_transactions + record_keeper.refund_transactions
    )
    payee_stats = calculate_payee_stats(
        relevant_transactions,
        record_keeper.base_currency,
        record_keeper.payees,
    ).values()

    model = PayeeTableModel(
        view=payee_form.tableView,
        proxy=QSortFilterProxyModel(),
    )
    model.load_payee_stats(payee_stats)

    qtmodeltester.check(model)
