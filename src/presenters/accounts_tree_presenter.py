from src.models.record_keeper import RecordKeeper
from src.presenters.view_models.accounts_tree_model import AccountsTreeModel
from src.views.main_view import MainView


class AccountsTreePresenter:
    def __init__(self, view: MainView, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper
        self._accounts_tree_model = AccountsTreeModel(
            view=view.accountsTree, data=record_keeper.account_objects
        )
        self._view.accountsTree.setModel(self._accounts_tree_model)
