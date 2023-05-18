from PyQt6.QtWidgets import QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.presenters.form.category_form_presenter import CategoryFormPresenter
from src.view_models.category_tree_model import CategoryTreeModel
from src.views import icons
from src.views.forms.category_form import CategoryForm
from tests.models.test_record_keeper import get_preloaded_record_keeper


def test_category_tree_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    category_form = CategoryForm(parent)
    record_keeper = get_preloaded_record_keeper()

    category_form_presenter = CategoryFormPresenter(
        view=category_form, record_keeper=record_keeper
    )

    model = CategoryTreeModel(
        tree_view=category_form.category_tree,
        root_categories=record_keeper.root_expense_categories,
        category_stats=category_form_presenter._model._category_stats_dict,
        base_currency=record_keeper.base_currency,
        proxy=category_form_presenter._proxy_model,
    )

    qtmodeltester.check(model)
