# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\widgets\transaction_table_widget.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_TransactionTableWidget(object):
    def setupUi(self, TransactionTableWidget):
        TransactionTableWidget.setObjectName("TransactionTableWidget")
        TransactionTableWidget.resize(454, 415)
        TransactionTableWidget.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.verticalLayout = QtWidgets.QVBoxLayout(TransactionTableWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.controlsHorizontalLayout = QtWidgets.QHBoxLayout()
        self.controlsHorizontalLayout.setObjectName("controlsHorizontalLayout")
        self.incomeToolButton = QtWidgets.QToolButton(TransactionTableWidget)
        self.incomeToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.incomeToolButton.setObjectName("incomeToolButton")
        self.controlsHorizontalLayout.addWidget(self.incomeToolButton)
        self.expenseToolButton = QtWidgets.QToolButton(TransactionTableWidget)
        self.expenseToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.expenseToolButton.setObjectName("expenseToolButton")
        self.controlsHorizontalLayout.addWidget(self.expenseToolButton)
        self.transferToolButton = QtWidgets.QToolButton(TransactionTableWidget)
        self.transferToolButton.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.transferToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.transferToolButton.setObjectName("transferToolButton")
        self.controlsHorizontalLayout.addWidget(self.transferToolButton)
        self.buyToolButton = QtWidgets.QToolButton(TransactionTableWidget)
        self.buyToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.buyToolButton.setObjectName("buyToolButton")
        self.controlsHorizontalLayout.addWidget(self.buyToolButton)
        self.sellToolButton = QtWidgets.QToolButton(TransactionTableWidget)
        self.sellToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.sellToolButton.setObjectName("sellToolButton")
        self.controlsHorizontalLayout.addWidget(self.sellToolButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.controlsHorizontalLayout.addItem(spacerItem)
        self.filterToolButton = QtWidgets.QToolButton(TransactionTableWidget)
        self.filterToolButton.setObjectName("filterToolButton")
        self.controlsHorizontalLayout.addWidget(self.filterToolButton)
        self.searchLineEdit = QtWidgets.QLineEdit(TransactionTableWidget)
        self.searchLineEdit.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.searchLineEdit.sizePolicy().hasHeightForWidth())
        self.searchLineEdit.setSizePolicy(sizePolicy)
        self.searchLineEdit.setMinimumSize(QtCore.QSize(200, 0))
        self.searchLineEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.searchLineEdit.setObjectName("searchLineEdit")
        self.controlsHorizontalLayout.addWidget(self.searchLineEdit)
        self.verticalLayout.addLayout(self.controlsHorizontalLayout)
        self.tableView = QtWidgets.QTableView(TransactionTableWidget)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setHighlightSections(False)
        self.tableView.horizontalHeader().setSortIndicatorShown(True)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.tableView)
        self.transactionsLabel = QtWidgets.QLabel(TransactionTableWidget)
        self.transactionsLabel.setObjectName("transactionsLabel")
        self.verticalLayout.addWidget(self.transactionsLabel)
        self.actionExpense = QtGui.QAction(TransactionTableWidget)
        self.actionExpense.setObjectName("actionExpense")
        self.actionIncome = QtGui.QAction(TransactionTableWidget)
        self.actionIncome.setObjectName("actionIncome")
        self.actionBuy = QtGui.QAction(TransactionTableWidget)
        self.actionBuy.setObjectName("actionBuy")
        self.actionSell = QtGui.QAction(TransactionTableWidget)
        self.actionSell.setObjectName("actionSell")
        self.actionRefund = QtGui.QAction(TransactionTableWidget)
        self.actionRefund.setObjectName("actionRefund")
        self.actionCash_Transfer = QtGui.QAction(TransactionTableWidget)
        self.actionCash_Transfer.setObjectName("actionCash_Transfer")
        self.actionSecurity_Transfer = QtGui.QAction(TransactionTableWidget)
        self.actionSecurity_Transfer.setObjectName("actionSecurity_Transfer")
        self.actionDelete = QtGui.QAction(TransactionTableWidget)
        self.actionDelete.setShortcutContext(QtCore.Qt.ShortcutContext.ApplicationShortcut)
        self.actionDelete.setObjectName("actionDelete")
        self.actionEdit = QtGui.QAction(TransactionTableWidget)
        self.actionEdit.setObjectName("actionEdit")
        self.actionDuplicate = QtGui.QAction(TransactionTableWidget)
        self.actionDuplicate.setObjectName("actionDuplicate")
        self.actionFilter_Transactions = QtGui.QAction(TransactionTableWidget)
        self.actionFilter_Transactions.setObjectName("actionFilter_Transactions")
        self.actionReset_Columns = QtGui.QAction(TransactionTableWidget)
        self.actionReset_Columns.setObjectName("actionReset_Columns")
        self.actionResize_Columns_to_Fit = QtGui.QAction(TransactionTableWidget)
        self.actionResize_Columns_to_Fit.setObjectName("actionResize_Columns_to_Fit")
        self.actionShow_All_Columns = QtGui.QAction(TransactionTableWidget)
        self.actionShow_All_Columns.setObjectName("actionShow_All_Columns")
        self.actionAdd_Tags = QtGui.QAction(TransactionTableWidget)
        self.actionAdd_Tags.setObjectName("actionAdd_Tags")
        self.actionRemove_Tags = QtGui.QAction(TransactionTableWidget)
        self.actionRemove_Tags.setObjectName("actionRemove_Tags")
        self.actionFind_Related = QtGui.QAction(TransactionTableWidget)
        self.actionFind_Related.setObjectName("actionFind_Related")

        self.retranslateUi(TransactionTableWidget)
        QtCore.QMetaObject.connectSlotsByName(TransactionTableWidget)

    def retranslateUi(self, TransactionTableWidget):
        _translate = QtCore.QCoreApplication.translate
        TransactionTableWidget.setWindowTitle(_translate("TransactionTableWidget", "Form"))
        self.incomeToolButton.setText(_translate("TransactionTableWidget", "..."))
        self.expenseToolButton.setText(_translate("TransactionTableWidget", "..."))
        self.transferToolButton.setText(_translate("TransactionTableWidget", "Transfer"))
        self.buyToolButton.setText(_translate("TransactionTableWidget", "..."))
        self.sellToolButton.setText(_translate("TransactionTableWidget", "..."))
        self.filterToolButton.setText(_translate("TransactionTableWidget", "..."))
        self.searchLineEdit.setToolTip(_translate("TransactionTableWidget", "<html><head/><body><p>Search text in all table columns (including hidden columns)<br/>For advanced filtering, use the Filter button to the left<br/><br/>Special regex characters:<br/>. matches any character<br/>* matches zero or more of preceding token<br/>? matches zero or one of preceding token<br/>+ matches one or more of the preceding token<br/>^ matches the beginning of a string<br/>$ matches the end of a string<br/>| matches the expression to the right or left<br/>[...] matches any character within square brackets<br/>(...) groups tokens together<br/>\\ escapes a special character</p></body></html>"))
        self.searchLineEdit.setPlaceholderText(_translate("TransactionTableWidget", "Search Transactions"))
        self.tableView.setStatusTip(_translate("TransactionTableWidget", "Transaction Table: right-click to open the context menu"))
        self.transactionsLabel.setText(_translate("TransactionTableWidget", "Showing Transactions: 0/0"))
        self.actionExpense.setText(_translate("TransactionTableWidget", "Expense"))
        self.actionExpense.setShortcut(_translate("TransactionTableWidget", "E"))
        self.actionIncome.setText(_translate("TransactionTableWidget", "Income"))
        self.actionIncome.setShortcut(_translate("TransactionTableWidget", "I"))
        self.actionBuy.setText(_translate("TransactionTableWidget", "Buy"))
        self.actionBuy.setShortcut(_translate("TransactionTableWidget", "B"))
        self.actionSell.setText(_translate("TransactionTableWidget", "Sell"))
        self.actionSell.setShortcut(_translate("TransactionTableWidget", "S"))
        self.actionRefund.setText(_translate("TransactionTableWidget", "Refund"))
        self.actionRefund.setToolTip(_translate("TransactionTableWidget", "Only Expenses can be refunded"))
        self.actionCash_Transfer.setText(_translate("TransactionTableWidget", "Cash Transfer"))
        self.actionSecurity_Transfer.setText(_translate("TransactionTableWidget", "Security Transfer"))
        self.actionDelete.setText(_translate("TransactionTableWidget", "Delete"))
        self.actionDelete.setShortcut(_translate("TransactionTableWidget", "Del"))
        self.actionEdit.setText(_translate("TransactionTableWidget", "Edit"))
        self.actionEdit.setToolTip(_translate("TransactionTableWidget", "Only Transactions of same type can be edited"))
        self.actionDuplicate.setText(_translate("TransactionTableWidget", "Duplicate"))
        self.actionFilter_Transactions.setText(_translate("TransactionTableWidget", "Filter Transactions"))
        self.actionFilter_Transactions.setToolTip(_translate("TransactionTableWidget", "Filter Transactions"))
        self.actionReset_Columns.setText(_translate("TransactionTableWidget", "Reset Columns"))
        self.actionResize_Columns_to_Fit.setText(_translate("TransactionTableWidget", "Resize Columns to Fit"))
        self.actionShow_All_Columns.setText(_translate("TransactionTableWidget", "Show All Columns"))
        self.actionAdd_Tags.setText(_translate("TransactionTableWidget", "Add Tags"))
        self.actionRemove_Tags.setText(_translate("TransactionTableWidget", "Remove Tags"))
        self.actionFind_Related.setText(_translate("TransactionTableWidget", "Find related"))
        self.actionFind_Related.setToolTip(_translate("TransactionTableWidget", "Show refunded Expense and its Refunds"))
