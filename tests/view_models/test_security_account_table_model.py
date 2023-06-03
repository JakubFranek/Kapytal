from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QTableView, QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.view_models.security_account_table_model import SecurityAccountTableModel
from src.views import icons
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_security_account_table_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    view = QTableView(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    proxy = QSortFilterProxyModel(parent)
    model = SecurityAccountTableModel(
        view=view,
        security_account=record_keeper.security_accounts[0],
        base_currency=record_keeper.base_currency,
        proxy=proxy,
    )
    proxy.setSourceModel(model)
    view.setModel(proxy)

    qtmodeltester.check(model)
