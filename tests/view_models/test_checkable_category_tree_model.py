from pathlib import Path

from PyQt6.QtWidgets import QTreeView, QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.utilities import constants
from src.view_models.checkable_category_tree_model import CheckableCategoryTreeModel
from src.views import icons
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_checkable_category_tree_model(
    qtbot: QtBot, qtmodeltester: ModelTester
) -> None:
    root_path = Path(__file__).parent.parent.parent
    constants.set_app_root_path(root_path)
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    view = QTreeView(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    model = CheckableCategoryTreeModel(tree_view=view)
    model.load_flat_categories(record_keeper.categories)
    model.load_checked_categories(record_keeper.categories[:1])
    view.setModel(model)

    qtmodeltester.check(model)
