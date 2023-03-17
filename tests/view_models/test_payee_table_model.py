from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.presenters.payee_form_presenter import PayeeFormPresenter
from src.view_models.payee_table_model import PayeeTableModel
from src.views.forms.payee_form import PayeeForm
from tests.models.test_record_keeper import get_preloaded_record_keeper


def test_payee_table_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    parent = QWidget()
    qtbot.add_widget(parent)
    payee_form = PayeeForm(parent)
    record_keeper = get_preloaded_record_keeper()

    payee_form_presenter = PayeeFormPresenter(
        view=payee_form, record_keeper=record_keeper
    )

    model = PayeeTableModel(
        view=payee_form.tableView,
        payee_stats=payee_form_presenter._model.payee_stats,
        proxy=payee_form_presenter._proxy_model,
    )

    qtmodeltester.check(model)
