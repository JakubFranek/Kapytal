# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\dialogs\account_group_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_AccountGroupDialog(object):
    def setupUi(self, AccountGroupDialog):
        AccountGroupDialog.setObjectName("AccountGroupDialog")
        AccountGroupDialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        AccountGroupDialog.resize(278, 135)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AccountGroupDialog.sizePolicy().hasHeightForWidth())
        AccountGroupDialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(AccountGroupDialog)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.currentPathLabel = QtWidgets.QLabel(AccountGroupDialog)
        self.currentPathLabel.setObjectName("currentPathLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.currentPathLabel)
        self.currentPathLineEdit = QtWidgets.QLineEdit(AccountGroupDialog)
        self.currentPathLineEdit.setObjectName("currentPathLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.currentPathLineEdit)
        self.positionLabel = QtWidgets.QLabel(AccountGroupDialog)
        self.positionLabel.setObjectName("positionLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.positionLabel)
        self.positionSpinBox = QtWidgets.QSpinBox(AccountGroupDialog)
        self.positionSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.positionSpinBox.setMinimum(1)
        self.positionSpinBox.setObjectName("positionSpinBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.positionSpinBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(AccountGroupDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AccountGroupDialog)
        QtCore.QMetaObject.connectSlotsByName(AccountGroupDialog)

    def retranslateUi(self, AccountGroupDialog):
        _translate = QtCore.QCoreApplication.translate
        AccountGroupDialog.setWindowTitle(_translate("AccountGroupDialog", "Dialog"))
        self.currentPathLabel.setText(_translate("AccountGroupDialog", "Current path"))
        self.positionLabel.setText(_translate("AccountGroupDialog", "Position"))
