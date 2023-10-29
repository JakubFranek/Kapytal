# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\dialogs\security_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SecurityDialog(object):
    def setupUi(self, SecurityDialog):
        SecurityDialog.setObjectName("SecurityDialog")
        SecurityDialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        SecurityDialog.resize(300, 165)
        SecurityDialog.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.verticalLayout = QtWidgets.QVBoxLayout(SecurityDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.nameLabel = QtWidgets.QLabel(SecurityDialog)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(SecurityDialog)
        self.nameLineEdit.setMaxLength(64)
        self.nameLineEdit.setPlaceholderText("")
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.nameLineEdit)
        self.symbolLabel = QtWidgets.QLabel(SecurityDialog)
        self.symbolLabel.setObjectName("symbolLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.symbolLabel)
        self.symbolLineEdit = QtWidgets.QLineEdit(SecurityDialog)
        self.symbolLineEdit.setMaxLength(8)
        self.symbolLineEdit.setObjectName("symbolLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.symbolLineEdit)
        self.unitLabel = QtWidgets.QLabel(SecurityDialog)
        self.unitLabel.setObjectName("unitLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.unitLabel)
        self.currencyLabel = QtWidgets.QLabel(SecurityDialog)
        self.currencyLabel.setObjectName("currencyLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.currencyLabel)
        self.currencyComboBox = QtWidgets.QComboBox(SecurityDialog)
        self.currencyComboBox.setObjectName("currencyComboBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.currencyComboBox)
        self.decimalsSpinBox = QtWidgets.QSpinBox(SecurityDialog)
        self.decimalsSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.decimalsSpinBox.setMaximum(18)
        self.decimalsSpinBox.setObjectName("decimalsSpinBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.decimalsSpinBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(SecurityDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SecurityDialog)
        QtCore.QMetaObject.connectSlotsByName(SecurityDialog)

    def retranslateUi(self, SecurityDialog):
        _translate = QtCore.QCoreApplication.translate
        SecurityDialog.setWindowTitle(_translate("SecurityDialog", "Add Currency"))
        self.nameLabel.setText(_translate("SecurityDialog", "Name"))
        self.symbolLabel.setText(_translate("SecurityDialog", "Symbol"))
        self.symbolLineEdit.setPlaceholderText(_translate("SecurityDialog", "Optional field"))
        self.unitLabel.setToolTip(_translate("SecurityDialog", "<html><head/><body><p>Number of decimals of Security shares.</p><p><br/>For example:</p><p>0 decimals - shares are multiples of 1</p><p>1 decimals - shares are multiples of 0.1</p></body></html>"))
        self.unitLabel.setText(_translate("SecurityDialog", "Shares decimals"))
        self.currencyLabel.setText(_translate("SecurityDialog", "Currency"))
        self.decimalsSpinBox.setToolTip(_translate("SecurityDialog", "<html><head/><body><p>Number of decimals of Security shares.</p><p><br/>For example:</p><p>0 decimals - shares are multiples of 1</p><p>1 decimals - shares are multiples of 0.1</p></body></html>"))
