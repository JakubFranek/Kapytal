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
        RefundTransactionDialog.resize(253, 82)
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
        self.dateLabel = QtWidgets.QLabel(RefundTransactionDialog)
        self.dateLabel.setObjectName("dateLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.dateLabel)
        self.dateEdit = QtWidgets.QDateEdit(RefundTransactionDialog)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setTimeSpec(QtCore.Qt.TimeSpec.LocalTime)
        self.dateEdit.setObjectName("dateEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dateEdit)
        self.amountLabel = QtWidgets.QLabel(RefundTransactionDialog)
        self.amountLabel.setObjectName("amountLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.amountLabel)
        self.amountDoubleSpinBox = QtWidgets.QDoubleSpinBox(RefundTransactionDialog)
        self.amountDoubleSpinBox.setEnabled(False)
        self.amountDoubleSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.amountDoubleSpinBox.setReadOnly(False)
        self.amountDoubleSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.amountDoubleSpinBox.setProperty("showGroupSeparator", True)
        self.amountDoubleSpinBox.setMaximum(1e+16)
        self.amountDoubleSpinBox.setObjectName("amountDoubleSpinBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.amountDoubleSpinBox)
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
        RefundTransactionDialog.setTabOrder(self.dateEdit, self.amountDoubleSpinBox)

    def retranslateUi(self, RefundTransactionDialog):
        _translate = QtCore.QCoreApplication.translate
        RefundTransactionDialog.setWindowTitle(_translate("RefundTransactionDialog", "Dialog"))
        self.dateLabel.setText(_translate("RefundTransactionDialog", "Date"))
        self.amountLabel.setText(_translate("RefundTransactionDialog", "Amount"))
        self.actionSelect_Payee.setText(_translate("RefundTransactionDialog", "Select Payee"))
        self.actionSelect_Tag.setText(_translate("RefundTransactionDialog", "Select Tag"))
        self.actionSelect_Account.setText(_translate("RefundTransactionDialog", "Select Account"))
