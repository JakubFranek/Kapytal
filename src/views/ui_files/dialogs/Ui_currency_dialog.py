# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\dialogs\currency_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_CurrencyDialog(object):
    def setupUi(self, CurrencyDialog):
        CurrencyDialog.setObjectName("CurrencyDialog")
        CurrencyDialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        CurrencyDialog.resize(392, 105)
        self.verticalLayout = QtWidgets.QVBoxLayout(CurrencyDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.currencyCodeLabel = QtWidgets.QLabel(CurrencyDialog)
        self.currencyCodeLabel.setObjectName("currencyCodeLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.currencyCodeLabel)
        self.currencyCodeLineEdit = QtWidgets.QLineEdit(CurrencyDialog)
        self.currencyCodeLineEdit.setMaxLength(3)
        self.currencyCodeLineEdit.setObjectName("currencyCodeLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.currencyCodeLineEdit)
        self.currencyDecimalsLabel = QtWidgets.QLabel(CurrencyDialog)
        self.currencyDecimalsLabel.setObjectName("currencyDecimalsLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.currencyDecimalsLabel)
        self.currencyDecimalsSpinBox = QtWidgets.QSpinBox(CurrencyDialog)
        self.currencyDecimalsSpinBox.setObjectName("currencyDecimalsSpinBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.currencyDecimalsSpinBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(CurrencyDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(CurrencyDialog)
        QtCore.QMetaObject.connectSlotsByName(CurrencyDialog)

    def retranslateUi(self, CurrencyDialog):
        _translate = QtCore.QCoreApplication.translate
        CurrencyDialog.setWindowTitle(_translate("CurrencyDialog", "Add Currency"))
        self.currencyCodeLabel.setText(_translate("CurrencyDialog", "Currency Code"))
        self.currencyCodeLineEdit.setPlaceholderText(_translate("CurrencyDialog", "Enter three letters (e.g. ISO 4217 code)"))
        self.currencyDecimalsLabel.setText(_translate("CurrencyDialog", "Decimal places"))
