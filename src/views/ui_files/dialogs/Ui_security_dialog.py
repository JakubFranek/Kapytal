# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\dialogs\security_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SecurityDialog(object):
    def setupUi(self, SecurityDialog):
        SecurityDialog.setObjectName("SecurityDialog")
        SecurityDialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        SecurityDialog.resize(300, 165)
        self.verticalLayout = QtWidgets.QVBoxLayout(SecurityDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.nameLabel = QtWidgets.QLabel(parent=SecurityDialog)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(parent=SecurityDialog)
        self.nameLineEdit.setMaxLength(64)
        self.nameLineEdit.setPlaceholderText("")
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.nameLineEdit)
        self.symbolLabel = QtWidgets.QLabel(parent=SecurityDialog)
        self.symbolLabel.setObjectName("symbolLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.symbolLabel)
        self.symbolLineEdit = QtWidgets.QLineEdit(parent=SecurityDialog)
        self.symbolLineEdit.setMaxLength(8)
        self.symbolLineEdit.setObjectName("symbolLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.symbolLineEdit)
        self.decimalsLabel = QtWidgets.QLabel(parent=SecurityDialog)
        self.decimalsLabel.setObjectName("decimalsLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.decimalsLabel)
        self.currencyLabel = QtWidgets.QLabel(parent=SecurityDialog)
        self.currencyLabel.setObjectName("currencyLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.currencyLabel)
        self.currencyComboBox = QtWidgets.QComboBox(parent=SecurityDialog)
        self.currencyComboBox.setObjectName("currencyComboBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.currencyComboBox)
        self.decimalsSpinBox = QtWidgets.QSpinBox(parent=SecurityDialog)
        self.decimalsSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.decimalsSpinBox.setMaximum(18)
        self.decimalsSpinBox.setObjectName("decimalsSpinBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.decimalsSpinBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=SecurityDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SecurityDialog)
        QtCore.QMetaObject.connectSlotsByName(SecurityDialog)

    def retranslateUi(self, SecurityDialog):
        _translate = QtCore.QCoreApplication.translate
        SecurityDialog.setWindowTitle(_translate("SecurityDialog", "Add Currency"))
        self.nameLabel.setToolTip(_translate("SecurityDialog", "<html><head/><body><p>Name of the Security can be any text string. Contrary to the Symbol, it is not used by Kapytal for downloading quotes.</p></body></html>"))
        self.nameLabel.setText(_translate("SecurityDialog", "Name"))
        self.nameLineEdit.setToolTip(_translate("SecurityDialog", "<html><head/><body><p>Name of the Security can be any text string. Contrary to the Symbol, it is not used by Kapytal for downloading quotes.</p></body></html>"))
        self.symbolLabel.setText(_translate("SecurityDialog", "Symbol"))
        self.symbolLineEdit.setToolTip(_translate("SecurityDialog", "<html><head/><body><p>If Yahoo Finance ticker of the Security is entered (for example &quot;VWCE.DE&quot;), Update Quotes Form will be able to download the quote. Leave empty if the Security does not exist on Yahoo Finance.</p></body></html>"))
        self.symbolLineEdit.setPlaceholderText(_translate("SecurityDialog", "Optional field"))
        self.decimalsLabel.setToolTip(_translate("SecurityDialog", "<html><head/><body><p>Number of decimals of Security shares.<br/><br/>For example:<br/>0 decimals - shares are multiples of 1<br/>1 decimals - shares are multiples of 0.1<br/>2 decimals - shares are multiples of 0.01</p></body></html>"))
        self.decimalsLabel.setText(_translate("SecurityDialog", "Shares decimals"))
        self.currencyLabel.setText(_translate("SecurityDialog", "Currency"))
        self.decimalsSpinBox.setToolTip(_translate("SecurityDialog", "<html><head/><body><p>Number of decimals of Security shares.<br/><br/>For example:<br/>0 decimals - shares are multiples of 1<br/>1 decimals - shares are multiples of 0.1<br/>2 decimals - shares are multiples of 0.01</p></body></html>"))
