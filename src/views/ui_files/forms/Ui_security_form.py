# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\forms\security_form.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SecurityForm(object):
    def setupUi(self, SecurityForm):
        SecurityForm.setObjectName("SecurityForm")
        SecurityForm.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        SecurityForm.resize(700, 600)
        SecurityForm.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(SecurityForm)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(SecurityForm)
        self.tabWidget.setObjectName("tabWidget")
        self.manageSecuritiesTab = QtWidgets.QWidget()
        self.manageSecuritiesTab.setObjectName("manageSecuritiesTab")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.manageSecuritiesTab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.splitter = QtWidgets.QSplitter(self.manageSecuritiesTab)
        self.splitter.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.splitter.setChildrenCollapsible(True)
        self.splitter.setObjectName("splitter")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.securityTableVerticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.securityTableVerticalLayout.setContentsMargins(0, 0, 0, 0)
        self.securityTableVerticalLayout.setObjectName("securityTableVerticalLayout")
        self.securityControlsHorizontalLayout = QtWidgets.QHBoxLayout()
        self.securityControlsHorizontalLayout.setObjectName("securityControlsHorizontalLayout")
        self.addToolButton = QtWidgets.QToolButton(self.verticalLayoutWidget)
        self.addToolButton.setObjectName("addToolButton")
        self.securityControlsHorizontalLayout.addWidget(self.addToolButton)
        self.editToolButton = QtWidgets.QToolButton(self.verticalLayoutWidget)
        self.editToolButton.setObjectName("editToolButton")
        self.securityControlsHorizontalLayout.addWidget(self.editToolButton)
        self.removeToolButton = QtWidgets.QToolButton(self.verticalLayoutWidget)
        self.removeToolButton.setObjectName("removeToolButton")
        self.securityControlsHorizontalLayout.addWidget(self.removeToolButton)
        self.manageSearchLineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.manageSearchLineEdit.setClearButtonEnabled(True)
        self.manageSearchLineEdit.setObjectName("manageSearchLineEdit")
        self.securityControlsHorizontalLayout.addWidget(self.manageSearchLineEdit)
        self.securityTableVerticalLayout.addLayout(self.securityControlsHorizontalLayout)
        self.securityTableView = QtWidgets.QTableView(self.verticalLayoutWidget)
        self.securityTableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.securityTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.securityTableView.setSortingEnabled(True)
        self.securityTableView.setObjectName("securityTableView")
        self.securityTableView.horizontalHeader().setHighlightSections(False)
        self.securityTableView.horizontalHeader().setStretchLastSection(True)
        self.securityTableView.verticalHeader().setVisible(False)
        self.securityTableVerticalLayout.addWidget(self.securityTableView)
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.securityPriceHorizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.securityPriceHorizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.securityPriceHorizontalLayout.setObjectName("securityPriceHorizontalLayout")
        self.securityPriceVerticalLayout = QtWidgets.QVBoxLayout()
        self.securityPriceVerticalLayout.setObjectName("securityPriceVerticalLayout")
        self.securityPriceControlsHorizontalLayout = QtWidgets.QHBoxLayout()
        self.securityPriceControlsHorizontalLayout.setObjectName("securityPriceControlsHorizontalLayout")
        self.addPriceToolButton = QtWidgets.QToolButton(self.layoutWidget)
        self.addPriceToolButton.setObjectName("addPriceToolButton")
        self.securityPriceControlsHorizontalLayout.addWidget(self.addPriceToolButton)
        self.editPriceToolButton = QtWidgets.QToolButton(self.layoutWidget)
        self.editPriceToolButton.setObjectName("editPriceToolButton")
        self.securityPriceControlsHorizontalLayout.addWidget(self.editPriceToolButton)
        self.removePriceToolButton = QtWidgets.QToolButton(self.layoutWidget)
        self.removePriceToolButton.setObjectName("removePriceToolButton")
        self.securityPriceControlsHorizontalLayout.addWidget(self.removePriceToolButton)
        self.loadPriceDataToolButton = QtWidgets.QToolButton(self.layoutWidget)
        self.loadPriceDataToolButton.setObjectName("loadPriceDataToolButton")
        self.securityPriceControlsHorizontalLayout.addWidget(self.loadPriceDataToolButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.securityPriceControlsHorizontalLayout.addItem(spacerItem)
        self.securityPriceVerticalLayout.addLayout(self.securityPriceControlsHorizontalLayout)
        self.securityPriceTableView = QtWidgets.QTableView(self.layoutWidget)
        self.securityPriceTableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.securityPriceTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.securityPriceTableView.setSortingEnabled(True)
        self.securityPriceTableView.setObjectName("securityPriceTableView")
        self.securityPriceTableView.horizontalHeader().setHighlightSections(False)
        self.securityPriceTableView.verticalHeader().setVisible(False)
        self.securityPriceTableView.verticalHeader().setHighlightSections(False)
        self.securityPriceVerticalLayout.addWidget(self.securityPriceTableView)
        self.securityPriceHorizontalLayout.addLayout(self.securityPriceVerticalLayout)
        self.verticalLayout_4.addWidget(self.splitter)
        self.tabWidget.addTab(self.manageSecuritiesTab, "")
        self.securitiesOverviewTab = QtWidgets.QWidget()
        self.securitiesOverviewTab.setObjectName("securitiesOverviewTab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.securitiesOverviewTab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.overviewControlsHorizontalLayout = QtWidgets.QHBoxLayout()
        self.overviewControlsHorizontalLayout.setObjectName("overviewControlsHorizontalLayout")
        self.expandAllToolButton = QtWidgets.QToolButton(self.securitiesOverviewTab)
        self.expandAllToolButton.setObjectName("expandAllToolButton")
        self.overviewControlsHorizontalLayout.addWidget(self.expandAllToolButton)
        self.collapseAllToolButton = QtWidgets.QToolButton(self.securitiesOverviewTab)
        self.collapseAllToolButton.setObjectName("collapseAllToolButton")
        self.overviewControlsHorizontalLayout.addWidget(self.collapseAllToolButton)
        self.overviewSearchLineEdit = QtWidgets.QLineEdit(self.securitiesOverviewTab)
        self.overviewSearchLineEdit.setObjectName("overviewSearchLineEdit")
        self.overviewControlsHorizontalLayout.addWidget(self.overviewSearchLineEdit)
        self.verticalLayout.addLayout(self.overviewControlsHorizontalLayout)
        self.treeView = QtWidgets.QTreeView(self.securitiesOverviewTab)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setSortingEnabled(True)
        self.treeView.setObjectName("treeView")
        self.verticalLayout.addWidget(self.treeView)
        self.tabWidget.addTab(self.securitiesOverviewTab, "")
        self.verticalLayout_2.addWidget(self.tabWidget)
        self.actionAdd_Security = QtGui.QAction(SecurityForm)
        self.actionAdd_Security.setObjectName("actionAdd_Security")
        self.actionEdit_Security = QtGui.QAction(SecurityForm)
        self.actionEdit_Security.setObjectName("actionEdit_Security")
        self.actionRemove_Security = QtGui.QAction(SecurityForm)
        self.actionRemove_Security.setObjectName("actionRemove_Security")
        self.actionExpand_All = QtGui.QAction(SecurityForm)
        self.actionExpand_All.setObjectName("actionExpand_All")
        self.actionCollapse_All = QtGui.QAction(SecurityForm)
        self.actionCollapse_All.setObjectName("actionCollapse_All")
        self.actionAdd_Price = QtGui.QAction(SecurityForm)
        self.actionAdd_Price.setObjectName("actionAdd_Price")
        self.actionEdit_Price = QtGui.QAction(SecurityForm)
        self.actionEdit_Price.setObjectName("actionEdit_Price")
        self.actionRemove_Price = QtGui.QAction(SecurityForm)
        self.actionRemove_Price.setObjectName("actionRemove_Price")
        self.actionLoad_Price_Data = QtGui.QAction(SecurityForm)
        self.actionLoad_Price_Data.setObjectName("actionLoad_Price_Data")

        self.retranslateUi(SecurityForm)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(SecurityForm)

    def retranslateUi(self, SecurityForm):
        _translate = QtCore.QCoreApplication.translate
        SecurityForm.setWindowTitle(_translate("SecurityForm", "Securities"))
        self.addToolButton.setText(_translate("SecurityForm", "..."))
        self.editToolButton.setText(_translate("SecurityForm", "..."))
        self.removeToolButton.setText(_translate("SecurityForm", "..."))
        self.manageSearchLineEdit.setToolTip(_translate("SecurityForm", "<html><head/><body><p>Special characters:</p><p>* matches zero or more of any characters<br/>? matches any single character<br/>[...] matches any character within square brackets</p></body></html>"))
        self.manageSearchLineEdit.setPlaceholderText(_translate("SecurityForm", "Search Securities"))
        self.addPriceToolButton.setText(_translate("SecurityForm", "..."))
        self.editPriceToolButton.setText(_translate("SecurityForm", "..."))
        self.removePriceToolButton.setText(_translate("SecurityForm", "..."))
        self.loadPriceDataToolButton.setText(_translate("SecurityForm", "..."))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.manageSecuritiesTab), _translate("SecurityForm", "Manage"))
        self.expandAllToolButton.setText(_translate("SecurityForm", "..."))
        self.collapseAllToolButton.setText(_translate("SecurityForm", "..."))
        self.overviewSearchLineEdit.setPlaceholderText(_translate("SecurityForm", "Search"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.securitiesOverviewTab), _translate("SecurityForm", "Overview"))
        self.actionAdd_Security.setText(_translate("SecurityForm", "Add Security"))
        self.actionEdit_Security.setText(_translate("SecurityForm", "Edit Security"))
        self.actionRemove_Security.setText(_translate("SecurityForm", "Remove Security"))
        self.actionExpand_All.setText(_translate("SecurityForm", "Expand All"))
        self.actionCollapse_All.setText(_translate("SecurityForm", "Collapse All"))
        self.actionAdd_Price.setText(_translate("SecurityForm", "Add Price"))
        self.actionEdit_Price.setText(_translate("SecurityForm", "Edit Price"))
        self.actionRemove_Price.setText(_translate("SecurityForm", "Remove Price"))
        self.actionLoad_Price_Data.setText(_translate("SecurityForm", "Load Price Data"))
