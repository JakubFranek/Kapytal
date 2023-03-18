# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\dialogs\cash_transaction_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_CashTransactionDialog(object):
    def setupUi(self, CashTransactionDialog):
        CashTransactionDialog.setObjectName("CashTransactionDialog")
        CashTransactionDialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        CashTransactionDialog.resize(253, 279)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CashTransactionDialog.sizePolicy().hasHeightForWidth())
        CashTransactionDialog.setSizePolicy(sizePolicy)
        CashTransactionDialog.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.verticalLayout = QtWidgets.QVBoxLayout(CashTransactionDialog)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.typeLabel = QtWidgets.QLabel(CashTransactionDialog)
        self.typeLabel.setObjectName("typeLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.typeLabel)
        self.radioButtonHorizontalLayout = QtWidgets.QHBoxLayout()
        self.radioButtonHorizontalLayout.setObjectName("radioButtonHorizontalLayout")
        self.incomeRadioButton = QtWidgets.QRadioButton(CashTransactionDialog)
        self.incomeRadioButton.setObjectName("incomeRadioButton")
        self.radioButtonHorizontalLayout.addWidget(self.incomeRadioButton)
        self.expenseRadioButton = QtWidgets.QRadioButton(CashTransactionDialog)
        self.expenseRadioButton.setObjectName("expenseRadioButton")
        self.radioButtonHorizontalLayout.addWidget(self.expenseRadioButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.radioButtonHorizontalLayout.addItem(spacerItem)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.radioButtonHorizontalLayout)
        self.accountLabel = QtWidgets.QLabel(CashTransactionDialog)
        self.accountLabel.setObjectName("accountLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.accountLabel)
        self.accountsComboBox = QtWidgets.QComboBox(CashTransactionDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.accountsComboBox.sizePolicy().hasHeightForWidth())
        self.accountsComboBox.setSizePolicy(sizePolicy)
        self.accountsComboBox.setEditable(False)
        self.accountsComboBox.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.accountsComboBox.setObjectName("accountsComboBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.accountsComboBox)
        self.payeeLabel = QtWidgets.QLabel(CashTransactionDialog)
        self.payeeLabel.setObjectName("payeeLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.payeeLabel)
        self.payeeHorizontalLayout = QtWidgets.QHBoxLayout()
        self.payeeHorizontalLayout.setObjectName("payeeHorizontalLayout")
        self.payeeComboBox = QtWidgets.QComboBox(CashTransactionDialog)
        self.payeeComboBox.setEditable(True)
        self.payeeComboBox.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.payeeComboBox.setObjectName("payeeComboBox")
        self.payeeHorizontalLayout.addWidget(self.payeeComboBox)
        self.payeeToolButton = QtWidgets.QToolButton(CashTransactionDialog)
        self.payeeToolButton.setObjectName("payeeToolButton")
        self.payeeHorizontalLayout.addWidget(self.payeeToolButton)
        self.payeeHorizontalLayout.setStretch(0, 1)
        self.formLayout.setLayout(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.payeeHorizontalLayout)
        self.dateLabel = QtWidgets.QLabel(CashTransactionDialog)
        self.dateLabel.setObjectName("dateLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.dateLabel)
        self.dateEdit = QtWidgets.QDateEdit(CashTransactionDialog)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setTimeSpec(QtCore.Qt.TimeSpec.LocalTime)
        self.dateEdit.setObjectName("dateEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dateEdit)
        self.descriptionLabelVerticalLayout = QtWidgets.QVBoxLayout()
        self.descriptionLabelVerticalLayout.setObjectName("descriptionLabelVerticalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.descriptionLabelVerticalLayout.addItem(spacerItem1)
        self.descriptionLabel = QtWidgets.QLabel(CashTransactionDialog)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.descriptionLabelVerticalLayout.addWidget(self.descriptionLabel)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.descriptionLabelVerticalLayout.addItem(spacerItem2)
        self.formLayout.setLayout(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.descriptionLabelVerticalLayout)
        self.descriptionPlainTextEdit = QtWidgets.QPlainTextEdit(CashTransactionDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.descriptionPlainTextEdit.sizePolicy().hasHeightForWidth())
        self.descriptionPlainTextEdit.setSizePolicy(sizePolicy)
        self.descriptionPlainTextEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.descriptionPlainTextEdit.setTabChangesFocus(True)
        self.descriptionPlainTextEdit.setObjectName("descriptionPlainTextEdit")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.descriptionPlainTextEdit)
        self.amountLabel = QtWidgets.QLabel(CashTransactionDialog)
        self.amountLabel.setObjectName("amountLabel")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.LabelRole, self.amountLabel)
        self.amountDoubleSpinBox = QtWidgets.QDoubleSpinBox(CashTransactionDialog)
        self.amountDoubleSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.amountDoubleSpinBox.setProperty("showGroupSeparator", True)
        self.amountDoubleSpinBox.setMaximum(1e+16)
        self.amountDoubleSpinBox.setObjectName("amountDoubleSpinBox")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.amountDoubleSpinBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(CashTransactionDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.NoButton)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.actionSelect_Payee = QtGui.QAction(CashTransactionDialog)
        self.actionSelect_Payee.setObjectName("actionSelect_Payee")
        self.actionSelect_Tag = QtGui.QAction(CashTransactionDialog)
        self.actionSelect_Tag.setObjectName("actionSelect_Tag")
        self.actionSplit_Tags = QtGui.QAction(CashTransactionDialog)
        self.actionSplit_Tags.setObjectName("actionSplit_Tags")

        self.retranslateUi(CashTransactionDialog)
        QtCore.QMetaObject.connectSlotsByName(CashTransactionDialog)
        CashTransactionDialog.setTabOrder(self.incomeRadioButton, self.expenseRadioButton)
        CashTransactionDialog.setTabOrder(self.expenseRadioButton, self.accountsComboBox)
        CashTransactionDialog.setTabOrder(self.accountsComboBox, self.payeeComboBox)
        CashTransactionDialog.setTabOrder(self.payeeComboBox, self.payeeToolButton)
        CashTransactionDialog.setTabOrder(self.payeeToolButton, self.dateEdit)
        CashTransactionDialog.setTabOrder(self.dateEdit, self.descriptionPlainTextEdit)
        CashTransactionDialog.setTabOrder(self.descriptionPlainTextEdit, self.amountDoubleSpinBox)

    def retranslateUi(self, CashTransactionDialog):
        _translate = QtCore.QCoreApplication.translate
        CashTransactionDialog.setWindowTitle(_translate("CashTransactionDialog", "Dialog"))
        self.typeLabel.setText(_translate("CashTransactionDialog", "Type"))
        self.incomeRadioButton.setText(_translate("CashTransactionDialog", "Income"))
        self.expenseRadioButton.setText(_translate("CashTransactionDialog", "Expense"))
        self.accountLabel.setText(_translate("CashTransactionDialog", "Account"))
        self.payeeLabel.setText(_translate("CashTransactionDialog", "Payee"))
        self.payeeToolButton.setText(_translate("CashTransactionDialog", "..."))
        self.dateLabel.setText(_translate("CashTransactionDialog", "Date"))
        self.descriptionLabel.setText(_translate("CashTransactionDialog", "Description"))
        self.descriptionPlainTextEdit.setPlaceholderText(_translate("CashTransactionDialog", "Enter optional description"))
        self.amountLabel.setText(_translate("CashTransactionDialog", "Amount"))
        self.actionSelect_Payee.setText(_translate("CashTransactionDialog", "Select Payee"))
        self.actionSelect_Tag.setText(_translate("CashTransactionDialog", "Select Tag"))
        self.actionSplit_Tags.setText(_translate("CashTransactionDialog", "Split Tags"))
