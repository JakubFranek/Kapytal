from pathlib import Path

from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QTreeView, QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.models.statistics.security_stats import SecurityStatsData
from src.utilities import constants
from src.view_models.securities_overview_tree_model import SecuritiesOverviewTreeModel
from src.views import icons
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_owned_securities_tree_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    root_path = Path(__file__).parent.parent.parent
    constants.set_app_root_path(root_path)
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    view = QTreeView(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    proxy = QSortFilterProxyModel(parent)
    model = SecuritiesOverviewTreeModel(
        tree_view=view,
        proxy=proxy,
    )
    model.load_data(
        SecurityStatsData(
            record_keeper.securities,
            record_keeper.security_accounts,
            record_keeper.base_currency,
        )
    )
    proxy.setSourceModel(model)
    view.setModel(proxy)

    qtmodeltester.check(model)
