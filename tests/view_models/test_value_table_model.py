from datetime import date
from decimal import Decimal

from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QTableView, QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.view_models.value_table_model import ValueTableModel, ValueType


def test_value_table_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    parent = QWidget()
    qtbot.add_widget(parent)
    list_view = QTableView(parent)
    model = ValueTableModel(
        view=list_view, proxy=QSortFilterProxyModel(), type_=ValueType.EXCHANGE_RATE
    )
    data = [(date(2022, 1, 1), Decimal("1.0")), (date(2022, 1, 2), Decimal("2.0"))]
    model.load_data(data)

    qtmodeltester.check(model)
