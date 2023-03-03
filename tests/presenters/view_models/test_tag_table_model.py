from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot

from src.presenters.tag_form_presenter import TagFormPresenter
from src.view_models.tag_table_model import TagTableModel
from src.views.forms.tag_form import TagForm
from tests.models.test_record_keeper import get_preloaded_record_keeper


def test_tag_table_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    parent = QWidget()
    qtbot.add_widget(parent)
    tag_form = TagForm(parent)
    record_keeper = get_preloaded_record_keeper()

    payee_form_presenter = TagFormPresenter(view=tag_form, record_keeper=record_keeper)

    model = TagTableModel(
        view=tag_form.tableView,
        tag_stats=payee_form_presenter._model.tag_stats,
        proxy=payee_form_presenter._proxy_model,
    )

    qtmodeltester.check(model)
