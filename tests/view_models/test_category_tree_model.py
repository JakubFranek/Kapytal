from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.presenters.form.category_form_presenter import CategoryFormPresenter
from src.views import icons
from src.views.forms.category_form import CategoryForm
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_category_tree_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    category_form = CategoryForm(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    category_form_presenter = CategoryFormPresenter(
        view=category_form, record_keeper=record_keeper
    )

    qtmodeltester.check(category_form_presenter._model_expense)
