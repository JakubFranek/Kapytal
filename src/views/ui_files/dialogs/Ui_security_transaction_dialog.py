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
        SecurityTransactionDialog.resize(248, 309)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SecurityTransactionDialog.sizePolicy().hasHeightForWidth())
        SecurityTransactionDialog.setSizePolicy(sizePolicy)
        SecurityTransactionDialog.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
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
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.radioButtonHorizontalLayout.addItem(spacerItem)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.radioButtonHorizontalLayout)
        self.securityLabel = QtWidgets.QLabel(SecurityTransactionDialog)
        self.securityLabel.setObjectName("securityLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.securityLabel)
        self.securityComboBox = QtWidgets.QComboBox(SecurityTransactionDialog)
        self.securityComboBox.setObjectName("securityComboBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.securityComboBox)
        self.cashAccountLabel = QtWidgets.QLabel(SecurityTransactionDialog)
        self.cashAccountLabel.setObjectName("cashAccountLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.cashAccountLabel)
        self.cashAccountHorizontalLayout = QtWidgets.QHBoxLayout()
        self.cashAccountHorizontalLayout.setObjectName("cashAccountHorizontalLayout")
        self.cashAccountComboBox = QtWidgets.QComboBox(SecurityTransactionDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cashAccountComboBox.sizePolicy().hasHeightForWidth())
        self.cashAccountComboBox.setSizePolicy(sizePolicy)
        self.cashAccountComboBox.setEditable(False)
        self.cashAccountComboBox.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.cashAccountComboBox.setObjectName("cashAccountComboBox")
        self.cashAccountHorizontalLayout.addWidget(self.cashAccountComboBox)
        self.cashAccountToolButton = QtWidgets.QToolButton(SecurityTransactionDialog)
        self.cashAccountToolButton.setObjectName("cashAccountToolButton")
        self.cashAccountHorizontalLayout.addWidget(self.cashAccountToolButton)
        self.formLayout.setLayout(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.cashAccountHorizontalLayout)
        self.securityAccountLabel = QtWidgets.QLabel(SecurityTransactionDialog)
        self.securityAccountLabel.setObjectName("securityAccountLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.securityAccountLabel)
        self.securityAccountHorizontalLayout = QtWidgets.QHBoxLayout()
        self.securityAccountHorizontalLayout.setObjectName("securityAccountHorizontalLayout")
        self.securityAccountComboBox = QtWidgets.QComboBox(SecurityTransactionDialog)
        self.securityAccountComboBox.setObjectName("securityAccountComboBox")
        self.securityAccountHorizontalLayout.addWidget(self.securityAccountComboBox)
        self.securityAccountToolButton = QtWidgets.QToolButton(SecurityTransactionDialog)
        self.securityAccountToolButton.setObjectName("securityAccountToolButton")
        self.securityAccountHorizontalLayout.addWidget(self.securityAccountToolButton)
        self.formLayout.setLayout(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.securityAccountHorizontalLayout)
        self.dateLabel = QtWidgets.QLabel(SecurityTransactionDialog)
        self.dateLabel.setObjectName("dateLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.dateLabel)
        self.dateEdit = QtWidgets.QDateEdit(SecurityTransactionDialog)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setTimeSpec(QtCore.Qt.TimeSpec.LocalTime)
        self.dateEdit.setObjectName("dateEdit")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dateEdit)
        self.descriptionLabelVerticalLayout = QtWidgets.QVBoxLayout()
        self.descriptionLabelVerticalLayout.setObjectName("descriptionLabelVerticalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.descriptionLabelVerticalLayout.addItem(spacerItem1)
        self.descriptionLabel = QtWidgets.QLabel(SecurityTransactionDialog)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.descriptionLabelVerticalLayout.addWidget(self.descriptionLabel)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.descriptionLabelVerticalLayout.addItem(spacerItem2)
        self.formLayout.setLayout(5, QtWidgets.QFormLayout.ItemRole.LabelRole, self.descriptionLabelVerticalLayout)
        self.descriptionPlainTextEdit = QtWidgets.QPlainTextEdit(SecurityTransactionDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.descriptionPlainTextEdit.sizePolicy().hasHeightForWidth())
        self.descriptionPlainTextEdit.setSizePolicy(sizePolicy)
        self.descriptionPlainTextEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.descriptionPlainTextEdit.setTabChangesFocus(True)
        self.descriptionPlainTextEdit.setObjectName("descriptionPlainTextEdit")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.descriptionPlainTextEdit)
        self.sharesLabel = QtWidgets.QLabel(SecurityTransactionDialog)
        self.sharesLabel.setObjectName("sharesLabel")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.ItemRole.LabelRole, self.sharesLabel)
        self.sharesDoubleSpinBox = QtWidgets.QDoubleSpinBox(SecurityTransactionDialog)
        self.sharesDoubleSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.sharesDoubleSpinBox.setProperty("showGroupSeparator", True)
        self.sharesDoubleSpinBox.setMaximum(1e+16)
        self.sharesDoubleSpinBox.setObjectName("sharesDoubleSpinBox")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.ItemRole.FieldRole, self.sharesDoubleSpinBox)
        self.priceLabel = QtWidgets.QLabel(SecurityTransactionDialog)
        self.priceLabel.setObjectName("priceLabel")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.ItemRole.LabelRole, self.priceLabel)
        self.priceDoubleSpinBox = QtWidgets.QDoubleSpinBox(SecurityTransactionDialog)
        self.priceDoubleSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.priceDoubleSpinBox.setProperty("showGroupSeparator", True)
        self.priceDoubleSpinBox.setDecimals(9)
        self.priceDoubleSpinBox.setMaximum(1e+16)
        self.priceDoubleSpinBox.setObjectName("priceDoubleSpinBox")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.ItemRole.FieldRole, self.priceDoubleSpinBox)
        self.totalLabel = QtWidgets.QLabel(SecurityTransactionDialog)
        self.totalLabel.setObjectName("totalLabel")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.ItemRole.LabelRole, self.totalLabel)
        self.totalDoubleSpinBox = QtWidgets.QDoubleSpinBox(SecurityTransactionDialog)
        self.totalDoubleSpinBox.setEnabled(True)
        self.totalDoubleSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.totalDoubleSpinBox.setReadOnly(False)
        self.totalDoubleSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.totalDoubleSpinBox.setProperty("showGroupSeparator", True)
        self.totalDoubleSpinBox.setDecimals(9)
        self.totalDoubleSpinBox.setMaximum(1e+16)
        self.totalDoubleSpinBox.setObjectName("totalDoubleSpinBox")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.ItemRole.FieldRole, self.totalDoubleSpinBox)
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
        SecurityTransactionDialog.setTabOrder(self.sellRadioButton, self.securityComboBox)
        SecurityTransactionDialog.setTabOrder(self.securityComboBox, self.cashAccountComboBox)
        SecurityTransactionDialog.setTabOrder(self.cashAccountComboBox, self.cashAccountToolButton)
        SecurityTransactionDialog.setTabOrder(self.cashAccountToolButton, self.securityAccountComboBox)
        SecurityTransactionDialog.setTabOrder(self.securityAccountComboBox, self.securityAccountToolButton)
        SecurityTransactionDialog.setTabOrder(self.securityAccountToolButton, self.dateEdit)
        SecurityTransactionDialog.setTabOrder(self.dateEdit, self.descriptionPlainTextEdit)
        SecurityTransactionDialog.setTabOrder(self.descriptionPlainTextEdit, self.sharesDoubleSpinBox)
        SecurityTransactionDialog.setTabOrder(self.sharesDoubleSpinBox, self.priceDoubleSpinBox)
        SecurityTransactionDialog.setTabOrder(self.priceDoubleSpinBox, self.totalDoubleSpinBox)

    def retranslateUi(self, SecurityTransactionDialog):
        _translate = QtCore.QCoreApplication.translate
        SecurityTransactionDialog.setWindowTitle(_translate("SecurityTransactionDialog", "Dialog"))
        self.typeLabel.setText(_translate("SecurityTransactionDialog", "Type"))
        self.buyRadioButton.setText(_translate("SecurityTransactionDialog", "Buy"))
        self.sellRadioButton.setText(_translate("SecurityTransactionDialog", "Sell"))
        self.securityLabel.setText(_translate("SecurityTransactionDialog", "Security"))
        self.cashAccountLabel.setText(_translate("SecurityTransactionDialog", "Cash Account"))
        self.cashAccountToolButton.setText(_translate("SecurityTransactionDialog", "..."))
        self.securityAccountLabel.setText(_translate("SecurityTransactionDialog", "Security Account"))
        self.securityAccountToolButton.setText(_translate("SecurityTransactionDialog", "..."))
        self.dateLabel.setText(_translate("SecurityTransactionDialog", "Date"))
        self.descriptionLabel.setText(_translate("SecurityTransactionDialog", "Description"))
        self.descriptionPlainTextEdit.setPlaceholderText(_translate("SecurityTransactionDialog", "Enter optional description"))
        self.sharesLabel.setText(_translate("SecurityTransactionDialog", "Shares"))
        self.priceLabel.setText(_translate("SecurityTransactionDialog", "Price per share"))
        self.totalLabel.setText(_translate("SecurityTransactionDialog", "Total"))
        self.actionSelect_Cash_Account.setText(_translate("SecurityTransactionDialog", "Select Cash Account"))
        self.actionSelect_Security_Account.setText(_translate("SecurityTransactionDialog", "Select Security Account"))
