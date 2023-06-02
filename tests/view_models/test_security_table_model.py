from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.presenters.form.security_form_presenter import SecurityFormPresenter
from src.view_models.security_table_model import SecurityTableModel
from src.views import icons
from src.views.forms.security_form import SecurityForm
from tests.models.test_record_keeper import get_preloaded_record_keeper


def test_security_table_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    security_form = SecurityForm(parent)
    record_keeper = get_preloaded_record_keeper()

    security_form_presenter = SecurityFormPresenter(security_form, record_keeper)

    model = SecurityTableModel(
        view=security_form.securityTableView,
        securities=security_form_presenter._security_table_model.securities,
        proxy=security_form_presenter._security_table_proxy,
    )

    qtmodeltester.check(model)
