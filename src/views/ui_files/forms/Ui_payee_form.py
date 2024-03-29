# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\forms\payee_form.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_PayeeForm(object):
    def setupUi(self, PayeeForm):
        PayeeForm.setObjectName("PayeeForm")
        PayeeForm.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        PayeeForm.resize(500, 400)
        self.horizontalLayout = QtWidgets.QHBoxLayout(PayeeForm)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.leftVerticalLayout = QtWidgets.QVBoxLayout()
        self.leftVerticalLayout.setObjectName("leftVerticalLayout")
        self.controlsHorizontalLayout = QtWidgets.QHBoxLayout()
        self.controlsHorizontalLayout.setObjectName("controlsHorizontalLayout")
        self.addToolButton = QtWidgets.QToolButton(PayeeForm)
        self.addToolButton.setObjectName("addToolButton")
        self.controlsHorizontalLayout.addWidget(self.addToolButton)
        self.renameToolButton = QtWidgets.QToolButton(PayeeForm)
        self.renameToolButton.setObjectName("renameToolButton")
        self.controlsHorizontalLayout.addWidget(self.renameToolButton)
        self.removeToolButton = QtWidgets.QToolButton(PayeeForm)
        self.removeToolButton.setObjectName("removeToolButton")
        self.controlsHorizontalLayout.addWidget(self.removeToolButton)
        self.showTransactionsToolButton = QtWidgets.QToolButton(PayeeForm)
        self.showTransactionsToolButton.setObjectName("showTransactionsToolButton")
        self.controlsHorizontalLayout.addWidget(self.showTransactionsToolButton)
        self.searchLineEdit = QtWidgets.QLineEdit(PayeeForm)
        self.searchLineEdit.setClearButtonEnabled(True)
        self.searchLineEdit.setObjectName("searchLineEdit")
        self.controlsHorizontalLayout.addWidget(self.searchLineEdit)
        self.leftVerticalLayout.addLayout(self.controlsHorizontalLayout)
        self.tableView = QtWidgets.QTableView(PayeeForm)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setHighlightSections(False)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setVisible(False)
        self.leftVerticalLayout.addWidget(self.tableView)
        self.horizontalLayout.addLayout(self.leftVerticalLayout)
        self.actionAdd_Payee = QtGui.QAction(PayeeForm)
        self.actionAdd_Payee.setObjectName("actionAdd_Payee")
        self.actionRename_Payee = QtGui.QAction(PayeeForm)
        self.actionRename_Payee.setObjectName("actionRename_Payee")
        self.actionRemove_Payee = QtGui.QAction(PayeeForm)
        self.actionRemove_Payee.setObjectName("actionRemove_Payee")
        self.actionShow_Transactions = QtGui.QAction(PayeeForm)
        self.actionShow_Transactions.setObjectName("actionShow_Transactions")

        self.retranslateUi(PayeeForm)
        QtCore.QMetaObject.connectSlotsByName(PayeeForm)

    def retranslateUi(self, PayeeForm):
        _translate = QtCore.QCoreApplication.translate
        PayeeForm.setWindowTitle(_translate("PayeeForm", "Payees"))
        self.addToolButton.setText(_translate("PayeeForm", "..."))
        self.renameToolButton.setText(_translate("PayeeForm", "..."))
        self.removeToolButton.setText(_translate("PayeeForm", "..."))
        self.showTransactionsToolButton.setText(_translate("PayeeForm", "..."))
        self.searchLineEdit.setToolTip(_translate("PayeeForm", "<html><head/><body><p>Special characters:</p><p>* matches zero or more of any characters<br/>? matches any single character<br/>[...] matches any character within square brackets</p></body></html>"))
        self.searchLineEdit.setPlaceholderText(_translate("PayeeForm", "Search Payees"))
        self.actionAdd_Payee.setText(_translate("PayeeForm", "Add Payee"))
        self.actionRename_Payee.setText(_translate("PayeeForm", "Rename Payee"))
        self.actionRemove_Payee.setText(_translate("PayeeForm", "Remove Payee(s)"))
        self.actionRemove_Payee.setShortcut(_translate("PayeeForm", "Del"))
        self.actionShow_Transactions.setText(_translate("PayeeForm", "Show Transactions"))
