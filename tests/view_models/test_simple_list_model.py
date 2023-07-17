from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QListView, QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.view_models.simple_list_model import SimpleListModel


def test_simple_list_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    parent = QWidget()
    qtbot.add_widget(parent)
    list_view = QListView(parent)
    items = ["a", "b", "c", "d", "e", "f"]
    model = SimpleListModel(view=list_view, proxy=QSortFilterProxyModel())
    model.load_items(items)

    qtmodeltester.check(model)
