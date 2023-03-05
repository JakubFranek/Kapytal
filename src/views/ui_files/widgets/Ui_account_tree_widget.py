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
        self.verticalLine_2 = QtWidgets.QFrame(AccountTreeWidget)
        self.verticalLine_2.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.verticalLine_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.verticalLine_2.setObjectName("verticalLine_2")
        self.controlsHorizontalLayout.addWidget(self.verticalLine_2)
        self.addAccountGroupToolButton = QtWidgets.QToolButton(AccountTreeWidget)
        self.addAccountGroupToolButton.setObjectName("addAccountGroupToolButton")
        self.controlsHorizontalLayout.addWidget(self.addAccountGroupToolButton)
        self.addCashAccountToolButton = QtWidgets.QToolButton(AccountTreeWidget)
        self.addCashAccountToolButton.setObjectName("addCashAccountToolButton")
        self.controlsHorizontalLayout.addWidget(self.addCashAccountToolButton)
        self.addSecurityAccountToolButton = QtWidgets.QToolButton(AccountTreeWidget)
        self.addSecurityAccountToolButton.setObjectName("addSecurityAccountToolButton")
        self.controlsHorizontalLayout.addWidget(self.addSecurityAccountToolButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.controlsHorizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.controlsHorizontalLayout)
        self.treeView = QtWidgets.QTreeView(AccountTreeWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeView.sizePolicy().hasHeightForWidth())
        self.treeView.setSizePolicy(sizePolicy)
        self.treeView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.treeView.setObjectName("treeView")
        self.treeView.header().setHighlightSections(True)
        self.treeView.header().setMinimumSectionSize(20)
        self.treeView.header().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.treeView)
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

        self.retranslateUi(AccountTreeWidget)
        QtCore.QMetaObject.connectSlotsByName(AccountTreeWidget)

    def retranslateUi(self, AccountTreeWidget):
        _translate = QtCore.QCoreApplication.translate
        AccountTreeWidget.setWindowTitle(_translate("AccountTreeWidget", "Form"))
        self.expandAllToolButton.setText(_translate("AccountTreeWidget", "..."))
        self.collapseAllToolButton.setText(_translate("AccountTreeWidget", "..."))
        self.showAllToolButton.setText(_translate("AccountTreeWidget", "..."))
        self.hideAllToolButton.setText(_translate("AccountTreeWidget", "..."))
        self.addAccountGroupToolButton.setText(_translate("AccountTreeWidget", "..."))
        self.addCashAccountToolButton.setText(_translate("AccountTreeWidget", "..."))
        self.addSecurityAccountToolButton.setText(_translate("AccountTreeWidget", "..."))
        self.treeView.setStatusTip(_translate("AccountTreeWidget", "Account Tree: right-click to open the context menu"))
        self.actionAdd_Account_Group.setText(_translate("AccountTreeWidget", "Add Account Group"))
        self.actionAdd_Security_Account.setText(_translate("AccountTreeWidget", "Add Security Account"))
        self.actionAdd_Cash_Account.setText(_translate("AccountTreeWidget", "Add Cash Account"))
        self.actionEdit.setText(_translate("AccountTreeWidget", "Edit"))
        self.actionDelete.setText(_translate("AccountTreeWidget", "Delete"))
        self.actionExpand_All.setText(_translate("AccountTreeWidget", "Expand All"))
        self.actionCollapse_All.setText(_translate("AccountTreeWidget", "Collapse All"))
        self.actionExpand_All_Below.setText(_translate("AccountTreeWidget", "Expand All Below"))
        self.actionShow_All.setText(_translate("AccountTreeWidget", "Show All"))
        self.actionHide_All.setText(_translate("AccountTreeWidget", "Hide All"))
        self.actionShow_Selection_Only.setText(_translate("AccountTreeWidget", "Show Selection Only"))
