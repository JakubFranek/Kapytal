from pathlib import Path

from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.utilities import constants
from src.view_models.account_tree_model import AccountTreeModel
from src.views import icons
from src.views.widgets.account_tree_widget import AccountTreeWidget
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_account_tree_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    root_path = Path(__file__).parent.parent.parent
    constants.set_app_root_path(root_path)
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    tree_view = AccountTreeWidget(parent).treeView
    record_keeper = get_preloaded_record_keeper_with_various_transactions()
    proxy = QSortFilterProxyModel(parent)
    model = AccountTreeModel(
        view=tree_view,
        proxy=proxy,
    )
    model.load_data(record_keeper.account_items, record_keeper.base_currency)

    qtmodeltester.check(model)
