# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\dialogs\cash_account_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_CashAccountDialog(object):
    def setupUi(self, CashAccountDialog):
        CashAccountDialog.setObjectName("CashAccountDialog")
        CashAccountDialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        CashAccountDialog.resize(272, 196)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CashAccountDialog.sizePolicy().hasHeightForWidth())
        CashAccountDialog.setSizePolicy(sizePolicy)
        CashAccountDialog.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.verticalLayout = QtWidgets.QVBoxLayout(CashAccountDialog)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.currentPathLabel = QtWidgets.QLabel(CashAccountDialog)
        self.currentPathLabel.setObjectName("currentPathLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.currentPathLabel)
        self.currentPathLineEdit = QtWidgets.QLineEdit(CashAccountDialog)
        self.currentPathLineEdit.setObjectName("currentPathLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.currentPathLineEdit)
        self.pathLabel = QtWidgets.QLabel(CashAccountDialog)
        self.pathLabel.setObjectName("pathLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.pathLabel)
        self.pathLineEdit = QtWidgets.QLineEdit(CashAccountDialog)
        self.pathLineEdit.setObjectName("pathLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.pathLineEdit)
        self.positionLabel = QtWidgets.QLabel(CashAccountDialog)
        self.positionLabel.setObjectName("positionLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.positionLabel)
        self.positionSpinBox = QtWidgets.QSpinBox(CashAccountDialog)
        self.positionSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.positionSpinBox.setMinimum(1)
        self.positionSpinBox.setObjectName("positionSpinBox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.positionSpinBox)
        self.currencyLabel = QtWidgets.QLabel(CashAccountDialog)
        self.currencyLabel.setObjectName("currencyLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.currencyLabel)
        self.initialBalanceLabel = QtWidgets.QLabel(CashAccountDialog)
        self.initialBalanceLabel.setObjectName("initialBalanceLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.initialBalanceLabel)
        self.currencyComboBox = QtWidgets.QComboBox(CashAccountDialog)
        self.currencyComboBox.setObjectName("currencyComboBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.currencyComboBox)
        self.initialBalanceDoubleSpinBox = QtWidgets.QDoubleSpinBox(CashAccountDialog)
        self.initialBalanceDoubleSpinBox.setProperty("showGroupSeparator", True)
        self.initialBalanceDoubleSpinBox.setObjectName("initialBalanceDoubleSpinBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.initialBalanceDoubleSpinBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(CashAccountDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(CashAccountDialog)
        QtCore.QMetaObject.connectSlotsByName(CashAccountDialog)

    def retranslateUi(self, CashAccountDialog):
        _translate = QtCore.QCoreApplication.translate
        CashAccountDialog.setWindowTitle(_translate("CashAccountDialog", "Dialog"))
        self.currentPathLabel.setText(_translate("CashAccountDialog", "Current path"))
        self.pathLabel.setText(_translate("CashAccountDialog", "Path"))
        self.positionLabel.setText(_translate("CashAccountDialog", "Position"))
        self.currencyLabel.setText(_translate("CashAccountDialog", "Currency"))
        self.initialBalanceLabel.setText(_translate("CashAccountDialog", "Initial balance"))
