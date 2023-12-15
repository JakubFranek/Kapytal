from pathlib import Path

from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QTreeView, QWidget
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot
from src.presenters.form.security_form_presenter import SecurityFormPresenter
from src.utilities import constants
from src.view_models.owned_securities_tree_model import OwnedSecuritiesTreeModel
from src.views import icons
from src.views.forms.security_form import SecurityForm
from tests.models.test_record_keeper import (
    get_preloaded_record_keeper_with_various_transactions,
)


def test_owned_securities_tree_model(qtbot: QtBot, qtmodeltester: ModelTester) -> None:
    root_path = Path(__file__).parent.parent.parent
    constants.set_app_root_path(root_path)
    icons.setup()

    parent = QWidget()
    qtbot.add_widget(parent)
    view = QTreeView(parent)
    form = SecurityForm(parent)
    record_keeper = get_preloaded_record_keeper_with_various_transactions()

    presenter = SecurityFormPresenter(view=form, record_keeper=record_keeper)
    irrs = presenter._calculate_irrs()

    proxy = QSortFilterProxyModel(parent)
    model = OwnedSecuritiesTreeModel(
        tree_view=view,
        proxy=proxy,
    )
    model.load_data(record_keeper.security_accounts, irrs, record_keeper.base_currency)
    proxy.setSourceModel(model)
    view.setModel(proxy)

    qtmodeltester.check(model)
