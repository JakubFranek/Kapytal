# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\dialogs\set_exchange_rate_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SetExchangeRateDialog(object):
    def setupUi(self, SetExchangeRateDialog):
        SetExchangeRateDialog.setObjectName("SetExchangeRateDialog")
        SetExchangeRateDialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        SetExchangeRateDialog.resize(229, 106)
        SetExchangeRateDialog.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.verticalLayout = QtWidgets.QVBoxLayout(SetExchangeRateDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.exchangeRateLabel = QtWidgets.QLabel(SetExchangeRateDialog)
        self.exchangeRateLabel.setObjectName("exchangeRateLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.exchangeRateLabel)
        self.dateLabel = QtWidgets.QLabel(SetExchangeRateDialog)
        self.dateLabel.setObjectName("dateLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.dateLabel)
        self.exchangeRateDoubleSpinBox = QtWidgets.QDoubleSpinBox(SetExchangeRateDialog)
        self.exchangeRateDoubleSpinBox.setProperty("showGroupSeparator", True)
        self.exchangeRateDoubleSpinBox.setDecimals(9)
        self.exchangeRateDoubleSpinBox.setObjectName("exchangeRateDoubleSpinBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.exchangeRateDoubleSpinBox)
        self.dateEdit = QtWidgets.QDateEdit(SetExchangeRateDialog)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setObjectName("dateEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dateEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(SetExchangeRateDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SetExchangeRateDialog)
        QtCore.QMetaObject.connectSlotsByName(SetExchangeRateDialog)

    def retranslateUi(self, SetExchangeRateDialog):
        _translate = QtCore.QCoreApplication.translate
        SetExchangeRateDialog.setWindowTitle(_translate("SetExchangeRateDialog", "Set Exchange Rate"))
        self.exchangeRateLabel.setText(_translate("SetExchangeRateDialog", "Exchange Rate"))
        self.dateLabel.setText(_translate("SetExchangeRateDialog", "Date"))