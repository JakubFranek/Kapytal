# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\reports\sunburst_report.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SunburstReport(object):
    def setupUi(self, SunburstReport):
        SunburstReport.setObjectName("SunburstReport")
        SunburstReport.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        SunburstReport.resize(800, 600)
        SunburstReport.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.horizontalLayout = QtWidgets.QHBoxLayout(SunburstReport)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(SunburstReport)
        self.label.setText("")
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.actionExpand_All_Income = QtGui.QAction(SunburstReport)
        self.actionExpand_All_Income.setObjectName("actionExpand_All_Income")
        self.actionExpand_All_Expense = QtGui.QAction(SunburstReport)
        self.actionExpand_All_Expense.setObjectName("actionExpand_All_Expense")
        self.actionCollapse_All_Income = QtGui.QAction(SunburstReport)
        self.actionCollapse_All_Income.setObjectName("actionCollapse_All_Income")
        self.actionCollapse_All_Expense = QtGui.QAction(SunburstReport)
        self.actionCollapse_All_Expense.setObjectName("actionCollapse_All_Expense")

        self.retranslateUi(SunburstReport)
        QtCore.QMetaObject.connectSlotsByName(SunburstReport)

    def retranslateUi(self, SunburstReport):
        _translate = QtCore.QCoreApplication.translate
        SunburstReport.setWindowTitle(_translate("SunburstReport", "Sunburst Report"))
        self.actionExpand_All_Income.setText(_translate("SunburstReport", "Expand All"))
        self.actionExpand_All_Expense.setText(_translate("SunburstReport", "Expand All"))
        self.actionCollapse_All_Income.setText(_translate("SunburstReport", "Collapse All"))
        self.actionCollapse_All_Expense.setText(_translate("SunburstReport", "Collapse All"))
