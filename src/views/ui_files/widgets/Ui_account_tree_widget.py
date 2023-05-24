# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\widgets\account_tree_widget.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_AccountTreeWidget(object):
    def setupUi(self, AccountTreeWidget):
        AccountTreeWidget.setObjectName("AccountTreeWidget")
        AccountTreeWidget.resize(400, 300)
        AccountTreeWidget.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.verticalLayout = QtWidgets.QVBoxLayout(AccountTreeWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.controlsHorizontalLayout = QtWidgets.QHBoxLayout()
        self.controlsHorizontalLayout.setObjectName("controlsHorizontalLayout")
        self.expandAllToolButton = QtWidgets.QToolButton(AccountTreeWidget)
        self.expandAllToolButton.setObjectName("expandAllToolButton")
        self.controlsHorizontalLayout.addWidget(self.expandAllToolButton)
        self.collapseAllToolButton = QtWidgets.QToolButton(AccountTreeWidget)
        self.collapseAllToolButton.setObjectName("collapseAllToolButton")
        self.controlsHorizontalLayout.addWidget(self.collapseAllToolButton)
        self.verticalLine_1 = QtWidgets.QFrame(AccountTreeWidget)
        self.verticalLine_1.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.verticalLine_1.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.verticalLine_1.setObjectName("verticalLine_1")
        self.controlsHorizontalLayout.addWidget(self.verticalLine_1)
        self.showAllToolButton = QtWidgets.QToolButton(AccountTreeWidget)
        self.showAllToolButton.setObjectName("showAllToolButton")
        self.controlsHorizontalLayout.addWidget(self.showAllToolButton)
        self.hideAllToolButton = QtWidgets.QToolButton(AccountTreeWidget)
        self.hideAllToolButton.setObjectName("hideAllToolButton")
        self.controlsHorizontalLayout.addWidget(self.hideAllToolButton)
        self.verticalLine_3 = QtWidgets.QFrame(AccountTreeWidget)
        self.verticalLine_3.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.verticalLine_3.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.verticalLine_3.setObjectName("verticalLine_3")
        self.controlsHorizontalLayout.addWidget(self.verticalLine_3)
        self.searchLineEdit = QtWidgets.QLineEdit(AccountTreeWidget)
        self.searchLineEdit.setObjectName("searchLineEdit")
        self.controlsHorizontalLayout.addWidget(self.searchLineEdit)
        self.verticalLayout.addLayout(self.controlsHorizontalLayout)
        self.treeView = QtWidgets.QTreeView(AccountTreeWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeView.sizePolicy().hasHeightForWidth())
        self.treeView.setSizePolicy(sizePolicy)
        self.treeView.setMouseTracking(False)
        self.treeView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setSortingEnabled(True)
        self.treeView.setObjectName("treeView")
        self.treeView.header().setHighlightSections(False)
        self.treeView.header().setMinimumSectionSize(20)
        self.treeView.header().setSortIndicatorShown(True)
        self.treeView.header().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.treeView)
        self.totalBalanceFormLayout = QtWidgets.QFormLayout()
        self.totalBalanceFormLayout.setObjectName("totalBalanceFormLayout")
        self.totalBaseBalanceLabel = QtWidgets.QLabel(AccountTreeWidget)
        self.totalBaseBalanceLabel.setObjectName("totalBaseBalanceLabel")
        self.totalBalanceFormLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.totalBaseBalanceLabel)
        self.totalBaseBalanceAmountLabel = QtWidgets.QLabel(AccountTreeWidget)
        self.totalBaseBalanceAmountLabel.setText("")
        self.totalBaseBalanceAmountLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.totalBaseBalanceAmountLabel.setObjectName("totalBaseBalanceAmountLabel")
        self.totalBalanceFormLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.totalBaseBalanceAmountLabel)
        self.verticalLayout.addLayout(self.totalBalanceFormLayout)
        self.actionAdd_Account_Group = QtGui.QAction(AccountTreeWidget)
        self.actionAdd_Account_Group.setObjectName("actionAdd_Account_Group")
        self.actionAdd_Security_Account = QtGui.QAction(AccountTreeWidget)
        self.actionAdd_Security_Account.setObjectName("actionAdd_Security_Account")
        self.actionAdd_Cash_Account = QtGui.QAction(AccountTreeWidget)
        self.actionAdd_Cash_Account.setObjectName("actionAdd_Cash_Account")
        self.actionEdit = QtGui.QAction(AccountTreeWidget)
        self.actionEdit.setObjectName("actionEdit")
        self.actionDelete = QtGui.QAction(AccountTreeWidget)
        self.actionDelete.setObjectName("actionDelete")
        self.actionExpand_All = QtGui.QAction(AccountTreeWidget)
        self.actionExpand_All.setObjectName("actionExpand_All")
        self.actionCollapse_All = QtGui.QAction(AccountTreeWidget)
        self.actionCollapse_All.setObjectName("actionCollapse_All")
        self.actionExpand_All_Below = QtGui.QAction(AccountTreeWidget)
        self.actionExpand_All_Below.setObjectName("actionExpand_All_Below")
        self.actionShow_All = QtGui.QAction(AccountTreeWidget)
        self.actionShow_All.setObjectName("actionShow_All")
        self.actionHide_All = QtGui.QAction(AccountTreeWidget)
        self.actionHide_All.setObjectName("actionHide_All")
        self.actionShow_Selection_Only = QtGui.QAction(AccountTreeWidget)
        self.actionShow_Selection_Only.setObjectName("actionShow_Selection_Only")
        self.actionSelect_All_Cash_Accounts_Below = QtGui.QAction(AccountTreeWidget)
        self.actionSelect_All_Cash_Accounts_Below.setObjectName("actionSelect_All_Cash_Accounts_Below")
        self.actionSelect_All_Security_Accounts_Below = QtGui.QAction(AccountTreeWidget)
        self.actionSelect_All_Security_Accounts_Below.setObjectName("actionSelect_All_Security_Accounts_Below")
        self.actionShow_Securities = QtGui.QAction(AccountTreeWidget)
        self.actionShow_Securities.setObjectName("actionShow_Securities")

        self.retranslateUi(AccountTreeWidget)
        QtCore.QMetaObject.connectSlotsByName(AccountTreeWidget)

    def retranslateUi(self, AccountTreeWidget):
        _translate = QtCore.QCoreApplication.translate
        AccountTreeWidget.setWindowTitle(_translate("AccountTreeWidget", "Form"))
        self.expandAllToolButton.setText(_translate("AccountTreeWidget", "..."))
        self.collapseAllToolButton.setText(_translate("AccountTreeWidget", "..."))
        self.showAllToolButton.setText(_translate("AccountTreeWidget", "..."))
        self.hideAllToolButton.setText(_translate("AccountTreeWidget", "..."))
        self.searchLineEdit.setToolTip(_translate("AccountTreeWidget", "<html><head/><body><p>Special characters:</p><p>* matches zero or more of any characters<br/>? matches any single character<br/>[...] matches any character within square brackets</p></body></html>"))
        self.searchLineEdit.setPlaceholderText(_translate("AccountTreeWidget", "Search Accounts"))
        self.treeView.setStatusTip(_translate("AccountTreeWidget", "Account Tree: right-click to open the context menu"))
        self.totalBaseBalanceLabel.setText(_translate("AccountTreeWidget", "Total base balance:"))
        self.actionAdd_Account_Group.setText(_translate("AccountTreeWidget", "Add Account Group"))
        self.actionAdd_Security_Account.setText(_translate("AccountTreeWidget", "Add Security Account"))
        self.actionAdd_Cash_Account.setText(_translate("AccountTreeWidget", "Add Cash Account"))
        self.actionEdit.setText(_translate("AccountTreeWidget", "Edit"))
        self.actionDelete.setText(_translate("AccountTreeWidget", "Delete"))
        self.actionExpand_All.setText(_translate("AccountTreeWidget", "Expand All"))
        self.actionCollapse_All.setText(_translate("AccountTreeWidget", "Collapse All"))
        self.actionExpand_All_Below.setText(_translate("AccountTreeWidget", "Expand All Below"))
        self.actionShow_All.setText(_translate("AccountTreeWidget", "Select All"))
        self.actionShow_All.setToolTip(_translate("AccountTreeWidget", "Select All"))
        self.actionHide_All.setText(_translate("AccountTreeWidget", "Unselect All"))
        self.actionHide_All.setToolTip(_translate("AccountTreeWidget", "Unselect All"))
        self.actionShow_Selection_Only.setText(_translate("AccountTreeWidget", "Select Only This Item"))
        self.actionShow_Selection_Only.setToolTip(_translate("AccountTreeWidget", "Select Only This Item"))
        self.actionSelect_All_Cash_Accounts_Below.setText(_translate("AccountTreeWidget", "Select All Cash Accounts Below"))
        self.actionSelect_All_Security_Accounts_Below.setText(_translate("AccountTreeWidget", "Select All Security Accounts Below"))
        self.actionShow_Securities.setText(_translate("AccountTreeWidget", "Show Securities"))