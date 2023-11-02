from pathlib import Path

from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.utilities import constants
from src.view_models.security_table_model import SecurityTableModel
from src.views import icons
from src.views.forms.security_form import SecurityForm
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_security_table_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    root_path = Path(__file__).parent.parent.parent
    constants.set_app_root_path(root_path)
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    security_form = SecurityForm(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    model = SecurityTableModel(
        view=security_form.securityTableView,
        proxy=QSortFilterProxyModel(),
    )
    model.load_securities(record_keeper.securities)

    qtmodeltester.check(model)
