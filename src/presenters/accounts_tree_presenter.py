from src.models.model_objects.account_group import AccountGroup
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

        self._view.finalize_setup()
        self._view.show()

    def _setup_signals(self) -> None:
        self._view.signal_tree_selection_changed.connect(self.selection_changed)

    def selection_changed(self) -> None:
        indexes = self._view.accountsTree.selectedIndexes()
        
        item = indexes[0].internalPointer()
        if isinstance(item,AccountGroup):
            
