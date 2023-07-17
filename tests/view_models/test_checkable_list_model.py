from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QListView, QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.view_models.checkable_list_model import CheckableListModel


def test_checkable_list_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    parent = QWidget()
    qtbot.add_widget(parent)
    list_view = QListView(parent)
    items = ["a", "b", "c", "d", "e", "f"]
    model = CheckableListModel(
        view=list_view,
        proxy=QSortFilterProxyModel(),
    )
    model.load_items(items)
    model.load_checked_items(items[1:4])

    qtmodeltester.check(model)
