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
        self.menuCash_Flow = QtWidgets.QMenu(self.menuReports)
        self.menuCash_Flow.setObjectName("menuCash_Flow")
        self.menuNet_Worth = QtWidgets.QMenu(self.menuReports)
        self.menuNet_Worth.setObjectName("menuNet_Worth")
        self.menuCategories = QtWidgets.QMenu(self.menuReports)
        self.menuCategories.setObjectName("menuCategories")
        self.menuTags = QtWidgets.QMenu(self.menuReports)
        self.menuTags.setObjectName("menuTags")
        self.menuPayees = QtWidgets.QMenu(self.menuReports)
        self.menuPayees.setObjectName("menuPayees")
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
        self.actionClose_File = QtGui.QAction(MainWindow)
        self.actionClose_File.setObjectName("actionClose_File")
        self.actionClear_Recent_File_Menu = QtGui.QAction(MainWindow)
        self.actionClear_Recent_File_Menu.setObjectName("actionClear_Recent_File_Menu")
        self.actionShow_Hide_Account_Tree = QtGui.QAction(MainWindow)
        self.actionShow_Hide_Account_Tree.setObjectName("actionShow_Hide_Account_Tree")
        self.actionCash_Flow_Monthly = QtGui.QAction(MainWindow)
        self.actionCash_Flow_Monthly.setObjectName("actionCash_Flow_Monthly")
        self.actionCash_Flow_Annual = QtGui.QAction(MainWindow)
        self.actionCash_Flow_Annual.setObjectName("actionCash_Flow_Annual")
        self.actionCash_Flow_Total = QtGui.QAction(MainWindow)
        self.actionCash_Flow_Total.setObjectName("actionCash_Flow_Total")
        self.actionNet_Worth_Accounts_Report = QtGui.QAction(MainWindow)
        self.actionNet_Worth_Accounts_Report.setObjectName("actionNet_Worth_Accounts_Report")
        self.actionNet_Worth_Asset_Type_Report = QtGui.QAction(MainWindow)
        self.actionNet_Worth_Asset_Type_Report.setObjectName("actionNet_Worth_Asset_Type_Report")
        self.actionCategory_Report_Total = QtGui.QAction(MainWindow)
        self.actionCategory_Report_Total.setObjectName("actionCategory_Report_Total")
        self.actionCategory_Report_Average_Per_Month = QtGui.QAction(MainWindow)
        self.actionCategory_Report_Average_Per_Month.setObjectName("actionCategory_Report_Average_Per_Month")
        self.actionNet_Worth_Time_Report = QtGui.QAction(MainWindow)
        self.actionNet_Worth_Time_Report.setObjectName("actionNet_Worth_Time_Report")
        self.actionTag_Report_Total = QtGui.QAction(MainWindow)
        self.actionTag_Report_Total.setObjectName("actionTag_Report_Total")
        self.actionTag_Report_Average_Per_Month = QtGui.QAction(MainWindow)
        self.actionTag_Report_Average_Per_Month.setObjectName("actionTag_Report_Average_Per_Month")
        self.actionPayee_Report_Total = QtGui.QAction(MainWindow)
        self.actionPayee_Report_Total.setObjectName("actionPayee_Report_Total")
        self.actionPayee_Report_Average_Per_Month = QtGui.QAction(MainWindow)
        self.actionPayee_Report_Average_Per_Month.setObjectName("actionPayee_Report_Average_Per_Month")
        self.actionCategory_Report_Monthly = QtGui.QAction(MainWindow)
        self.actionCategory_Report_Monthly.setObjectName("actionCategory_Report_Monthly")
        self.actionCategory_Report_Annual = QtGui.QAction(MainWindow)
        self.actionCategory_Report_Annual.setObjectName("actionCategory_Report_Annual")
        self.actionTag_Report_Monthly = QtGui.QAction(MainWindow)
        self.actionTag_Report_Monthly.setObjectName("actionTag_Report_Monthly")
        self.actionTag_Report_Annual = QtGui.QAction(MainWindow)
        self.actionTag_Report_Annual.setObjectName("actionTag_Report_Annual")
        self.actionPayee_Report_Monthly = QtGui.QAction(MainWindow)
        self.actionPayee_Report_Monthly.setObjectName("actionPayee_Report_Monthly")
        self.actionPayee_Report_Annual = QtGui.QAction(MainWindow)
        self.actionPayee_Report_Annual.setObjectName("actionPayee_Report_Annual")
        self.actionShow_Hide_Transaction_Table = QtGui.QAction(MainWindow)
        self.actionShow_Hide_Transaction_Table.setObjectName("actionShow_Hide_Transaction_Table")
        self.actionOpen_Demo_File = QtGui.QAction(MainWindow)
        self.actionOpen_Demo_File.setObjectName("actionOpen_Demo_File")
        self.menuRecent_Files.addSeparator()
        self.menuRecent_Files.addAction(self.actionClear_Recent_File_Menu)
        self.menuFile.addAction(self.actionOpen_File)
        self.menuFile.addAction(self.menuRecent_Files.menuAction())
        self.menuFile.addAction(self.actionOpen_Demo_File)
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
        self.menuEdit.addAction(self.actionCategories)
        self.menuEdit.addAction(self.actionTags)
        self.menuEdit.addAction(self.actionPayees)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionSettings)
        self.menuCash_Flow.addAction(self.actionCash_Flow_Monthly)
        self.menuCash_Flow.addAction(self.actionCash_Flow_Annual)
        self.menuCash_Flow.addAction(self.actionCash_Flow_Total)
        self.menuNet_Worth.addAction(self.actionNet_Worth_Accounts_Report)
        self.menuNet_Worth.addAction(self.actionNet_Worth_Asset_Type_Report)
        self.menuNet_Worth.addAction(self.actionNet_Worth_Time_Report)
        self.menuCategories.addAction(self.actionCategory_Report_Monthly)
        self.menuCategories.addAction(self.actionCategory_Report_Annual)
        self.menuTags.addAction(self.actionTag_Report_Monthly)
        self.menuTags.addAction(self.actionTag_Report_Annual)
        self.menuPayees.addAction(self.actionPayee_Report_Monthly)
        self.menuPayees.addAction(self.actionPayee_Report_Annual)
        self.menuReports.addAction(self.menuNet_Worth.menuAction())
        self.menuReports.addAction(self.menuCash_Flow.menuAction())
        self.menuReports.addSeparator()
        self.menuReports.addAction(self.menuCategories.menuAction())
        self.menuReports.addAction(self.menuTags.menuAction())
        self.menuReports.addAction(self.menuPayees.menuAction())
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
        self.toolBar.addAction(self.actionTags)
        self.toolBar.addAction(self.actionPayees)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionSettings)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionShow_Hide_Account_Tree)
        self.toolBar.addAction(self.actionShow_Hide_Transaction_Table)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Kapytal"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuRecent_Files.setTitle(_translate("MainWindow", "Recent Files"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuReports.setTitle(_translate("MainWindow", "Reports"))
        self.menuCash_Flow.setTitle(_translate("MainWindow", "Cash Flow"))
        self.menuNet_Worth.setTitle(_translate("MainWindow", "Net Worth"))
        self.menuCategories.setTitle(_translate("MainWindow", "Categories"))
        self.menuTags.setTitle(_translate("MainWindow", "Tags"))
        self.menuPayees.setTitle(_translate("MainWindow", "Payees"))
        self.menuAbout.setTitle(_translate("MainWindow", "Help"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setToolTip(_translate("MainWindow", "Save"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSave_As.setText(_translate("MainWindow", "Save As..."))
        self.actionSave_As.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.actionOpen_File.setText(_translate("MainWindow", "Open File"))
        self.actionOpen_File.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionCurrencies_and_Exchange_Rates.setText(_translate("MainWindow", "Currencies and Exchange Rates"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionSecurities.setText(_translate("MainWindow", "Securities"))
        self.actionPayees.setText(_translate("MainWindow", "Payees"))
        self.actionCategories.setText(_translate("MainWindow", "Categories"))
        self.actionTags.setText(_translate("MainWindow", "Tags"))
        self.actionSettings.setText(_translate("MainWindow", "Settings"))
        self.actionClose_File.setText(_translate("MainWindow", "Close File"))
        self.actionClear_Recent_File_Menu.setText(_translate("MainWindow", "Clear Menu"))
        self.actionShow_Hide_Account_Tree.setText(_translate("MainWindow", "Show/Hide Account Tree"))
        self.actionCash_Flow_Monthly.setText(_translate("MainWindow", "Monthly"))
        self.actionCash_Flow_Annual.setText(_translate("MainWindow", "Annual"))
        self.actionCash_Flow_Total.setText(_translate("MainWindow", "Total"))
        self.actionNet_Worth_Accounts_Report.setText(_translate("MainWindow", "Accounts"))
        self.actionNet_Worth_Asset_Type_Report.setText(_translate("MainWindow", "Asset Type"))
        self.actionCategory_Report_Total.setText(_translate("MainWindow", "Total"))
        self.actionCategory_Report_Average_Per_Month.setText(_translate("MainWindow", "Average per month"))
        self.actionNet_Worth_Time_Report.setText(_translate("MainWindow", "Time"))
        self.actionTag_Report_Total.setText(_translate("MainWindow", "Total"))
        self.actionTag_Report_Average_Per_Month.setText(_translate("MainWindow", "Average per month"))
        self.actionPayee_Report_Total.setText(_translate("MainWindow", "Total"))
        self.actionPayee_Report_Average_Per_Month.setText(_translate("MainWindow", "Average per month"))
        self.actionCategory_Report_Monthly.setText(_translate("MainWindow", "Monthly"))
        self.actionCategory_Report_Annual.setText(_translate("MainWindow", "Annual"))
        self.actionTag_Report_Monthly.setText(_translate("MainWindow", "Monthly"))
        self.actionTag_Report_Annual.setText(_translate("MainWindow", "Annual"))
        self.actionPayee_Report_Monthly.setText(_translate("MainWindow", "Monthly"))
        self.actionPayee_Report_Annual.setText(_translate("MainWindow", "Annual"))
        self.actionShow_Hide_Transaction_Table.setText(_translate("MainWindow", "Show/Hide Transaction Table"))
        self.actionOpen_Demo_File.setText(_translate("MainWindow", "Open Demo File"))
