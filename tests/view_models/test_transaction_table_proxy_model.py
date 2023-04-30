from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.models.transaction_filters.transaction_filter import TransactionFilter
from src.view_models.proxy_models.transaction_table_proxy_model import (
    TransactionTableProxyModel,
)
from src.views import icons
from src.views.widgets.transaction_table_widget import TransactionTableWidget


def test_transaction_table_proxy_model(
    qtbot: QtBot, qtmodeltester: ModelTester
) -> None:
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    view = TransactionTableWidget(parent)

    filter_ = TransactionFilter()
    model = TransactionTableProxyModel(parent=view, transaction_filter=filter_)

    qtmodeltester.check(model)
