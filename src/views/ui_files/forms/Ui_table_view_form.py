# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\forms\table_view_form.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_TableViewForm(object):
    def setupUi(self, TableViewForm):
        TableViewForm.setObjectName("TableViewForm")
        TableViewForm.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        TableViewForm.resize(700, 200)
        TableViewForm.setWindowTitle("")
        TableViewForm.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.verticalLayout = QtWidgets.QVBoxLayout(TableViewForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableView = QtWidgets.QTableView(TableViewForm)
        self.tableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setHighlightSections(False)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.tableView)

        self.retranslateUi(TableViewForm)
        QtCore.QMetaObject.connectSlotsByName(TableViewForm)

    def retranslateUi(self, TableViewForm):
        pass
