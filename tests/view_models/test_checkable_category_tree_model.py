from PyQt6.QtWidgets import QTreeView, QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.view_models.checkable_category_tree_model import CheckableCategoryTreeModel
from src.views import icons
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_checkable_category_tree_model(
    qtbot: QtBot, qtmodeltester: ModelTester
) -> None:
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    view = QTreeView(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    model = CheckableCategoryTreeModel(
        tree_view=view, flat_categories=record_keeper.categories
    )
    model.checked_categories = record_keeper.categories[:1]
    view.setModel(model)

    qtmodeltester.check(model)
