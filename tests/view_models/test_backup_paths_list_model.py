from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.view_models.backup_paths_list_model import BackupPathsListModel
from src.views.forms.settings_form import SettingsForm


def test_backup_paths_list_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    parent = QWidget()
    qtbot.add_widget(parent)
    settings_form = SettingsForm(parent)
    paths = ["a", "b", "c", "d", "e", "f"]
    model = BackupPathsListModel(view=settings_form.backupsListView, paths=paths)

    qtmodeltester.check(model)
