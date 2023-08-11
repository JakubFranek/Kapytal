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
        SecurityDialog.resize(285, 207)
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
        self.unitDoubleSpinBox = QtWidgets.QDoubleSpinBox(SecurityDialog)
        self.unitDoubleSpinBox.setDecimals(9)
        self.unitDoubleSpinBox.setMaximum(1000000.0)
        self.unitDoubleSpinBox.setObjectName("unitDoubleSpinBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.unitDoubleSpinBox)
        self.currencyLabel = QtWidgets.QLabel(SecurityDialog)
        self.currencyLabel.setObjectName("currencyLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.currencyLabel)
        self.currencyComboBox = QtWidgets.QComboBox(SecurityDialog)
        self.currencyComboBox.setObjectName("currencyComboBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.currencyComboBox)
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
        self.unitLabel.setText(_translate("SecurityDialog", "Unit"))
        self.unitDoubleSpinBox.setToolTip(_translate("SecurityDialog", "Enter smallest unit of Security (for example 1 share, or 0.01 for 1 percent etc)"))
        self.currencyLabel.setText(_translate("SecurityDialog", "Currency"))
