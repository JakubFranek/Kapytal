import logging

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QContextMenuEvent, QCursor, QIcon
from PyQt6.QtWidgets import QHeaderView, QMenu, QTableView, QWidget


class TransactionTable(QTableView):
    signal_selection_changed = pyqtSignal()

    signal_add_cash_transaction = pyqtSignal()
    signal_add_cash_transfer = pyqtSignal()
    signal_add_security_transaction = pyqtSignal()
    signal_add_security_transfer = pyqtSignal()

    signal_edit_item = pyqtSignal()
    signal_duplicate_item = pyqtSignal()
    signal_delete_item = pyqtSignal()

    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )
        self.setObjectName("transactionTable")

        self.actionExpand_All.triggered.connect(self.expand_all)
        self.actionExpand_All_Below.triggered.connect(self.signal_expand_below.emit)
        self.actionCollapse_All.triggered.connect(self.collapse_all)
        self.actionDelete_Account_Tree_Item.triggered.connect(
            self.signal_delete_item.emit
        )
        self.actionAdd_Account_Group.triggered.connect(
            self.signal_add_account_group.emit
        )
        self.actionAdd_Security_Account.triggered.connect(
            self.signal_add_security_account.emit
        )
        self.actionAdd_Cash_Account.triggered.connect(self.signal_add_cash_account.emit)
        self.actionEdit_Account_Tree_Item.triggered.connect(self.signal_edit_item.emit)

        self.setStatusTip("Account Tree: right click to open the context menu")

        self.contextMenuEvent = self.create_context_menu

    def enable_actions(
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
        self.selectionModel().selectionChanged.connect(
            self.signal_selection_changed.emit
        )
