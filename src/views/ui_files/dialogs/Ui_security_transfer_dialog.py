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
        SecurityTransferDialog.resize(248, 192)
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
        self.sharesLabel = QtWidgets.QLabel(SecurityTransferDialog)
        self.sharesLabel.setObjectName("sharesLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.sharesLabel)
        self.sharesDoubleSpinBox = QtWidgets.QDoubleSpinBox(SecurityTransferDialog)
        self.sharesDoubleSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.sharesDoubleSpinBox.setProperty("showGroupSeparator", True)
        self.sharesDoubleSpinBox.setMaximum(1e+16)
        self.sharesDoubleSpinBox.setObjectName("sharesDoubleSpinBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.sharesDoubleSpinBox)
        self.dateLabel = QtWidgets.QLabel(SecurityTransferDialog)
        self.dateLabel.setObjectName("dateLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.dateLabel)
        self.dateEdit = QtWidgets.QDateEdit(SecurityTransferDialog)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setTimeSpec(QtCore.Qt.TimeSpec.LocalTime)
        self.dateEdit.setObjectName("dateEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dateEdit)
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
        self.sharesLabel.setText(_translate("SecurityTransferDialog", "Shares"))
        self.dateLabel.setText(_translate("SecurityTransferDialog", "Date"))
        self.dateEdit.setDisplayFormat(_translate("SecurityTransferDialog", "dd.MM.yyyy hh:mm"))
