# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\dialogs\refund_transaction_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_RefundTransactionDialog(object):
    def setupUi(self, RefundTransactionDialog):
        RefundTransactionDialog.setObjectName("RefundTransactionDialog")
        RefundTransactionDialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        RefundTransactionDialog.resize(253, 246)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(RefundTransactionDialog.sizePolicy().hasHeightForWidth())
        RefundTransactionDialog.setSizePolicy(sizePolicy)
        RefundTransactionDialog.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.verticalLayout = QtWidgets.QVBoxLayout(RefundTransactionDialog)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.accountLabel = QtWidgets.QLabel(RefundTransactionDialog)
        self.accountLabel.setObjectName("accountLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.accountLabel)
        self.accountHorizontalLayout = QtWidgets.QHBoxLayout()
        self.accountHorizontalLayout.setObjectName("accountHorizontalLayout")
        self.accountsComboBox = QtWidgets.QComboBox(RefundTransactionDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.accountsComboBox.sizePolicy().hasHeightForWidth())
        self.accountsComboBox.setSizePolicy(sizePolicy)
        self.accountsComboBox.setEditable(False)
        self.accountsComboBox.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.accountsComboBox.setObjectName("accountsComboBox")
        self.accountHorizontalLayout.addWidget(self.accountsComboBox)
        self.accountsToolButton = QtWidgets.QToolButton(RefundTransactionDialog)
        self.accountsToolButton.setObjectName("accountsToolButton")
        self.accountHorizontalLayout.addWidget(self.accountsToolButton)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.accountHorizontalLayout)
        self.payeeLabel = QtWidgets.QLabel(RefundTransactionDialog)
        self.payeeLabel.setObjectName("payeeLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.payeeLabel)
        self.payeeHorizontalLayout = QtWidgets.QHBoxLayout()
        self.payeeHorizontalLayout.setObjectName("payeeHorizontalLayout")
        self.payeeComboBox = QtWidgets.QComboBox(RefundTransactionDialog)
        self.payeeComboBox.setEditable(True)
        self.payeeComboBox.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.payeeComboBox.setObjectName("payeeComboBox")
        self.payeeHorizontalLayout.addWidget(self.payeeComboBox)
        self.payeeToolButton = QtWidgets.QToolButton(RefundTransactionDialog)
        self.payeeToolButton.setObjectName("payeeToolButton")
        self.payeeHorizontalLayout.addWidget(self.payeeToolButton)
        self.payeeHorizontalLayout.setStretch(0, 1)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.payeeHorizontalLayout)
        self.dateLabel = QtWidgets.QLabel(RefundTransactionDialog)
        self.dateLabel.setObjectName("dateLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.dateLabel)
        self.dateEdit = QtWidgets.QDateEdit(RefundTransactionDialog)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setTimeSpec(QtCore.Qt.TimeSpec.LocalTime)
        self.dateEdit.setObjectName("dateEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dateEdit)
        self.descriptionLabelVerticalLayout = QtWidgets.QVBoxLayout()
        self.descriptionLabelVerticalLayout.setObjectName("descriptionLabelVerticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.descriptionLabelVerticalLayout.addItem(spacerItem)
        self.descriptionLabel = QtWidgets.QLabel(RefundTransactionDialog)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.descriptionLabelVerticalLayout.addWidget(self.descriptionLabel)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.descriptionLabelVerticalLayout.addItem(spacerItem1)
        self.formLayout.setLayout(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.descriptionLabelVerticalLayout)
        self.descriptionPlainTextEdit = QtWidgets.QPlainTextEdit(RefundTransactionDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.descriptionPlainTextEdit.sizePolicy().hasHeightForWidth())
        self.descriptionPlainTextEdit.setSizePolicy(sizePolicy)
        self.descriptionPlainTextEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.descriptionPlainTextEdit.setTabChangesFocus(True)
        self.descriptionPlainTextEdit.setObjectName("descriptionPlainTextEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.descriptionPlainTextEdit)
        self.amountLabel = QtWidgets.QLabel(RefundTransactionDialog)
        self.amountLabel.setObjectName("amountLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.amountLabel)
        self.amountDoubleSpinBox = QtWidgets.QDoubleSpinBox(RefundTransactionDialog)
        self.amountDoubleSpinBox.setEnabled(False)
        self.amountDoubleSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.amountDoubleSpinBox.setReadOnly(False)
        self.amountDoubleSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.amountDoubleSpinBox.setProperty("showGroupSeparator", True)
        self.amountDoubleSpinBox.setMaximum(1e+16)
        self.amountDoubleSpinBox.setObjectName("amountDoubleSpinBox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.amountDoubleSpinBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(RefundTransactionDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.NoButton)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.actionSelect_Payee = QtGui.QAction(RefundTransactionDialog)
        self.actionSelect_Payee.setObjectName("actionSelect_Payee")
        self.actionSelect_Tag = QtGui.QAction(RefundTransactionDialog)
        self.actionSelect_Tag.setObjectName("actionSelect_Tag")
        self.actionSelect_Account = QtGui.QAction(RefundTransactionDialog)
        self.actionSelect_Account.setObjectName("actionSelect_Account")

        self.retranslateUi(RefundTransactionDialog)
        QtCore.QMetaObject.connectSlotsByName(RefundTransactionDialog)
        RefundTransactionDialog.setTabOrder(self.accountsComboBox, self.accountsToolButton)
        RefundTransactionDialog.setTabOrder(self.accountsToolButton, self.payeeComboBox)
        RefundTransactionDialog.setTabOrder(self.payeeComboBox, self.payeeToolButton)
        RefundTransactionDialog.setTabOrder(self.payeeToolButton, self.dateEdit)
        RefundTransactionDialog.setTabOrder(self.dateEdit, self.descriptionPlainTextEdit)
        RefundTransactionDialog.setTabOrder(self.descriptionPlainTextEdit, self.amountDoubleSpinBox)

    def retranslateUi(self, RefundTransactionDialog):
        _translate = QtCore.QCoreApplication.translate
        RefundTransactionDialog.setWindowTitle(_translate("RefundTransactionDialog", "Dialog"))
        self.accountLabel.setText(_translate("RefundTransactionDialog", "Account"))
        self.accountsToolButton.setText(_translate("RefundTransactionDialog", "..."))
        self.payeeLabel.setText(_translate("RefundTransactionDialog", "Payee"))
        self.payeeToolButton.setText(_translate("RefundTransactionDialog", "..."))
        self.dateLabel.setText(_translate("RefundTransactionDialog", "Date"))
        self.descriptionLabel.setText(_translate("RefundTransactionDialog", "Description"))
        self.descriptionPlainTextEdit.setPlaceholderText(_translate("RefundTransactionDialog", "Enter optional description"))
        self.amountLabel.setText(_translate("RefundTransactionDialog", "Amount"))
        self.actionSelect_Payee.setText(_translate("RefundTransactionDialog", "Select Payee"))
        self.actionSelect_Tag.setText(_translate("RefundTransactionDialog", "Select Tag"))
        self.actionSelect_Account.setText(_translate("RefundTransactionDialog", "Select Account"))
