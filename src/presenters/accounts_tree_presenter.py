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

        self._setup_signals()
        self._view.finalize_setup()
        self._view.show()

    def _setup_signals(self) -> None:
        self._view.signal_tree_selection_changed.connect(self.selection_changed)

        self.selection_changed()  # called to ensure context menu is OK at start of run

    def selection_changed(self) -> None:
        indexes = self._view.accountsTree.selectedIndexes()

        enable_object_change = len(indexes) != 0
        enable_add_objects = True
        if len(indexes) != 0:
            item = indexes[0].internalPointer()
            if not isinstance(item, AccountGroup):
                enable_add_objects = False

        self._view.actionAdd_Account_Group.setEnabled(enable_add_objects)
        self._view.actionAdd_Security_Account.setEnabled(enable_add_objects)
        self._view.actionAdd_Cash_Account.setEnabled(enable_add_objects)
        self._view.actionEdit_Account_Object.setEnabled(enable_object_change)
        self._view.actionDelete_Account_Object.setEnabled(enable_object_change)
