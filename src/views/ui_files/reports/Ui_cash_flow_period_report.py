# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\reports\cash_flow_period_report.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_CashFlowPeriodReport(object):
    def setupUi(self, CashFlowPeriodReport):
        CashFlowPeriodReport.setObjectName("CashFlowPeriodReport")
        CashFlowPeriodReport.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        CashFlowPeriodReport.resize(800, 600)
        CashFlowPeriodReport.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.horizontalLayout = QtWidgets.QHBoxLayout(CashFlowPeriodReport)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tableView = QtWidgets.QTableView(CashFlowPeriodReport)
        self.tableView.setObjectName("tableView")
        self.horizontalLayout.addWidget(self.tableView)
        self.line = QtWidgets.QFrame(CashFlowPeriodReport)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)

        self.retranslateUi(CashFlowPeriodReport)
        QtCore.QMetaObject.connectSlotsByName(CashFlowPeriodReport)

    def retranslateUi(self, CashFlowPeriodReport):
        _translate = QtCore.QCoreApplication.translate
        CashFlowPeriodReport.setWindowTitle(_translate("CashFlowPeriodReport", "Cash Flow Report"))
