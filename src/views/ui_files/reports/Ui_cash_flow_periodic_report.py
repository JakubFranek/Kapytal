# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\reports\cash_flow_periodic_report.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_CashFlowPeriodicReport(object):
    def setupUi(self, CashFlowPeriodicReport):
        CashFlowPeriodicReport.setObjectName("CashFlowPeriodicReport")
        CashFlowPeriodicReport.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        CashFlowPeriodicReport.resize(800, 600)
        CashFlowPeriodicReport.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.horizontalLayout = QtWidgets.QHBoxLayout(CashFlowPeriodicReport)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(CashFlowPeriodicReport)
        self.tabWidget.setObjectName("tabWidget")
        self.tableTab = QtWidgets.QWidget()
        self.tableTab.setObjectName("tableTab")
        self.tableTabVerticalLayout = QtWidgets.QVBoxLayout(self.tableTab)
        self.tableTabVerticalLayout.setObjectName("tableTabVerticalLayout")
        self.currencyNoteLabel = QtWidgets.QLabel(self.tableTab)
        self.currencyNoteLabel.setObjectName("currencyNoteLabel")
        self.tableTabVerticalLayout.addWidget(self.currencyNoteLabel)
        self.tableView = QtWidgets.QTableView(self.tableTab)
        self.tableView.setSortingEnabled(True)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setHighlightSections(True)
        self.tableView.horizontalHeader().setStretchLastSection(False)
        self.tableView.verticalHeader().setHighlightSections(True)
        self.tableTabVerticalLayout.addWidget(self.tableView)
        self.tabWidget.addTab(self.tableTab, "")
        self.chartTab = QtWidgets.QWidget()
        self.chartTab.setObjectName("chartTab")
        self.chartTabVerticalLayout = QtWidgets.QVBoxLayout(self.chartTab)
        self.chartTabVerticalLayout.setObjectName("chartTabVerticalLayout")
        self.tabWidget.addTab(self.chartTab, "")
        self.horizontalLayout.addWidget(self.tabWidget)

        self.retranslateUi(CashFlowPeriodicReport)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(CashFlowPeriodicReport)

    def retranslateUi(self, CashFlowPeriodicReport):
        _translate = QtCore.QCoreApplication.translate
        CashFlowPeriodicReport.setWindowTitle(_translate("CashFlowPeriodicReport", "Cash Flow Report"))
        self.currencyNoteLabel.setText(_translate("CashFlowPeriodicReport", "All values in XXX"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tableTab), _translate("CashFlowPeriodicReport", "Table"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.chartTab), _translate("CashFlowPeriodicReport", "Chart"))
