from pathlib import Path

from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QTableView, QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.utilities import constants
from src.view_models.security_account_table_model import SecurityAccountTableModel
from src.views import icons
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_security_account_table_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    root_path = Path(__file__).parent.parent.parent
    constants.set_app_root_path(root_path)
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    view = QTableView(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    proxy = QSortFilterProxyModel(parent)
    model = SecurityAccountTableModel(
        view=view,
        proxy=proxy,
    )
    model.load_data(record_keeper.security_accounts[0], record_keeper.base_currency)
    proxy.setSourceModel(model)
    view.setModel(proxy)

    qtmodeltester.check(model)
