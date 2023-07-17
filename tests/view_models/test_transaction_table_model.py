from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.presenters.widget.transactions_presenter import (
    TransactionsPresenter,
)
from src.view_models.transaction_table_model import TransactionTableModel
from src.views import icons
from src.views.widgets.transaction_table_widget import TransactionTableWidget
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_transaction_table_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    view = TransactionTableWidget(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    presenter = TransactionsPresenter(view=view, record_keeper=record_keeper)

    model = TransactionTableModel(
        view=view.tableView,
        proxy_viewside=presenter._proxy_regex_sort_filter,
        proxy_sourceside=presenter._proxy_transaction_filter,
    )

    qtmodeltester.check(model)
