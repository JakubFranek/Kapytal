# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\mainwindow.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(863, 673)
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayoutTree = QtWidgets.QVBoxLayout()
        self.verticalLayoutTree.setObjectName("verticalLayoutTree")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, 2, -1, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.toolButton_expandAll = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_expandAll.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.toolButton_expandAll.setArrowType(QtCore.Qt.ArrowType.NoArrow)
        self.toolButton_expandAll.setObjectName("toolButton_expandAll")
        self.horizontalLayout_3.addWidget(self.toolButton_expandAll)
        self.toolButton_collapseAll = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_collapseAll.setObjectName("toolButton_collapseAll")
        self.horizontalLayout_3.addWidget(self.toolButton_collapseAll)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayoutTree.addLayout(self.horizontalLayout_3)
        self.accountTree = QtWidgets.QTreeView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.accountTree.sizePolicy().hasHeightForWidth())
        self.accountTree.setSizePolicy(sizePolicy)
        self.accountTree.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.accountTree.setObjectName("accountTree")
        self.accountTree.header().setHighlightSections(True)
        self.accountTree.header().setMinimumSectionSize(35)
        self.accountTree.header().setSortIndicatorShown(False)
        self.accountTree.header().setStretchLastSection(False)
        self.verticalLayoutTree.addWidget(self.accountTree)
        self.horizontalLayout.addLayout(self.verticalLayoutTree)
        self.verticalLayoutTable = QtWidgets.QVBoxLayout()
        self.verticalLayoutTable.setObjectName("verticalLayoutTable")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.toolButton_4 = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_4.setObjectName("toolButton_4")
        self.horizontalLayout_2.addWidget(self.toolButton_4)
        self.toolButton_5 = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_5.setObjectName("toolButton_5")
        self.horizontalLayout_2.addWidget(self.toolButton_5)
        self.toolButton_6 = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_6.setObjectName("toolButton_6")
        self.horizontalLayout_2.addWidget(self.toolButton_6)
        self.toolButton_7 = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_7.setObjectName("toolButton_7")
        self.horizontalLayout_2.addWidget(self.toolButton_7)
        self.toolButton_8 = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_8.setObjectName("toolButton_8")
        self.horizontalLayout_2.addWidget(self.toolButton_8)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.toolButton = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton.setObjectName("toolButton")
        self.horizontalLayout_2.addWidget(self.toolButton)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.horizontalLayout_2.setStretch(5, 1)
        self.verticalLayoutTable.addLayout(self.horizontalLayout_2)
        self.transactionTable = QtWidgets.QTableView(self.centralwidget)
        self.transactionTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.transactionTable.setObjectName("transactionTable")
        self.verticalLayoutTable.addWidget(self.transactionTable)
        self.horizontalLayout.addLayout(self.verticalLayoutTable)
        self.horizontalLayout.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 863, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuReports = QtWidgets.QMenu(self.menubar)
        self.menuReports.setObjectName("menuReports")
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.toolBar)
        self.actionSave = QtGui.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionAdd_Account_Group = QtGui.QAction(MainWindow)
        self.actionAdd_Account_Group.setObjectName("actionAdd_Account_Group")
        self.actionSave_As = QtGui.QAction(MainWindow)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionOpen_File = QtGui.QAction(MainWindow)
        self.actionOpen_File.setObjectName("actionOpen_File")
        self.actionExpand_All = QtGui.QAction(MainWindow)
        self.actionExpand_All.setObjectName("actionExpand_All")
        self.actionExpand = QtGui.QAction(MainWindow)
        self.actionExpand.setObjectName("actionExpand")
        self.actionCollapse_All = QtGui.QAction(MainWindow)
        self.actionCollapse_All.setObjectName("actionCollapse_All")
        self.actionCollapse = QtGui.QAction(MainWindow)
        self.actionCollapse.setObjectName("actionCollapse")
        self.actionAdd_Expense = QtGui.QAction(MainWindow)
        self.actionAdd_Expense.setObjectName("actionAdd_Expense")
        self.actionAdd_Income = QtGui.QAction(MainWindow)
        self.actionAdd_Income.setObjectName("actionAdd_Income")
        self.actionAdd_Transfer = QtGui.QAction(MainWindow)
        self.actionAdd_Transfer.setObjectName("actionAdd_Transfer")
        self.actionAdd_Buy = QtGui.QAction(MainWindow)
        self.actionAdd_Buy.setObjectName("actionAdd_Buy")
        self.actionAdd_Sell = QtGui.QAction(MainWindow)
        self.actionAdd_Sell.setObjectName("actionAdd_Sell")
        self.actionAdd_Refund = QtGui.QAction(MainWindow)
        self.actionAdd_Refund.setObjectName("actionAdd_Refund")
        self.actionDuplicate_Transaction = QtGui.QAction(MainWindow)
        self.actionDuplicate_Transaction.setObjectName("actionDuplicate_Transaction")
        self.actionDelete_Account_Tree_Item = QtGui.QAction(MainWindow)
        self.actionDelete_Account_Tree_Item.setObjectName("actionDelete_Account_Tree_Item")
        self.actionDelete_Transactions = QtGui.QAction(MainWindow)
        self.actionDelete_Transactions.setObjectName("actionDelete_Transactions")
        self.actionEdit_Account_Tree_Item = QtGui.QAction(MainWindow)
        self.actionEdit_Account_Tree_Item.setObjectName("actionEdit_Account_Tree_Item")
        self.actionAdd_Cash_Account = QtGui.QAction(MainWindow)
        self.actionAdd_Cash_Account.setObjectName("actionAdd_Cash_Account")
        self.actionAdd_Security_Account = QtGui.QAction(MainWindow)
        self.actionAdd_Security_Account.setObjectName("actionAdd_Security_Account")
        self.actionExpand_All_Below = QtGui.QAction(MainWindow)
        self.actionExpand_All_Below.setObjectName("actionExpand_All_Below")
        self.menuFile.addAction(self.actionOpen_File)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuReports.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())
        self.toolBar.addAction(self.actionOpen_File)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionSave_As)
        self.toolBar.addSeparator()

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Kapytal"))
        self.toolButton_expandAll.setText(_translate("MainWindow", "Expand All"))
        self.toolButton_collapseAll.setText(_translate("MainWindow", "Collapse All"))
        self.toolButton_4.setText(_translate("MainWindow", "Expense"))
        self.toolButton_5.setText(_translate("MainWindow", "Income"))
        self.toolButton_6.setText(_translate("MainWindow", "Transfer"))
        self.toolButton_7.setText(_translate("MainWindow", "Buy"))
        self.toolButton_8.setText(_translate("MainWindow", "Sell"))
        self.toolButton.setText(_translate("MainWindow", "Filter"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "Search"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuReports.setTitle(_translate("MainWindow", "Reports"))
        self.menuAbout.setTitle(_translate("MainWindow", "About"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setToolTip(_translate("MainWindow", "Save"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionAdd_Account_Group.setText(_translate("MainWindow", "Add Account Group"))
        self.actionAdd_Account_Group.setToolTip(_translate("MainWindow", "Add Account Group"))
        self.actionSave_As.setText(_translate("MainWindow", "Save As..."))
        self.actionSave_As.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.actionOpen_File.setText(_translate("MainWindow", "Open File"))
        self.actionOpen_File.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionExpand_All.setText(_translate("MainWindow", "Expand All"))
        self.actionExpand.setText(_translate("MainWindow", "Expand"))
        self.actionCollapse_All.setText(_translate("MainWindow", "Collapse All"))
        self.actionCollapse.setText(_translate("MainWindow", "Collapse"))
        self.actionAdd_Expense.setText(_translate("MainWindow", "Add Expense"))
        self.actionAdd_Income.setText(_translate("MainWindow", "Add Income"))
        self.actionAdd_Transfer.setText(_translate("MainWindow", "Add Transfer"))
        self.actionAdd_Buy.setText(_translate("MainWindow", "Add Buy"))
        self.actionAdd_Sell.setText(_translate("MainWindow", "Add Sell"))
        self.actionAdd_Refund.setText(_translate("MainWindow", "Add Refund"))
        self.actionDuplicate_Transaction.setText(_translate("MainWindow", "Duplicate Transaction"))
        self.actionDelete_Account_Tree_Item.setText(_translate("MainWindow", "Delete"))
        self.actionDelete_Transactions.setText(_translate("MainWindow", "Delete Transaction(s)"))
        self.actionEdit_Account_Tree_Item.setText(_translate("MainWindow", "Edit"))
        self.actionAdd_Cash_Account.setText(_translate("MainWindow", "Add Cash Account"))
        self.actionAdd_Security_Account.setText(_translate("MainWindow", "Add Security Account"))
        self.actionExpand_All_Below.setText(_translate("MainWindow", "Expand All Below"))
