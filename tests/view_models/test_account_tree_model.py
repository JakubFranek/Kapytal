from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.view_models.account_tree_model import AccountTreeModel
from src.views import icons
from src.views.widgets.account_tree_widget import AccountTreeWidget
from tests.models.test_record_keeper import get_preloaded_record_keeper

# TODO: add view model tests


def test_account_tree_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    tree_view = AccountTreeWidget(parent).treeView
    record_keeper = get_preloaded_record_keeper()
    proxy = QSortFilterProxyModel(parent)
    model = AccountTreeModel(
        view=tree_view,
        proxy=proxy,
    )
    model.load_data(record_keeper.account_items, record_keeper.base_currency)

    qtmodeltester.check(model)
