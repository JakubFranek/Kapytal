from pathlib import Path

from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.presenters.form.category_form_presenter import CategoryFormPresenter
from src.presenters.form.transaction_table_form_presenter import (
    TransactionTableFormPresenter,
)
from src.utilities import constants
from src.views import icons
from src.views.forms.category_form import CategoryForm
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_category_tree_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    root_path = Path(__file__).parent.parent.parent
    constants.set_app_root_path(root_path)
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    category_form = CategoryForm(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    transaction_table_form_presenter = TransactionTableFormPresenter(
        record_keeper=record_keeper
    )
    category_form_presenter = CategoryFormPresenter(
        view=category_form,
        record_keeper=record_keeper,
        transaction_table_form_presenter=transaction_table_form_presenter,
    )

    qtmodeltester.check(category_form_presenter._model_expense)
