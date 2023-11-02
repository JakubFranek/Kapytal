from pathlib import Path

from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.utilities import constants
from src.view_models.backup_paths_list_model import BackupPathsListModel
from src.views import icons
from src.views.forms.settings_form import SettingsForm


def test_backup_paths_list_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    root_path = Path(__file__).parent.parent.parent
    constants.set_app_root_path(root_path)
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    settings_form = SettingsForm(parent)
    paths = ["a", "b", "c", "d", "e", "f"]
    model = BackupPathsListModel(view=settings_form.backupsListView)
    model.load_paths(paths)

    qtmodeltester.check(model)
