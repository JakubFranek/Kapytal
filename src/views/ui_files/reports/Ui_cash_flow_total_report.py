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
        CashFlowTotalReport.resize(800, 600)
        CashFlowTotalReport.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.horizontalLayout = QtWidgets.QHBoxLayout(CashFlowTotalReport)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.inflowFormLayout = QtWidgets.QFormLayout()
        self.inflowFormLayout.setObjectName("inflowFormLayout")
        self.incomeLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.incomeLabel.setObjectName("incomeLabel")
        self.inflowFormLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.incomeLabel)
        self.incomeAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.incomeAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.incomeAmountLabel.setObjectName("incomeAmountLabel")
        self.inflowFormLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.incomeAmountLabel)
        self.inwardTransfersLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.inwardTransfersLabel.setObjectName("inwardTransfersLabel")
        self.inflowFormLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.inwardTransfersLabel)
        self.inwardTransfersAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.inwardTransfersAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.inwardTransfersAmountLabel.setObjectName("inwardTransfersAmountLabel")
        self.inflowFormLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.inwardTransfersAmountLabel)
        self.refundsLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.refundsLabel.setObjectName("refundsLabel")
        self.inflowFormLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.refundsLabel)
        self.refundsAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.refundsAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.refundsAmountLabel.setObjectName("refundsAmountLabel")
        self.inflowFormLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.refundsAmountLabel)
        self.inflowLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(False)
        self.inflowLabel.setFont(font)
        self.inflowLabel.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.inflowLabel.setObjectName("inflowLabel")
        self.inflowFormLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.inflowLabel)
        self.inflowAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(True)
        self.inflowAmountLabel.setFont(font)
        self.inflowAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.inflowAmountLabel.setObjectName("inflowAmountLabel")
        self.inflowFormLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.inflowAmountLabel)
        self.verticalLayout.addLayout(self.inflowFormLayout)
        self.line_1 = QtWidgets.QFrame(CashFlowTotalReport)
        self.line_1.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_1.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_1.setObjectName("line_1")
        self.verticalLayout.addWidget(self.line_1)
        self.outflowFormLayout = QtWidgets.QFormLayout()
        self.outflowFormLayout.setObjectName("outflowFormLayout")
        self.expensesLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.expensesLabel.setObjectName("expensesLabel")
        self.outflowFormLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.expensesLabel)
        self.expensesAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.expensesAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.expensesAmountLabel.setObjectName("expensesAmountLabel")
        self.outflowFormLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.expensesAmountLabel)
        self.outwardTransfersLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.outwardTransfersLabel.setObjectName("outwardTransfersLabel")
        self.outflowFormLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.outwardTransfersLabel)
        self.outwardTransfersAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        self.outwardTransfersAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.outwardTransfersAmountLabel.setObjectName("outwardTransfersAmountLabel")
        self.outflowFormLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.outwardTransfersAmountLabel)
        self.outflowLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(False)
        self.outflowLabel.setFont(font)
        self.outflowLabel.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.outflowLabel.setObjectName("outflowLabel")
        self.outflowFormLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.outflowLabel)
        self.outflowAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(True)
        self.outflowAmountLabel.setFont(font)
        self.outflowAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.outflowAmountLabel.setObjectName("outflowAmountLabel")
        self.outflowFormLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.outflowAmountLabel)
        self.verticalLayout.addLayout(self.outflowFormLayout)
        self.line_2 = QtWidgets.QFrame(CashFlowTotalReport)
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.gainLossFormLayout = QtWidgets.QFormLayout()
        self.gainLossFormLayout.setObjectName("gainLossFormLayout")
        self.cashFlowLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(False)
        font.setUnderline(False)
        self.cashFlowLabel.setFont(font)
        self.cashFlowLabel.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.cashFlowLabel.setObjectName("cashFlowLabel")
        self.gainLossFormLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.cashFlowLabel)
        self.cashFlowAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(False)
        self.cashFlowAmountLabel.setFont(font)
        self.cashFlowAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.cashFlowAmountLabel.setObjectName("cashFlowAmountLabel")
        self.gainLossFormLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.cashFlowAmountLabel)
        self.gainLossLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(False)
        font.setUnderline(False)
        self.gainLossLabel.setFont(font)
        self.gainLossLabel.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.gainLossLabel.setObjectName("gainLossLabel")
        self.gainLossFormLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.gainLossLabel)
        self.gainLossAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(False)
        self.gainLossAmountLabel.setFont(font)
        self.gainLossAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.gainLossAmountLabel.setObjectName("gainLossAmountLabel")
        self.gainLossFormLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.gainLossAmountLabel)
        self.netGrowthLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(True)
        self.netGrowthLabel.setFont(font)
        self.netGrowthLabel.setObjectName("netGrowthLabel")
        self.gainLossFormLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.netGrowthLabel)
        self.netGrowthAmountLabel = QtWidgets.QLabel(CashFlowTotalReport)
        font = QtGui.QFont()
        font.setBold(True)
        self.netGrowthAmountLabel.setFont(font)
        self.netGrowthAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.netGrowthAmountLabel.setObjectName("netGrowthAmountLabel")
        self.gainLossFormLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.netGrowthAmountLabel)
        self.verticalLayout.addLayout(self.gainLossFormLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.line = QtWidgets.QFrame(CashFlowTotalReport)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)

        self.retranslateUi(CashFlowTotalReport)
        QtCore.QMetaObject.connectSlotsByName(CashFlowTotalReport)

    def retranslateUi(self, CashFlowTotalReport):
        _translate = QtCore.QCoreApplication.translate
        CashFlowTotalReport.setWindowTitle(_translate("CashFlowTotalReport", "Cash Flow Report"))
        self.incomeLabel.setText(_translate("CashFlowTotalReport", "Income"))
        self.incomeAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.inwardTransfersLabel.setText(_translate("CashFlowTotalReport", "Inward Transfers"))
        self.inwardTransfersAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.refundsLabel.setText(_translate("CashFlowTotalReport", "Refunds"))
        self.refundsAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.inflowLabel.setText(_translate("CashFlowTotalReport", "Total Inflow"))
        self.inflowAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.expensesLabel.setText(_translate("CashFlowTotalReport", "Expenses"))
        self.expensesAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.outwardTransfersLabel.setText(_translate("CashFlowTotalReport", "Outward Transfers"))
        self.outwardTransfersAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.outflowLabel.setText(_translate("CashFlowTotalReport", "Total Outflow"))
        self.outflowAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.cashFlowLabel.setToolTip(_translate("CashFlowTotalReport", "<html><head/><body><p>Cash Flow is the difference between Total Inflow and Total Outflow. It does not reflect any Currency exchange rate or Security price fluctuations.</p></body></html>"))
        self.cashFlowLabel.setText(_translate("CashFlowTotalReport", "Cash Flow"))
        self.cashFlowAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.gainLossLabel.setToolTip(_translate("CashFlowTotalReport", "<html><head/><body><p>Gain / Loss consists of the Currency exchange rate and Security price fluctuations.</p></body></html>"))
        self.gainLossLabel.setText(_translate("CashFlowTotalReport", "Gain / Loss"))
        self.gainLossAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))
        self.netGrowthLabel.setText(_translate("CashFlowTotalReport", "Net Growth"))
        self.netGrowthAmountLabel.setText(_translate("CashFlowTotalReport", "TextLabel"))