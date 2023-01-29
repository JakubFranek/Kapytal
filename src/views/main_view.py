import os

from PyQt6.QtCore import QDir, pyqtSignal
from PyQt6.QtGui import QContextMenuEvent, QCursor, QIcon
from PyQt6.QtWidgets import QHeaderView, QMainWindow, QMenu, QMessageBox

from src.views.constants import AccountTreeColumns
from src.views.ui_files.Ui_mainwindow import Ui_MainWindow


class MainView(QMainWindow, Ui_MainWindow):
    signal_tree_selection_changed = pyqtSignal()
    signal_tree_context_menu = pyqtSignal()
    signal_tree_expand_below = pyqtSignal()
    signal_tree_delete_item = pyqtSignal()
    signal_tree_add_account_group = pyqtSignal()
    signal_tree_add_security_account = pyqtSignal()
    signal_tree_edit_item = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.initial_setup()
        self.accountTree.contextMenuEvent = self.account_tree_context_menu

    def enable_accounts_tree_actions(
        self,
        enable_add_objects: bool,
        enable_modify_object: bool,
        enable_expand_below: bool,
    ) -> None:
        self.actionAdd_Account_Group.setEnabled(enable_add_objects)
        self.actionAdd_Security_Account.setEnabled(enable_add_objects)
        self.actionAdd_Cash_Account.setEnabled(enable_add_objects)
        self.actionEdit_Account_Tree_Item.setEnabled(enable_modify_object)
        self.actionDelete_Account_Tree_Item.setEnabled(enable_modify_object)
        self.actionExpand_All_Below.setEnabled(enable_expand_below)

    def account_tree_context_menu(self, event: QContextMenuEvent) -> None:  # noqa: U100
        self.menu = QMenu(self)
        self.menu.addAction(self.actionAdd_Account_Group)
        self.menu.addAction(self.actionAdd_Cash_Account)
        self.menu.addAction(self.actionAdd_Security_Account)
        self.menu.addSeparator()
        self.menu.addAction(self.actionEdit_Account_Tree_Item)
        self.menu.addAction(self.actionDelete_Account_Tree_Item)
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
        self.actionEdit_Account_Tree_Item.setIcon(QIcon("icons_16:pencil.png"))
        self.actionDelete_Account_Tree_Item.setIcon(QIcon("icons_16:minus.png"))

        self.actionExpand_All.triggered.connect(self.accountTree.expandAll)
        self.actionExpand_All_Below.triggered.connect(
            self.signal_tree_expand_below.emit
        )
        self.actionCollapse_All.triggered.connect(self.accountTree.collapseAll)
        self.actionDelete_Account_Tree_Item.triggered.connect(
            self.signal_tree_delete_item.emit
        )
        self.actionAdd_Account_Group.triggered.connect(
            self.signal_tree_add_account_group.emit
        )
        self.actionAdd_Security_Account.triggered.connect(
            self.signal_tree_add_security_account.emit
        )
        self.actionEdit_Account_Tree_Item.triggered.connect(self.signal_tree_edit_item)

        self.toolButton_expandAll.setDefaultAction(self.actionExpand_All)
        self.toolButton_collapseAll.setDefaultAction(self.actionCollapse_All)

    def finalize_setup(self) -> None:
        self.accountTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.accountTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_BALANCE_NATIVE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.accountTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_BALANCE_BASE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.accountTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_SHOW,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self.accountTree.selectionModel().selectionChanged.connect(
            self.signal_tree_selection_changed.emit
        )

    def display_error(
        self,
        text: str,
        exc_details: str,
        critical: bool = False,
        title: str = "Error!",
    ) -> None:
        message_box = QMessageBox()
        if critical is True:
            message_box.setIcon(QMessageBox.Icon.Critical)
            message_box.setWindowIcon(QIcon("icons_24:cross.png"))
        else:
            message_box.setIcon(QMessageBox.Icon.Warning)
            message_box.setWindowIcon(QIcon("icons_24:exclamation.png"))
        message_box.setWindowTitle(title)
        message_box.setText(text)
        message_box.setDetailedText(exc_details)
        message_box.exec()
