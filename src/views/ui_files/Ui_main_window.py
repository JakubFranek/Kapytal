# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\main_window.ui'
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
        self.treeControlsHorizontalLayout = QtWidgets.QHBoxLayout()
        self.treeControlsHorizontalLayout.setContentsMargins(-1, 2, -1, 0)
        self.treeControlsHorizontalLayout.setObjectName("treeControlsHorizontalLayout")
        self.expandAllToolButton = QtWidgets.QToolButton(self.centralwidget)
        self.expandAllToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.expandAllToolButton.setArrowType(QtCore.Qt.ArrowType.NoArrow)
        self.expandAllToolButton.setObjectName("expandAllToolButton")
        self.treeControlsHorizontalLayout.addWidget(self.expandAllToolButton)
        self.collapseAllToolButton = QtWidgets.QToolButton(self.centralwidget)
        self.collapseAllToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.collapseAllToolButton.setObjectName("collapseAllToolButton")
        self.treeControlsHorizontalLayout.addWidget(self.collapseAllToolButton)
        self.addAccountGroupToolButton = QtWidgets.QToolButton(self.centralwidget)
        self.addAccountGroupToolButton.setObjectName("addAccountGroupToolButton")
        self.treeControlsHorizontalLayout.addWidget(self.addAccountGroupToolButton)
        self.addCashAccountToolButton = QtWidgets.QToolButton(self.centralwidget)
        self.addCashAccountToolButton.setObjectName("addCashAccountToolButton")
        self.treeControlsHorizontalLayout.addWidget(self.addCashAccountToolButton)
        self.addSecurityAccountToolButton = QtWidgets.QToolButton(self.centralwidget)
        self.addSecurityAccountToolButton.setObjectName("addSecurityAccountToolButton")
        self.treeControlsHorizontalLayout.addWidget(self.addSecurityAccountToolButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.treeControlsHorizontalLayout.addItem(spacerItem)
        self.verticalLayoutTree.addLayout(self.treeControlsHorizontalLayout)
        self.horizontalLayout.addLayout(self.verticalLayoutTree)
        self.verticalLayoutTable = QtWidgets.QVBoxLayout()
        self.verticalLayoutTable.setObjectName("verticalLayoutTable")
        self.tableControlsHorizontalLayout = QtWidgets.QHBoxLayout()
        self.tableControlsHorizontalLayout.setObjectName("tableControlsHorizontalLayout")
        self.incomeToolButton = QtWidgets.QToolButton(self.centralwidget)
        self.incomeToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.incomeToolButton.setObjectName("incomeToolButton")
        self.tableControlsHorizontalLayout.addWidget(self.incomeToolButton)
        self.expenseToolButton = QtWidgets.QToolButton(self.centralwidget)
        self.expenseToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.expenseToolButton.setObjectName("expenseToolButton")
        self.tableControlsHorizontalLayout.addWidget(self.expenseToolButton)
        self.transferToolButton = QtWidgets.QToolButton(self.centralwidget)
        self.transferToolButton.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.transferToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.transferToolButton.setArrowType(QtCore.Qt.ArrowType.NoArrow)
        self.transferToolButton.setObjectName("transferToolButton")
        self.tableControlsHorizontalLayout.addWidget(self.transferToolButton)
        self.buyToolButton = QtWidgets.QToolButton(self.centralwidget)
        self.buyToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.buyToolButton.setObjectName("buyToolButton")
        self.tableControlsHorizontalLayout.addWidget(self.buyToolButton)
        self.sellToolButton = QtWidgets.QToolButton(self.centralwidget)
        self.sellToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.sellToolButton.setObjectName("sellToolButton")
        self.tableControlsHorizontalLayout.addWidget(self.sellToolButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.tableControlsHorizontalLayout.addItem(spacerItem1)
        self.filterToolButton = QtWidgets.QToolButton(self.centralwidget)
        self.filterToolButton.setObjectName("filterToolButton")
        self.tableControlsHorizontalLayout.addWidget(self.filterToolButton)
        self.searchLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.searchLineEdit.sizePolicy().hasHeightForWidth())
        self.searchLineEdit.setSizePolicy(sizePolicy)
        self.searchLineEdit.setMaximumSize(QtCore.QSize(155, 16777215))
        self.searchLineEdit.setClearButtonEnabled(True)
        self.searchLineEdit.setObjectName("searchLineEdit")
        self.tableControlsHorizontalLayout.addWidget(self.searchLineEdit)
        self.tableControlsHorizontalLayout.setStretch(5, 1)
        self.verticalLayoutTable.addLayout(self.tableControlsHorizontalLayout)
        self.horizontalLayout.addLayout(self.verticalLayoutTable)
        self.horizontalLayout.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 863, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuRecent_Files = QtWidgets.QMenu(self.menuFile)
        self.menuRecent_Files.setObjectName("menuRecent_Files")
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
        self.actionSave_As = QtGui.QAction(MainWindow)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionOpen_File = QtGui.QAction(MainWindow)
        self.actionOpen_File.setObjectName("actionOpen_File")
        self.actionExpense = QtGui.QAction(MainWindow)
        self.actionExpense.setObjectName("actionExpense")
        self.actionIncome = QtGui.QAction(MainWindow)
        self.actionIncome.setObjectName("actionIncome")
        self.actionTransfer = QtGui.QAction(MainWindow)
        self.actionTransfer.setObjectName("actionTransfer")
        self.actionBuy = QtGui.QAction(MainWindow)
        self.actionBuy.setObjectName("actionBuy")
        self.actionSell = QtGui.QAction(MainWindow)
        self.actionSell.setObjectName("actionSell")
        self.actionRefund = QtGui.QAction(MainWindow)
        self.actionRefund.setObjectName("actionRefund")
        self.actionDuplicate_Transaction = QtGui.QAction(MainWindow)
        self.actionDuplicate_Transaction.setObjectName("actionDuplicate_Transaction")
        self.actionDelete_Transactions = QtGui.QAction(MainWindow)
        self.actionDelete_Transactions.setObjectName("actionDelete_Transactions")
        self.actionCurrencies_and_Exchange_Rates = QtGui.QAction(MainWindow)
        self.actionCurrencies_and_Exchange_Rates.setObjectName("actionCurrencies_and_Exchange_Rates")
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionSecurities = QtGui.QAction(MainWindow)
        self.actionSecurities.setObjectName("actionSecurities")
        self.actionPayees = QtGui.QAction(MainWindow)
        self.actionPayees.setObjectName("actionPayees")
        self.actionCategories = QtGui.QAction(MainWindow)
        self.actionCategories.setObjectName("actionCategories")
        self.actionTags = QtGui.QAction(MainWindow)
        self.actionTags.setObjectName("actionTags")
        self.actionSettings = QtGui.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.actionCashTransfer = QtGui.QAction(MainWindow)
        self.actionCashTransfer.setObjectName("actionCashTransfer")
        self.actionSecurityTransfer = QtGui.QAction(MainWindow)
        self.actionSecurityTransfer.setObjectName("actionSecurityTransfer")
        self.actionClose_File = QtGui.QAction(MainWindow)
        self.actionClose_File.setObjectName("actionClose_File")
        self.actionClear_Recent_File_Menu = QtGui.QAction(MainWindow)
        self.actionClear_Recent_File_Menu.setObjectName("actionClear_Recent_File_Menu")
        self.menuRecent_Files.addSeparator()
        self.menuRecent_Files.addAction(self.actionClear_Recent_File_Menu)
        self.menuFile.addAction(self.actionOpen_File)
        self.menuFile.addAction(self.menuRecent_Files.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose_File)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuEdit.addAction(self.actionCurrencies_and_Exchange_Rates)
        self.menuEdit.addAction(self.actionSecurities)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionPayees)
        self.menuEdit.addAction(self.actionCategories)
        self.menuEdit.addAction(self.actionTags)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionSettings)
        self.menuAbout.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuReports.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())
        self.toolBar.addAction(self.actionOpen_File)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionSave_As)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionCurrencies_and_Exchange_Rates)
        self.toolBar.addAction(self.actionSecurities)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionCategories)
        self.toolBar.addAction(self.actionPayees)
        self.toolBar.addAction(self.actionTags)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionSettings)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Kapytal"))
        self.expandAllToolButton.setText(_translate("MainWindow", "..."))
        self.collapseAllToolButton.setText(_translate("MainWindow", "..."))
        self.addAccountGroupToolButton.setText(_translate("MainWindow", "..."))
        self.addCashAccountToolButton.setText(_translate("MainWindow", "..."))
        self.addSecurityAccountToolButton.setText(_translate("MainWindow", "..."))
        self.incomeToolButton.setText(_translate("MainWindow", "Income"))
        self.expenseToolButton.setText(_translate("MainWindow", "Expense"))
        self.transferToolButton.setText(_translate("MainWindow", "Transfer"))
        self.buyToolButton.setText(_translate("MainWindow", "Buy"))
        self.sellToolButton.setText(_translate("MainWindow", "Sell"))
        self.filterToolButton.setText(_translate("MainWindow", "Filter"))
        self.searchLineEdit.setPlaceholderText(_translate("MainWindow", "Search"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuRecent_Files.setTitle(_translate("MainWindow", "Recent Files"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuReports.setTitle(_translate("MainWindow", "Reports"))
        self.menuAbout.setTitle(_translate("MainWindow", "Help"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setToolTip(_translate("MainWindow", "Save"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSave_As.setText(_translate("MainWindow", "Save As..."))
        self.actionSave_As.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.actionOpen_File.setText(_translate("MainWindow", "Open File"))
        self.actionOpen_File.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionExpense.setText(_translate("MainWindow", "Expense"))
        self.actionIncome.setText(_translate("MainWindow", "Income"))
        self.actionTransfer.setText(_translate("MainWindow", "Transfer"))
        self.actionBuy.setText(_translate("MainWindow", "Buy"))
        self.actionSell.setText(_translate("MainWindow", "Sell"))
        self.actionRefund.setText(_translate("MainWindow", "Refund"))
        self.actionDuplicate_Transaction.setText(_translate("MainWindow", "Duplicate Transaction"))
        self.actionDelete_Transactions.setText(_translate("MainWindow", "Delete Transaction(s)"))
        self.actionCurrencies_and_Exchange_Rates.setText(_translate("MainWindow", "Currencies and Exchange Rates"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionSecurities.setText(_translate("MainWindow", "Securities"))
        self.actionPayees.setText(_translate("MainWindow", "Payees"))
        self.actionCategories.setText(_translate("MainWindow", "Categories"))
        self.actionTags.setText(_translate("MainWindow", "Tags"))
        self.actionSettings.setText(_translate("MainWindow", "Settings"))
        self.actionCashTransfer.setText(_translate("MainWindow", "Cash Transfer"))
        self.actionSecurityTransfer.setText(_translate("MainWindow", "Security Transfer"))
        self.actionSecurityTransfer.setToolTip(_translate("MainWindow", "Security Transfer"))
        self.actionClose_File.setText(_translate("MainWindow", "Close File"))
        self.actionClear_Recent_File_Menu.setText(_translate("MainWindow", "Clear Menu"))
