from pathlib import Path

from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QTreeView, QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.utilities import constants
from src.view_models.checkable_account_tree_model import CheckableAccountTreeModel
from src.views import icons
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_checkable_account_tree_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    root_path = Path(__file__).parent.parent.parent
    constants.set_app_root_path(root_path)
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    view = QTreeView(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    proxy = QSortFilterProxyModel(parent)
    model = CheckableAccountTreeModel(
        tree_view=view,
        proxy=proxy,
    )
    model.load_flat_items(record_keeper.account_items)
    model.load_checked_accounts(record_keeper.accounts[:1])
    proxy.setSourceModel(model)
    view.setModel(proxy)

    qtmodeltester.check(model)
