from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QTreeView, QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.view_models.checkable_account_tree_model import CheckableAccountTreeModel
from src.views import icons
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_checkable_account_tree_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    view = QTreeView(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    proxy = QSortFilterProxyModel(parent)
    model = CheckableAccountTreeModel(
        tree_view=view, proxy=proxy, flat_account_items=record_keeper.account_items
    )
    model.checked_accounts = record_keeper.accounts[:1]
    proxy.setSourceModel(model)
    view.setModel(proxy)

    qtmodeltester.check(model)
