# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\reports\category_report.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_CategoryReport(object):
    def setupUi(self, CategoryReport):
        CategoryReport.setObjectName("CategoryReport")
        CategoryReport.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        CategoryReport.resize(800, 600)
        CategoryReport.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.horizontalLayout = QtWidgets.QHBoxLayout(CategoryReport)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtWidgets.QSplitter(CategoryReport)
        self.splitter.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.splitter.setLineWidth(1)
        self.splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeControlsHorizontalLayout = QtWidgets.QHBoxLayout()
        self.treeControlsHorizontalLayout.setObjectName("treeControlsHorizontalLayout")
        self.expandAllToolButton = QtWidgets.QToolButton(self.layoutWidget)
        self.expandAllToolButton.setObjectName("expandAllToolButton")
        self.treeControlsHorizontalLayout.addWidget(self.expandAllToolButton)
        self.collapseAllToolButton = QtWidgets.QToolButton(self.layoutWidget)
        self.collapseAllToolButton.setObjectName("collapseAllToolButton")
        self.treeControlsHorizontalLayout.addWidget(self.collapseAllToolButton)
        self.line = QtWidgets.QFrame(self.layoutWidget)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.treeControlsHorizontalLayout.addWidget(self.line)
        self.hidePeriodsToolButton = QtWidgets.QToolButton(self.layoutWidget)
        self.hidePeriodsToolButton.setObjectName("hidePeriodsToolButton")
        self.treeControlsHorizontalLayout.addWidget(self.hidePeriodsToolButton)
        self.line_2 = QtWidgets.QFrame(self.layoutWidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.treeControlsHorizontalLayout.addWidget(self.line_2)
        self.recalculateToolButton = QtWidgets.QToolButton(self.layoutWidget)
        self.recalculateToolButton.setObjectName("recalculateToolButton")
        self.treeControlsHorizontalLayout.addWidget(self.recalculateToolButton)
        self.currencyNoteLabel = QtWidgets.QLabel(self.layoutWidget)
        self.currencyNoteLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.currencyNoteLabel.setObjectName("currencyNoteLabel")
        self.treeControlsHorizontalLayout.addWidget(self.currencyNoteLabel)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.treeControlsHorizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.treeControlsHorizontalLayout)
        self.treeView = QtWidgets.QTreeView(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeView.sizePolicy().hasHeightForWidth())
        self.treeView.setSizePolicy(sizePolicy)
        self.treeView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.treeView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setSortingEnabled(True)
        self.treeView.setObjectName("treeView")
        self.treeView.header().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.treeView)
        self.horizontalLayout.addWidget(self.splitter)
        self.actionExpand_All = QtGui.QAction(CategoryReport)
        self.actionExpand_All.setObjectName("actionExpand_All")
        self.actionCollapse_All = QtGui.QAction(CategoryReport)
        self.actionCollapse_All.setObjectName("actionCollapse_All")
        self.actionShow_Hide_Period_Columns = QtGui.QAction(CategoryReport)
        self.actionShow_Hide_Period_Columns.setObjectName("actionShow_Hide_Period_Columns")
        self.actionShow_Transactions = QtGui.QAction(CategoryReport)
        self.actionShow_Transactions.setObjectName("actionShow_Transactions")
        self.actionRecalculate_Report = QtGui.QAction(CategoryReport)
        self.actionRecalculate_Report.setObjectName("actionRecalculate_Report")

        self.retranslateUi(CategoryReport)
        QtCore.QMetaObject.connectSlotsByName(CategoryReport)

    def retranslateUi(self, CategoryReport):
        _translate = QtCore.QCoreApplication.translate
        CategoryReport.setWindowTitle(_translate("CategoryReport", "Category Report"))
        self.expandAllToolButton.setText(_translate("CategoryReport", "..."))
        self.collapseAllToolButton.setText(_translate("CategoryReport", "..."))
        self.hidePeriodsToolButton.setText(_translate("CategoryReport", "..."))
        self.recalculateToolButton.setText(_translate("CategoryReport", "..."))
        self.currencyNoteLabel.setText(_translate("CategoryReport", "All values in XXX"))
        self.actionExpand_All.setText(_translate("CategoryReport", "Expand All"))
        self.actionCollapse_All.setText(_translate("CategoryReport", "Collapse All"))
        self.actionShow_Hide_Period_Columns.setText(_translate("CategoryReport", "Show/Hide Period Columns"))
        self.actionShow_Hide_Period_Columns.setToolTip(_translate("CategoryReport", "Show/Hide Period Columns"))
        self.actionShow_Transactions.setText(_translate("CategoryReport", "Show Transactions"))
        self.actionRecalculate_Report.setText(_translate("CategoryReport", "Recalculate Report"))
