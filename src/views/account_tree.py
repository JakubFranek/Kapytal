from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QContextMenuEvent, QCursor, QIcon
from PyQt6.QtWidgets import QHeaderView, QMenu, QTreeView, QWidget

from src.views.constants import AccountTreeColumns


class AccountTree(QTreeView):
    signal_selection_changed = pyqtSignal()
    signal_context_menu = pyqtSignal()
    signal_expand_below = pyqtSignal()
    signal_delete_item = pyqtSignal()
    signal_add_account_group = pyqtSignal()
    signal_add_security_account = pyqtSignal()
    signal_edit_item = pyqtSignal()

    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )
        self.setObjectName("accountTree")
        self.header().setHighlightSections(True)
        self.header().setMinimumSectionSize(35)
        self.header().setSortIndicatorShown(False)
        self.header().setStretchLastSection(False)

        self.actionAdd_Account_Group = QtGui.QAction(self)
        self.actionAdd_Account_Group.setText("Add Account Group")
        self.actionAdd_Security_Account = QtGui.QAction(self)
        self.actionAdd_Security_Account.setText("Add Security Account")
        self.actionAdd_Cash_Account = QtGui.QAction(self)
        self.actionAdd_Cash_Account.setText("Add Cash Account")
        self.actionEdit_Account_Tree_Item = QtGui.QAction(self)
        self.actionEdit_Account_Tree_Item.setText("Edit")
        self.actionDelete_Account_Tree_Item = QtGui.QAction(self)
        self.actionDelete_Account_Tree_Item.setText("Delete")
        self.actionExpand_All = QtGui.QAction(self)
        self.actionExpand_All.setText("Expand All")
        self.actionExpand_All_Below = QtGui.QAction(self)
        self.actionExpand_All_Below.setText("Expand All Below")
        self.actionCollapse_All = QtGui.QAction(self)
        self.actionCollapse_All.setText("Collapse All")

        self.actionExpand_All.setIcon(QIcon("icons_custom:arrow-out.png"))
        self.actionExpand_All_Below.setIcon(QIcon("icons_16:arrow-stop-270.png"))
        self.actionCollapse_All.setIcon(QIcon("icons_16:arrow-in.png"))
        self.actionAdd_Account_Group.setIcon(QIcon("icons_16:folder--plus.png"))
        self.actionAdd_Security_Account.setIcon(QIcon("icons_custom:bank-plus.png"))
        self.actionAdd_Cash_Account.setIcon(QIcon("icons_custom:money-coin-plus.png"))
        self.actionEdit_Account_Tree_Item.setIcon(QIcon("icons_16:pencil.png"))
        self.actionDelete_Account_Tree_Item.setIcon(QIcon("icons_16:minus.png"))

        self.actionExpand_All.triggered.connect(self.expandAll)
        self.actionExpand_All_Below.triggered.connect(self.signal_expand_below.emit)
        self.actionCollapse_All.triggered.connect(self.collapseAll)
        self.actionDelete_Account_Tree_Item.triggered.connect(
            self.signal_delete_item.emit
        )
        self.actionAdd_Account_Group.triggered.connect(
            self.signal_add_account_group.emit
        )
        self.actionAdd_Security_Account.triggered.connect(
            self.signal_add_security_account.emit
        )
        self.actionEdit_Account_Tree_Item.triggered.connect(self.signal_edit_item.emit)

        self.contextMenuEvent = self.create_context_menu

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

    def create_context_menu(self, event: QContextMenuEvent) -> None:  # noqa: U100
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

    def finalize_setup(self) -> None:
        self.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_BALANCE_NATIVE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_BALANCE_BASE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_SHOW,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self.selectionModel().selectionChanged.connect(
            self.signal_selection_changed.emit
        )
