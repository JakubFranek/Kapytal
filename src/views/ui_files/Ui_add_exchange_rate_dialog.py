# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\add_exchange_rate_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_AddExchangeRateDialog(object):
    def setupUi(self, AddExchangeRateDialog):
        AddExchangeRateDialog.setObjectName("AddExchangeRateDialog")
        AddExchangeRateDialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        AddExchangeRateDialog.resize(398, 104)
        AddExchangeRateDialog.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.verticalLayout = QtWidgets.QVBoxLayout(AddExchangeRateDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.primaryCurrencyLabel = QtWidgets.QLabel(AddExchangeRateDialog)
        self.primaryCurrencyLabel.setObjectName("primaryCurrencyLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.primaryCurrencyLabel)
        self.primaryCurrencyComboBox = QtWidgets.QComboBox(AddExchangeRateDialog)
        self.primaryCurrencyComboBox.setObjectName("primaryCurrencyComboBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.primaryCurrencyComboBox)
        self.secondaryCurrencyLabel = QtWidgets.QLabel(AddExchangeRateDialog)
        self.secondaryCurrencyLabel.setObjectName("secondaryCurrencyLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.secondaryCurrencyLabel)
        self.secondaryCurrencyComboBox = QtWidgets.QComboBox(AddExchangeRateDialog)
        self.secondaryCurrencyComboBox.setObjectName("secondaryCurrencyComboBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.secondaryCurrencyComboBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(AddExchangeRateDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AddExchangeRateDialog)
        QtCore.QMetaObject.connectSlotsByName(AddExchangeRateDialog)

    def retranslateUi(self, AddExchangeRateDialog):
        _translate = QtCore.QCoreApplication.translate
        AddExchangeRateDialog.setWindowTitle(_translate("AddExchangeRateDialog", "Add Exchange Rate"))
        self.primaryCurrencyLabel.setText(_translate("AddExchangeRateDialog", "Primary currency"))
        self.secondaryCurrencyLabel.setText(_translate("AddExchangeRateDialog", "Secondary currency"))
