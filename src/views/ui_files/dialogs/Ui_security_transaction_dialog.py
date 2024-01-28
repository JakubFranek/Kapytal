# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\dialogs\security_transaction_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SecurityTransactionDialog(object):
    def setupUi(self, SecurityTransactionDialog):
        SecurityTransactionDialog.setObjectName("SecurityTransactionDialog")
        SecurityTransactionDialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        SecurityTransactionDialog.resize(292, 228)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SecurityTransactionDialog.sizePolicy().hasHeightForWidth())
        SecurityTransactionDialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(SecurityTransactionDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.typeLabel = QtWidgets.QLabel(SecurityTransactionDialog)
        self.typeLabel.setObjectName("typeLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.typeLabel)
        self.radioButtonHorizontalLayout = QtWidgets.QHBoxLayout()
        self.radioButtonHorizontalLayout.setObjectName("radioButtonHorizontalLayout")
        self.buyRadioButton = QtWidgets.QRadioButton(SecurityTransactionDialog)
        self.buyRadioButton.setObjectName("buyRadioButton")
        self.radioButtonHorizontalLayout.addWidget(self.buyRadioButton)
        self.sellRadioButton = QtWidgets.QRadioButton(SecurityTransactionDialog)
        self.sellRadioButton.setObjectName("sellRadioButton")
        self.radioButtonHorizontalLayout.addWidget(self.sellRadioButton)
        self.dividendRadioButton = QtWidgets.QRadioButton(SecurityTransactionDialog)
        self.dividendRadioButton.setObjectName("dividendRadioButton")
        self.radioButtonHorizontalLayout.addWidget(self.dividendRadioButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.radioButtonHorizontalLayout.addItem(spacerItem)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.radioButtonHorizontalLayout)
        self.dateLabel = QtWidgets.QLabel(SecurityTransactionDialog)
        self.dateLabel.setObjectName("dateLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.dateLabel)
        self.sharesLabel = QtWidgets.QLabel(SecurityTransactionDialog)
        self.sharesLabel.setObjectName("sharesLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.sharesLabel)
        self.sharesDoubleSpinBox = QtWidgets.QDoubleSpinBox(SecurityTransactionDialog)
        self.sharesDoubleSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.sharesDoubleSpinBox.setProperty("showGroupSeparator", True)
        self.sharesDoubleSpinBox.setDecimals(0)
        self.sharesDoubleSpinBox.setMaximum(1e+16)
        self.sharesDoubleSpinBox.setObjectName("sharesDoubleSpinBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.sharesDoubleSpinBox)
        self.priceLabel = QtWidgets.QLabel(SecurityTransactionDialog)
        self.priceLabel.setObjectName("priceLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.priceLabel)
        self.priceDoubleSpinBox = QtWidgets.QDoubleSpinBox(SecurityTransactionDialog)
        self.priceDoubleSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.priceDoubleSpinBox.setProperty("showGroupSeparator", True)
        self.priceDoubleSpinBox.setDecimals(0)
        self.priceDoubleSpinBox.setMaximum(1e+16)
        self.priceDoubleSpinBox.setObjectName("priceDoubleSpinBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.priceDoubleSpinBox)
        self.totalLabel = QtWidgets.QLabel(SecurityTransactionDialog)
        self.totalLabel.setObjectName("totalLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.totalLabel)
        self.totalDoubleSpinBox = QtWidgets.QDoubleSpinBox(SecurityTransactionDialog)
        self.totalDoubleSpinBox.setEnabled(True)
        self.totalDoubleSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.totalDoubleSpinBox.setReadOnly(False)
        self.totalDoubleSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.totalDoubleSpinBox.setProperty("showGroupSeparator", True)
        self.totalDoubleSpinBox.setDecimals(0)
        self.totalDoubleSpinBox.setMaximum(1e+16)
        self.totalDoubleSpinBox.setObjectName("totalDoubleSpinBox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.totalDoubleSpinBox)
        self.dateTimeEdit = QtWidgets.QDateTimeEdit(SecurityTransactionDialog)
        self.dateTimeEdit.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.dateTimeEdit.setCalendarPopup(True)
        self.dateTimeEdit.setObjectName("dateTimeEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dateTimeEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(SecurityTransactionDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.NoButton)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.actionSelect_Cash_Account = QtGui.QAction(SecurityTransactionDialog)
        self.actionSelect_Cash_Account.setObjectName("actionSelect_Cash_Account")
        self.actionSelect_Security_Account = QtGui.QAction(SecurityTransactionDialog)
        self.actionSelect_Security_Account.setObjectName("actionSelect_Security_Account")

        self.retranslateUi(SecurityTransactionDialog)
        QtCore.QMetaObject.connectSlotsByName(SecurityTransactionDialog)
        SecurityTransactionDialog.setTabOrder(self.buyRadioButton, self.sellRadioButton)
        SecurityTransactionDialog.setTabOrder(self.sellRadioButton, self.sharesDoubleSpinBox)
        SecurityTransactionDialog.setTabOrder(self.sharesDoubleSpinBox, self.priceDoubleSpinBox)
        SecurityTransactionDialog.setTabOrder(self.priceDoubleSpinBox, self.totalDoubleSpinBox)

    def retranslateUi(self, SecurityTransactionDialog):
        _translate = QtCore.QCoreApplication.translate
        SecurityTransactionDialog.setWindowTitle(_translate("SecurityTransactionDialog", "Dialog"))
        self.typeLabel.setText(_translate("SecurityTransactionDialog", "Type"))
        self.buyRadioButton.setText(_translate("SecurityTransactionDialog", "Buy"))
        self.sellRadioButton.setText(_translate("SecurityTransactionDialog", "Sell"))
        self.dividendRadioButton.setText(_translate("SecurityTransactionDialog", "Dividend"))
        self.dateLabel.setText(_translate("SecurityTransactionDialog", "Date"))
        self.sharesLabel.setText(_translate("SecurityTransactionDialog", "Shares"))
        self.priceLabel.setText(_translate("SecurityTransactionDialog", "Amount per Share"))
        self.totalLabel.setText(_translate("SecurityTransactionDialog", "Total"))
        self.dateTimeEdit.setDisplayFormat(_translate("SecurityTransactionDialog", "dd.MM.yyyy hh:mm"))
        self.actionSelect_Cash_Account.setText(_translate("SecurityTransactionDialog", "Select Cash Account"))
        self.actionSelect_Security_Account.setText(_translate("SecurityTransactionDialog", "Select Security Account"))
