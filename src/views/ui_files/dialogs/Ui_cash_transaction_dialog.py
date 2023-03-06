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
        CashTransactionDialog.resize(250, 320)
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
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.incomeRadioButton = QtWidgets.QRadioButton(CashTransactionDialog)
        self.incomeRadioButton.setObjectName("incomeRadioButton")
        self.horizontalLayout.addWidget(self.incomeRadioButton)
        self.expenseRadioButton = QtWidgets.QRadioButton(CashTransactionDialog)
        self.expenseRadioButton.setObjectName("expenseRadioButton")
        self.horizontalLayout.addWidget(self.expenseRadioButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.horizontalLayout)
        self.accountLabel = QtWidgets.QLabel(CashTransactionDialog)
        self.accountLabel.setObjectName("accountLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.accountLabel)
        self.accountsComboBox = QtWidgets.QComboBox(CashTransactionDialog)
        self.accountsComboBox.setObjectName("accountsComboBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.accountsComboBox)
        self.descriptionLabel = QtWidgets.QLabel(CashTransactionDialog)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.descriptionLabel)
        self.descriptionPlainTextEdit = QtWidgets.QPlainTextEdit(CashTransactionDialog)
        self.descriptionPlainTextEdit.setObjectName("descriptionPlainTextEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.descriptionPlainTextEdit)
        self.amountLabel = QtWidgets.QLabel(CashTransactionDialog)
        self.amountLabel.setObjectName("amountLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.amountLabel)
        self.amountDoubleSpinBox = QtWidgets.QDoubleSpinBox(CashTransactionDialog)
        self.amountDoubleSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.amountDoubleSpinBox.setMaximum(1e+16)
        self.amountDoubleSpinBox.setObjectName("amountDoubleSpinBox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.amountDoubleSpinBox)
        self.categoryLabel = QtWidgets.QLabel(CashTransactionDialog)
        self.categoryLabel.setObjectName("categoryLabel")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.LabelRole, self.categoryLabel)
        self.categoryLineEdit = QtWidgets.QLineEdit(CashTransactionDialog)
        self.categoryLineEdit.setObjectName("categoryLineEdit")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.categoryLineEdit)
        self.tagsLabel = QtWidgets.QLabel(CashTransactionDialog)
        self.tagsLabel.setObjectName("tagsLabel")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.ItemRole.LabelRole, self.tagsLabel)
        self.dateTimeLabel = QtWidgets.QLabel(CashTransactionDialog)
        self.dateTimeLabel.setObjectName("dateTimeLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.dateTimeLabel)
        self.dateTimeEdit = QtWidgets.QDateTimeEdit(CashTransactionDialog)
        self.dateTimeEdit.setWrapping(False)
        self.dateTimeEdit.setReadOnly(False)
        self.dateTimeEdit.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.dateTimeEdit.setProperty("showGroupSeparator", False)
        self.dateTimeEdit.setCalendarPopup(True)
        self.dateTimeEdit.setTimeSpec(QtCore.Qt.TimeSpec.LocalTime)
        self.dateTimeEdit.setObjectName("dateTimeEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dateTimeEdit)
        self.tagsLineEdit = QtWidgets.QLineEdit(CashTransactionDialog)
        self.tagsLineEdit.setObjectName("tagsLineEdit")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.ItemRole.FieldRole, self.tagsLineEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(CashTransactionDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.NoButton)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(CashTransactionDialog)
        QtCore.QMetaObject.connectSlotsByName(CashTransactionDialog)

    def retranslateUi(self, CashTransactionDialog):
        _translate = QtCore.QCoreApplication.translate
        CashTransactionDialog.setWindowTitle(_translate("CashTransactionDialog", "Dialog"))
        self.typeLabel.setText(_translate("CashTransactionDialog", "Type"))
        self.incomeRadioButton.setText(_translate("CashTransactionDialog", "Income"))
        self.expenseRadioButton.setText(_translate("CashTransactionDialog", "Expense"))
        self.accountLabel.setText(_translate("CashTransactionDialog", "Account"))
        self.descriptionLabel.setText(_translate("CashTransactionDialog", "Description"))
        self.amountLabel.setText(_translate("CashTransactionDialog", "Amount"))
        self.categoryLabel.setText(_translate("CashTransactionDialog", "Category"))
        self.tagsLabel.setText(_translate("CashTransactionDialog", "Tags"))
        self.dateTimeLabel.setText(_translate("CashTransactionDialog", "Date & Time"))
