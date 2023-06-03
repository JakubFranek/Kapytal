from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QTreeView, QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.view_models.owned_securities_tree_model import OwnedSecuritiesTreeModel
from src.views import icons
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_owned_securities_tree_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    view = QTreeView(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    proxy = QSortFilterProxyModel(parent)
    model = OwnedSecuritiesTreeModel(
        tree_view=view,
        security_accounts=record_keeper.security_accounts,
        base_currency=record_keeper.base_currency,
        proxy=proxy,
    )
    proxy.setSourceModel(model)
    view.setModel(proxy)

    qtmodeltester.check(model)
