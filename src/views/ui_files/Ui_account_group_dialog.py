# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\account_group_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_AccountGroupDialog(object):
    def setupUi(self, AccountGroupDialog):
        AccountGroupDialog.setObjectName("AccountGroupDialog")
        AccountGroupDialog.resize(272, 151)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AccountGroupDialog.sizePolicy().hasHeightForWidth())
        AccountGroupDialog.setSizePolicy(sizePolicy)
        AccountGroupDialog.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.formLayout = QtWidgets.QFormLayout(AccountGroupDialog)
        self.formLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)
        self.formLayout.setObjectName("formLayout")
        self.pathLabel = QtWidgets.QLabel(AccountGroupDialog)
        self.pathLabel.setObjectName("pathLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.pathLabel)
        self.pathLineEdit = QtWidgets.QLineEdit(AccountGroupDialog)
        self.pathLineEdit.setObjectName("pathLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.pathLineEdit)
        self.positionLabel = QtWidgets.QLabel(AccountGroupDialog)
        self.positionLabel.setObjectName("positionLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.positionLabel)
        self.buttonBox = QtWidgets.QDialogButtonBox(AccountGroupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.buttonBox)
        self.positionSpinBox = QtWidgets.QSpinBox(AccountGroupDialog)
        self.positionSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.positionSpinBox.setMinimum(1)
        self.positionSpinBox.setObjectName("positionSpinBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.positionSpinBox)

        self.retranslateUi(AccountGroupDialog)
        self.buttonBox.accepted.connect(AccountGroupDialog.accept) # type: ignore
        self.buttonBox.rejected.connect(AccountGroupDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(AccountGroupDialog)

    def retranslateUi(self, AccountGroupDialog):
        _translate = QtCore.QCoreApplication.translate
        AccountGroupDialog.setWindowTitle(_translate("AccountGroupDialog", "Dialog"))
        self.pathLabel.setText(_translate("AccountGroupDialog", "Path"))
        self.positionLabel.setText(_translate("AccountGroupDialog", "Position"))
