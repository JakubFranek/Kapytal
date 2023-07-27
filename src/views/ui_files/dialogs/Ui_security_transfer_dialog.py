# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\dialogs\security_transfer_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SecurityTransferDialog(object):
    def setupUi(self, SecurityTransferDialog):
        SecurityTransferDialog.setObjectName("SecurityTransferDialog")
        SecurityTransferDialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        SecurityTransferDialog.resize(248, 238)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SecurityTransferDialog.sizePolicy().hasHeightForWidth())
        SecurityTransferDialog.setSizePolicy(sizePolicy)
        SecurityTransferDialog.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.verticalLayout = QtWidgets.QVBoxLayout(SecurityTransferDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.senderLabel = QtWidgets.QLabel(SecurityTransferDialog)
        self.senderLabel.setObjectName("senderLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.senderLabel)
        self.senderComboBox = QtWidgets.QComboBox(SecurityTransferDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.senderComboBox.sizePolicy().hasHeightForWidth())
        self.senderComboBox.setSizePolicy(sizePolicy)
        self.senderComboBox.setEditable(False)
        self.senderComboBox.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.senderComboBox.setObjectName("senderComboBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.senderComboBox)
        self.recipientLabel = QtWidgets.QLabel(SecurityTransferDialog)
        self.recipientLabel.setObjectName("recipientLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.recipientLabel)
        self.recipientComboBox = QtWidgets.QComboBox(SecurityTransferDialog)
        self.recipientComboBox.setObjectName("recipientComboBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.recipientComboBox)
        self.securityLabel = QtWidgets.QLabel(SecurityTransferDialog)
        self.securityLabel.setObjectName("securityLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.securityLabel)
        self.securityComboBox = QtWidgets.QComboBox(SecurityTransferDialog)
        self.securityComboBox.setObjectName("securityComboBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.securityComboBox)
        self.sharesLabel = QtWidgets.QLabel(SecurityTransferDialog)
        self.sharesLabel.setObjectName("sharesLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.sharesLabel)
        self.sharesDoubleSpinBox = QtWidgets.QDoubleSpinBox(SecurityTransferDialog)
        self.sharesDoubleSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.sharesDoubleSpinBox.setProperty("showGroupSeparator", True)
        self.sharesDoubleSpinBox.setMaximum(1e+16)
        self.sharesDoubleSpinBox.setObjectName("sharesDoubleSpinBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.sharesDoubleSpinBox)
        self.dateLabel = QtWidgets.QLabel(SecurityTransferDialog)
        self.dateLabel.setObjectName("dateLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.dateLabel)
        self.dateEdit = QtWidgets.QDateEdit(SecurityTransferDialog)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setTimeSpec(QtCore.Qt.TimeSpec.LocalTime)
        self.dateEdit.setObjectName("dateEdit")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dateEdit)
        self.descriptionLabelVerticalLayout = QtWidgets.QVBoxLayout()
        self.descriptionLabelVerticalLayout.setObjectName("descriptionLabelVerticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.descriptionLabelVerticalLayout.addItem(spacerItem)
        self.descriptionLabel = QtWidgets.QLabel(SecurityTransferDialog)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.descriptionLabelVerticalLayout.addWidget(self.descriptionLabel)
        spacerItem1 = QtWidgets.QSpacerItem(20, 25, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.descriptionLabelVerticalLayout.addItem(spacerItem1)
        self.formLayout.setLayout(5, QtWidgets.QFormLayout.ItemRole.LabelRole, self.descriptionLabelVerticalLayout)
        self.descriptionPlainTextEdit = QtWidgets.QPlainTextEdit(SecurityTransferDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.descriptionPlainTextEdit.sizePolicy().hasHeightForWidth())
        self.descriptionPlainTextEdit.setSizePolicy(sizePolicy)
        self.descriptionPlainTextEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.descriptionPlainTextEdit.setTabChangesFocus(True)
        self.descriptionPlainTextEdit.setObjectName("descriptionPlainTextEdit")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.descriptionPlainTextEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(SecurityTransferDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.NoButton)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SecurityTransferDialog)
        QtCore.QMetaObject.connectSlotsByName(SecurityTransferDialog)

    def retranslateUi(self, SecurityTransferDialog):
        _translate = QtCore.QCoreApplication.translate
        SecurityTransferDialog.setWindowTitle(_translate("SecurityTransferDialog", "Dialog"))
        self.senderLabel.setText(_translate("SecurityTransferDialog", "Sender"))
        self.recipientLabel.setText(_translate("SecurityTransferDialog", "Recipient"))
        self.securityLabel.setText(_translate("SecurityTransferDialog", "Security"))
        self.sharesLabel.setText(_translate("SecurityTransferDialog", "Shares"))
        self.dateLabel.setText(_translate("SecurityTransferDialog", "Date"))
        self.descriptionLabel.setText(_translate("SecurityTransferDialog", "Description"))
        self.descriptionPlainTextEdit.setPlaceholderText(_translate("SecurityTransferDialog", "Enter optional description"))
