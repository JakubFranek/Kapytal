# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\forms\transaction_table_form.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_TransactionTableForm(object):
    def setupUi(self, TransactionTableForm):
        TransactionTableForm.setObjectName("TransactionTableForm")
        TransactionTableForm.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        TransactionTableForm.resize(800, 500)
        TransactionTableForm.setWindowTitle("")
        self.verticalLayout = QtWidgets.QVBoxLayout(TransactionTableForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.searchLineEdit = QtWidgets.QLineEdit(parent=TransactionTableForm)
        self.searchLineEdit.setObjectName("searchLineEdit")
        self.verticalLayout.addWidget(self.searchLineEdit)
        self.tableView = QtWidgets.QTableView(parent=TransactionTableForm)
        self.tableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setHighlightSections(False)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.tableView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.selectedTransactionsLabel = QtWidgets.QLabel(parent=TransactionTableForm)
        self.selectedTransactionsLabel.setObjectName("selectedTransactionsLabel")
        self.horizontalLayout.addWidget(self.selectedTransactionsLabel)
        self.line_2 = QtWidgets.QFrame(parent=TransactionTableForm)
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout.addWidget(self.line_2)
        self.selectedTotalLabel = QtWidgets.QLabel(parent=TransactionTableForm)
        self.selectedTotalLabel.setObjectName("selectedTotalLabel")
        self.horizontalLayout.addWidget(self.selectedTotalLabel)
        self.line = QtWidgets.QFrame(parent=TransactionTableForm)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.shownTransactionsLabel = QtWidgets.QLabel(parent=TransactionTableForm)
        self.shownTransactionsLabel.setObjectName("shownTransactionsLabel")
        self.horizontalLayout.addWidget(self.shownTransactionsLabel)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(TransactionTableForm)
        QtCore.QMetaObject.connectSlotsByName(TransactionTableForm)

    def retranslateUi(self, TransactionTableForm):
        _translate = QtCore.QCoreApplication.translate
        self.selectedTransactionsLabel.setToolTip(_translate("TransactionTableForm", "<html><head/><body><p>Only Income, Expense and Refund Transaction amounts are used in the calculation.</p></body></html>"))
        self.selectedTransactionsLabel.setText(_translate("TransactionTableForm", "Selected Transactions: ???"))
        self.selectedTotalLabel.setText(_translate("TransactionTableForm", "Selected Total: ??? XXX"))
        self.shownTransactionsLabel.setToolTip(_translate("TransactionTableForm", "<html><head/><body><p>Shows how many Transactions have passed the Transaction Filter and are listed in Transaction Table.</p></body></html>"))
        self.shownTransactionsLabel.setText(_translate("TransactionTableForm", "Showing Transactions: 0 / 0"))
