# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\reports\cash_flow_total_report.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_CashFlowTotalReport(object):
    def setupUi(self, CashFlowTotalReport):
        CashFlowTotalReport.setObjectName("CashFlowTotalReport")
        CashFlowTotalReport.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        CashFlowTotalReport.resize(900, 600)
        self.horizontalLayout = QtWidgets.QHBoxLayout(CashFlowTotalReport)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.incomeLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.incomeLabel.setObjectName("incomeLabel")
        self.gridLayout.addWidget(self.incomeLabel, 0, 1, 1, 1)
        self.inwardTransfersLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.inwardTransfersLabel.setObjectName("inwardTransfersLabel")
        self.gridLayout.addWidget(self.inwardTransfersLabel, 1, 1, 1, 1)
        self.inflowLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(False)
        self.inflowLabel.setFont(font)
        self.inflowLabel.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.inflowLabel.setObjectName("inflowLabel")
        self.gridLayout.addWidget(self.inflowLabel, 4, 1, 1, 1)
        self.initialBalancesAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.initialBalancesAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.initialBalancesAmountLabel.setObjectName("initialBalancesAmountLabel")
        self.gridLayout.addWidget(self.initialBalancesAmountLabel, 3, 2, 1, 1)
        self.inflowAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(True)
        self.inflowAmountLabel.setFont(font)
        self.inflowAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.inflowAmountLabel.setObjectName("inflowAmountLabel")
        self.gridLayout.addWidget(self.inflowAmountLabel, 4, 2, 1, 1)
        self.inwardTransfersAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.inwardTransfersAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.inwardTransfersAmountLabel.setObjectName("inwardTransfersAmountLabel")
        self.gridLayout.addWidget(self.inwardTransfersAmountLabel, 1, 2, 1, 1)
        self.incomeAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.incomeAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.incomeAmountLabel.setObjectName("incomeAmountLabel")
        self.gridLayout.addWidget(self.incomeAmountLabel, 0, 2, 1, 1)
        self.refundsLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.refundsLabel.setObjectName("refundsLabel")
        self.gridLayout.addWidget(self.refundsLabel, 2, 1, 1, 1)
        self.refundsAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.refundsAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.refundsAmountLabel.setObjectName("refundsAmountLabel")
        self.gridLayout.addWidget(self.refundsAmountLabel, 2, 2, 1, 1)
        self.initialBalancesLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.initialBalancesLabel.setObjectName("initialBalancesLabel")
        self.gridLayout.addWidget(self.initialBalancesLabel, 3, 1, 1, 1)
        self.incomeToolButton = QtWidgets.QToolButton(CashFlowTotalReport)
        self.incomeToolButton.setObjectName("incomeToolButton")
        self.gridLayout.addWidget(self.incomeToolButton, 0, 0, 1, 1)
        self.inwardTransfersToolButton = QtWidgets.QToolButton(CashFlowTotalReport)
        self.inwardTransfersToolButton.setObjectName("inwardTransfersToolButton")
        self.gridLayout.addWidget(self.inwardTransfersToolButton, 1, 0, 1, 1)
        self.refundsToolButton = QtWidgets.QToolButton(CashFlowTotalReport)
        self.refundsToolButton.setObjectName("refundsToolButton")
        self.gridLayout.addWidget(self.refundsToolButton, 2, 0, 1, 1)
        self.totalInflowToolButton = QtWidgets.QToolButton(CashFlowTotalReport)
        self.totalInflowToolButton.setObjectName("totalInflowToolButton")
        self.gridLayout.addWidget(self.totalInflowToolButton, 4, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.line_1 = QtWidgets.QFrame(CashFlowTotalReport)
        self.line_1.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_1.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_1.setObjectName("line_1")
        self.verticalLayout.addWidget(self.line_1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.outflowAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(True)
        self.outflowAmountLabel.setFont(font)
        self.outflowAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.outflowAmountLabel.setObjectName("outflowAmountLabel")
        self.gridLayout_2.addWidget(self.outflowAmountLabel, 2, 2, 1, 1)
        self.outwardTransfersLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.outwardTransfersLabel.setObjectName("outwardTransfersLabel")
        self.gridLayout_2.addWidget(self.outwardTransfersLabel, 1, 1, 1, 1)
        self.outwardTransfersAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.outwardTransfersAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.outwardTransfersAmountLabel.setObjectName("outwardTransfersAmountLabel")
        self.gridLayout_2.addWidget(self.outwardTransfersAmountLabel, 1, 2, 1, 1)
        self.expensesLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.expensesLabel.setObjectName("expensesLabel")
        self.gridLayout_2.addWidget(self.expensesLabel, 0, 1, 1, 1)
        self.expensesAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.expensesAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.expensesAmountLabel.setObjectName("expensesAmountLabel")
        self.gridLayout_2.addWidget(self.expensesAmountLabel, 0, 2, 1, 1)
        self.outflowLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(False)
        self.outflowLabel.setFont(font)
        self.outflowLabel.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.outflowLabel.setObjectName("outflowLabel")
        self.gridLayout_2.addWidget(self.outflowLabel, 2, 1, 1, 1)
        self.expensesToolButton = QtWidgets.QToolButton(CashFlowTotalReport)
        self.expensesToolButton.setObjectName("expensesToolButton")
        self.gridLayout_2.addWidget(self.expensesToolButton, 0, 0, 1, 1)
        self.outwardTransfersToolButton = QtWidgets.QToolButton(CashFlowTotalReport)
        self.outwardTransfersToolButton.setObjectName("outwardTransfersToolButton")
        self.gridLayout_2.addWidget(self.outwardTransfersToolButton, 1, 0, 1, 1)
        self.totalOutflowToolButton = QtWidgets.QToolButton(CashFlowTotalReport)
        self.totalOutflowToolButton.setObjectName("totalOutflowToolButton")
        self.gridLayout_2.addWidget(self.totalOutflowToolButton, 2, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.line_2 = QtWidgets.QFrame(CashFlowTotalReport)
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.cashFlowAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(False)
        self.cashFlowAmountLabel.setFont(font)
        self.cashFlowAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.cashFlowAmountLabel.setObjectName("cashFlowAmountLabel")
        self.gridLayout_3.addWidget(self.cashFlowAmountLabel, 0, 2, 1, 1)
        self.gainLossSecuritiesLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.gainLossSecuritiesLabel.setObjectName("gainLossSecuritiesLabel")
        self.gridLayout_3.addWidget(self.gainLossSecuritiesLabel, 2, 1, 1, 1)
        self.netGrowthLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(True)
        self.netGrowthLabel.setFont(font)
        self.netGrowthLabel.setObjectName("netGrowthLabel")
        self.gridLayout_3.addWidget(self.netGrowthLabel, 5, 1, 1, 1)
        self.gainLossCurrenciesLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.gainLossCurrenciesLabel.setObjectName("gainLossCurrenciesLabel")
        self.gridLayout_3.addWidget(self.gainLossCurrenciesLabel, 3, 1, 1, 1)
        self.netGrowthAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(True)
        self.netGrowthAmountLabel.setFont(font)
        self.netGrowthAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.netGrowthAmountLabel.setObjectName("netGrowthAmountLabel")
        self.gridLayout_3.addWidget(self.netGrowthAmountLabel, 5, 2, 1, 1)
        self.savingsRateLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.savingsRateLabel.setObjectName("savingsRateLabel")
        self.gridLayout_3.addWidget(self.savingsRateLabel, 1, 1, 1, 1)
        self.savingsRateAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.savingsRateAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.savingsRateAmountLabel.setObjectName("savingsRateAmountLabel")
        self.gridLayout_3.addWidget(self.savingsRateAmountLabel, 1, 2, 1, 1)
        self.gainLossLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(False)
        font.setUnderline(False)
        self.gainLossLabel.setFont(font)
        self.gainLossLabel.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.gainLossLabel.setObjectName("gainLossLabel")
        self.gridLayout_3.addWidget(self.gainLossLabel, 4, 1, 1, 1)
        self.gainLossSecuritiesAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.gainLossSecuritiesAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.gainLossSecuritiesAmountLabel.setObjectName("gainLossSecuritiesAmountLabel")
        self.gridLayout_3.addWidget(self.gainLossSecuritiesAmountLabel, 2, 2, 1, 1)
        self.gainLossCurrenciesAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.gainLossCurrenciesAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.gainLossCurrenciesAmountLabel.setObjectName("gainLossCurrenciesAmountLabel")
        self.gridLayout_3.addWidget(self.gainLossCurrenciesAmountLabel, 3, 2, 1, 1)
        self.gainLossAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(False)
        self.gainLossAmountLabel.setFont(font)
        self.gainLossAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.gainLossAmountLabel.setObjectName("gainLossAmountLabel")
        self.gridLayout_3.addWidget(self.gainLossAmountLabel, 4, 2, 1, 1)
        self.cashFlowLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(False)
        font.setUnderline(False)
        self.cashFlowLabel.setFont(font)
        self.cashFlowLabel.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.cashFlowLabel.setObjectName("cashFlowLabel")
        self.gridLayout_3.addWidget(self.cashFlowLabel, 0, 1, 1, 1)
        self.cashflowToolButton = QtWidgets.QToolButton(CashFlowTotalReport)
        self.cashflowToolButton.setObjectName("cashflowToolButton")
        self.gridLayout_3.addWidget(self.cashflowToolButton, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_3)
        self.line = QtWidgets.QFrame(CashFlowTotalReport)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.recalculateToolButton = QtWidgets.QToolButton(CashFlowTotalReport)
        self.recalculateToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.recalculateToolButton.setObjectName("recalculateToolButton")
        self.horizontalLayout_2.addWidget(self.recalculateToolButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.actionShow_Income_Transactions = QtGui.QAction(CashFlowTotalReport)
        self.actionShow_Income_Transactions.setObjectName("actionShow_Income_Transactions")
        self.actionShow_Inward_Transfers = QtGui.QAction(CashFlowTotalReport)
        self.actionShow_Inward_Transfers.setObjectName("actionShow_Inward_Transfers")
        self.actionShow_Refunds = QtGui.QAction(CashFlowTotalReport)
        self.actionShow_Refunds.setObjectName("actionShow_Refunds")
        self.actionShow_Inflow_Transactions = QtGui.QAction(CashFlowTotalReport)
        self.actionShow_Inflow_Transactions.setObjectName("actionShow_Inflow_Transactions")
        self.actionShow_Expense_Transactions = QtGui.QAction(CashFlowTotalReport)
        self.actionShow_Expense_Transactions.setObjectName("actionShow_Expense_Transactions")
        self.actionShow_Outward_Transfers = QtGui.QAction(CashFlowTotalReport)
        self.actionShow_Outward_Transfers.setObjectName("actionShow_Outward_Transfers")
        self.actionShow_Outflow_Transactions = QtGui.QAction(CashFlowTotalReport)
        self.actionShow_Outflow_Transactions.setObjectName("actionShow_Outflow_Transactions")
        self.actionShow_All_Transactions = QtGui.QAction(CashFlowTotalReport)
        self.actionShow_All_Transactions.setObjectName("actionShow_All_Transactions")
        self.actionRecalculate_Report = QtGui.QAction(CashFlowTotalReport)
        self.actionRecalculate_Report.setObjectName("actionRecalculate_Report")

        self.retranslateUi(CashFlowTotalReport)
        QtCore.QMetaObject.connectSlotsByName(CashFlowTotalReport)

    def retranslateUi(self, CashFlowTotalReport):
        _translate = QtCore.QCoreApplication.translate
        CashFlowTotalReport.setWindowTitle(_translate("CashFlowTotalReport", "Cash Flow Report"))
        self.incomeLabel.setText(_translate("CashFlowTotalReport", "Income"))
        self.inwardTransfersLabel.setText(_translate("CashFlowTotalReport", "Inward Transfers"))
        self.inflowLabel.setText(_translate("CashFlowTotalReport", "Total Inflow"))
        self.initialBalancesAmountLabel.setToolTip(_translate("CashFlowTotalReport", "<html><head/><body><p>Cash Account Initial Balances are deemed &quot;effective&quot; the day before first Transaction related to the given Cash Account.</p></body></html>"))
        self.initialBalancesAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.inflowAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.inwardTransfersAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.incomeAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.refundsLabel.setText(_translate("CashFlowTotalReport", "Refunds"))
        self.refundsAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.initialBalancesLabel.setToolTip(_translate("CashFlowTotalReport", "<html><head/><body><p>Cash Account Initial Balances are deemed &quot;effective&quot; the day before first Transaction related to the given Cash Account.</p></body></html>"))
        self.initialBalancesLabel.setText(_translate("CashFlowTotalReport", "Cash Account Initial Balances"))
        self.incomeToolButton.setText(_translate("CashFlowTotalReport", "..."))
        self.inwardTransfersToolButton.setText(_translate("CashFlowTotalReport", "..."))
        self.refundsToolButton.setText(_translate("CashFlowTotalReport", "..."))
        self.totalInflowToolButton.setText(_translate("CashFlowTotalReport", "..."))
        self.outflowAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.outwardTransfersLabel.setText(_translate("CashFlowTotalReport", "Outward Transfers"))
        self.outwardTransfersAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.expensesLabel.setText(_translate("CashFlowTotalReport", "Expenses"))
        self.expensesAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.outflowLabel.setText(_translate("CashFlowTotalReport", "Total Outflow"))
        self.expensesToolButton.setText(_translate("CashFlowTotalReport", "..."))
        self.outwardTransfersToolButton.setText(_translate("CashFlowTotalReport", "..."))
        self.totalOutflowToolButton.setText(_translate("CashFlowTotalReport", "..."))
        self.cashFlowAmountLabel.setToolTip(_translate("CashFlowTotalReport", "<html><head/><body><p>Cash Flow is the difference between Total Inflow and Total Outflow. It does not reflect any Currency exchange rate or Security price fluctuations.</p></body></html>"))
        self.cashFlowAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.gainLossSecuritiesLabel.setToolTip(_translate("CashFlowTotalReport", "<html><head/><body><p>Represents Gain / Loss of Securities due to their Price changing over time. The effect of Exchange Rate fluctuations on non-base Currency Securities is also included within this quantity.</p></body></html>"))
        self.gainLossSecuritiesLabel.setText(_translate("CashFlowTotalReport", "Securities Gain / Loss"))
        self.netGrowthLabel.setToolTip(_translate("CashFlowTotalReport", "<html><head/><body><p>Net Growth is the sum of Cash Flow and Total Gain / Loss</p></body></html>"))
        self.netGrowthLabel.setText(_translate("CashFlowTotalReport", "Net Growth"))
        self.gainLossCurrenciesLabel.setToolTip(_translate("CashFlowTotalReport", "<html><head/><body><p>Represents Gain / Loss caused by fluctuating Exchange Rates and inter-Currency Cash Transfers.</p></body></html>"))
        self.gainLossCurrenciesLabel.setText(_translate("CashFlowTotalReport", "Currencies Gain / Loss"))
        self.netGrowthAmountLabel.setToolTip(_translate("CashFlowTotalReport", "Net Growth is the sum of Cash Flow and Total Gain / Loss"))
        self.netGrowthAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.savingsRateLabel.setToolTip(_translate("CashFlowTotalReport", "<html><head/><body><p>Cash Flow / (Income + Inward Transfers)</p></body></html>"))
        self.savingsRateLabel.setText(_translate("CashFlowTotalReport", "Savings Rate"))
        self.savingsRateAmountLabel.setToolTip(_translate("CashFlowTotalReport", "<html><head/><body><p>Cash Flow / (Income + Inward Transfers)</p></body></html>"))
        self.savingsRateAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.gainLossLabel.setText(_translate("CashFlowTotalReport", "Total Gain / Loss"))
        self.gainLossSecuritiesAmountLabel.setToolTip(_translate("CashFlowTotalReport", "<html><head/><body><p>Represents Gain / Loss of Securities due to their Price changing over time. The effect of Exchange Rate fluctuations on non-base Currency Securities is also included within this quantity.</p></body></html>"))
        self.gainLossSecuritiesAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.gainLossCurrenciesAmountLabel.setToolTip(_translate("CashFlowTotalReport", "<html><head/><body><p>Represents Gain / Loss caused by fluctuating Exchange Rates and inter-Currency Cash Transfers.</p></body></html>"))
        self.gainLossCurrenciesAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.gainLossAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.cashFlowLabel.setToolTip(_translate("CashFlowTotalReport", "<html><head/><body><p>Cash Flow is the difference between Total Inflow and Total Outflow. It does not reflect any Currency exchange rate or Security price fluctuations.</p></body></html>"))
        self.cashFlowLabel.setText(_translate("CashFlowTotalReport", "Cash Flow"))
        self.cashflowToolButton.setText(_translate("CashFlowTotalReport", "..."))
        self.recalculateToolButton.setText(_translate("CashFlowTotalReport", "Recalculate Report"))
        self.actionShow_Income_Transactions.setText(_translate("CashFlowTotalReport", "Show Income Transactions"))
        self.actionShow_Inward_Transfers.setText(_translate("CashFlowTotalReport", "Show Inward Transfers"))
        self.actionShow_Refunds.setText(_translate("CashFlowTotalReport", "Show Refunds"))
        self.actionShow_Inflow_Transactions.setText(_translate("CashFlowTotalReport", "Show Inflow Transactions"))
        self.actionShow_Expense_Transactions.setText(_translate("CashFlowTotalReport", "Show Expense Transactions"))
        self.actionShow_Outward_Transfers.setText(_translate("CashFlowTotalReport", "Show Outward Transfers"))
        self.actionShow_Outflow_Transactions.setText(_translate("CashFlowTotalReport", "Show Outflow Transactions"))
        self.actionShow_All_Transactions.setText(_translate("CashFlowTotalReport", "Show All Transactions"))
        self.actionRecalculate_Report.setText(_translate("CashFlowTotalReport", "Recalculate Report"))
