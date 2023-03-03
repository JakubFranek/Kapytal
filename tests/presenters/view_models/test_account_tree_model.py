from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot

from src.view_models.account_tree_model import AccountTreeModel
from src.views.widgets.account_tree_widget import AccountTreeWidget
from tests.models.test_record_keeper import get_preloaded_record_keeper


def test_account_tree_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    parent = QWidget()
    qtbot.add_widget(parent)
    tree_view = AccountTreeWidget(parent).treeView
    record_keeper = get_preloaded_record_keeper()
    model = AccountTreeModel(
        view=tree_view,
        root_items=record_keeper.root_account_items,
        base_currency=record_keeper.base_currency,
    )

    qtmodeltester.check(model)
