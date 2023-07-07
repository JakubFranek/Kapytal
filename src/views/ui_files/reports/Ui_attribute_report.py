# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\reports\attribute_report.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_AttributeReport(object):
    def setupUi(self, AttributeReport):
        AttributeReport.setObjectName("AttributeReport")
        AttributeReport.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        AttributeReport.resize(800, 600)
        AttributeReport.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.horizontalLayout = QtWidgets.QHBoxLayout(AttributeReport)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtWidgets.QSplitter(AttributeReport)
        self.splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splitter.setObjectName("splitter")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.currencyNoteLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.currencyNoteLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.currencyNoteLabel.setObjectName("currencyNoteLabel")
        self.verticalLayout.addWidget(self.currencyNoteLabel)
        self.tableView = QtWidgets.QTableView(self.verticalLayoutWidget)
        self.tableView.setSortingEnabled(True)
        self.tableView.setObjectName("tableView")
        self.verticalLayout.addWidget(self.tableView)
        self.horizontalLayout.addWidget(self.splitter)
        self.actionExpand_All_Income = QtGui.QAction(AttributeReport)
        self.actionExpand_All_Income.setObjectName("actionExpand_All_Income")
        self.actionExpand_All_Expense = QtGui.QAction(AttributeReport)
        self.actionExpand_All_Expense.setObjectName("actionExpand_All_Expense")
        self.actionCollapse_All_Income = QtGui.QAction(AttributeReport)
        self.actionCollapse_All_Income.setObjectName("actionCollapse_All_Income")
        self.actionCollapse_All_Expense = QtGui.QAction(AttributeReport)
        self.actionCollapse_All_Expense.setObjectName("actionCollapse_All_Expense")

        self.retranslateUi(AttributeReport)
        QtCore.QMetaObject.connectSlotsByName(AttributeReport)

    def retranslateUi(self, AttributeReport):
        _translate = QtCore.QCoreApplication.translate
        AttributeReport.setWindowTitle(_translate("AttributeReport", "Category Report"))
        self.currencyNoteLabel.setText(_translate("AttributeReport", "All values in XXX"))
        self.actionExpand_All_Income.setText(_translate("AttributeReport", "Expand All"))
        self.actionExpand_All_Expense.setText(_translate("AttributeReport", "Expand All"))
        self.actionCollapse_All_Income.setText(_translate("AttributeReport", "Collapse All"))
        self.actionCollapse_All_Expense.setText(_translate("AttributeReport", "Collapse All"))
