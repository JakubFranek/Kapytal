import os

from PyQt6.QtCore import QDir, pyqtSignal
from PyQt6.QtGui import QContextMenuEvent, QCursor, QIcon
from PyQt6.QtWidgets import QHeaderView, QMainWindow, QMenu

from src.views.constants import AccountTreeColumns
from src.views.ui_files.Ui_mainwindow import Ui_MainWindow

# TODO: set up error display


class MainView(QMainWindow, Ui_MainWindow):
    signal_tree_selection_changed = pyqtSignal()
    signal_tree_context_menu = pyqtSignal()
    signal_tree_expand_all_below = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.initial_setup()
        self.accountsTree.contextMenuEvent = self.accounts_tree_context_menu

    def accounts_tree_context_menu(
        self, event: QContextMenuEvent  # noqa: U100
    ) -> None:
        self.menu = QMenu(self)
        self.menu.addAction(self.actionAdd_Account_Group)
        self.menu.addAction(self.actionAdd_Cash_Account)
        self.menu.addAction(self.actionAdd_Security_Account)
        self.menu.addSeparator()
        self.menu.addAction(self.actionEdit_Account_Object)
        self.menu.addAction(self.actionDelete_Account_Object)
        self.menu.addSeparator()
        self.menu.addAction(self.actionExpand_All_Below)
        self.menu.popup(QCursor.pos())

    def initial_setup(self) -> None:
        QDir.addSearchPath(
            "icons_24",
            os.path.join(QDir.currentPath(), "resources/icons/icons-24"),
        )
        QDir.addSearchPath(
            "icons_16",
            os.path.join(QDir.currentPath(), "resources/icons/icons-16"),
        )
        QDir.addSearchPath(
            "icons_custom",
            os.path.join(QDir.currentPath(), "resources/icons/icons-custom"),
        )

        self.setupUi(self)

        self.actionExpand_All.setIcon(QIcon("icons_custom:arrow-out.png"))
        self.actionExpand_All_Below.setIcon(QIcon("icons_16:arrow-stop-270.png"))
        self.actionCollapse_All.setIcon(QIcon("icons_16:arrow-in.png"))
        self.actionAdd_Account_Group.setIcon(QIcon("icons_16:folder--plus.png"))
        self.actionAdd_Security_Account.setIcon(QIcon("icons_custom:bank-plus.png"))
        self.actionAdd_Cash_Account.setIcon(QIcon("icons_custom:money-coin-plus.png"))
        self.actionEdit_Account_Object.setIcon(QIcon("icons_16:pencil.png"))
        self.actionDelete_Account_Object.setIcon(QIcon("icons_16:minus.png"))

        self.actionExpand_All.triggered.connect(self.accountsTree.expandAll)
        self.actionExpand_All_Below.triggered.connect(
            self.signal_tree_expand_all_below.emit
        )
        self.actionCollapse_All.triggered.connect(self.accountsTree.collapseAll)

        self.toolButton_expandAll.setDefaultAction(self.actionExpand_All)
        self.toolButton_collapseAll.setDefaultAction(self.actionCollapse_All)

    def finalize_setup(self) -> None:
        self.accountsTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.accountsTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_BALANCE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.accountsTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_BALANCE_BASE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.accountsTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_SHOW,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self.accountsTree.selectionModel().selectionChanged.connect(
            self.signal_tree_selection_changed.emit
        )
