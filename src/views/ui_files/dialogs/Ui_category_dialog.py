# Form implementation generated from reading ui file 'd:\Coding\Kapytal\src\views\ui_files\category_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_CategoryDialog(object):
    def setupUi(self, CategoryDialog):
        CategoryDialog.setObjectName("CategoryDialog")
        CategoryDialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        CategoryDialog.resize(278, 165)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CategoryDialog.sizePolicy().hasHeightForWidth())
        CategoryDialog.setSizePolicy(sizePolicy)
        CategoryDialog.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedKingdom))
        self.verticalLayout = QtWidgets.QVBoxLayout(CategoryDialog)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.currentPathLabel = QtWidgets.QLabel(CategoryDialog)
        self.currentPathLabel.setObjectName("currentPathLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.currentPathLabel)
        self.currentPathLineEdit = QtWidgets.QLineEdit(CategoryDialog)
        self.currentPathLineEdit.setObjectName("currentPathLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.currentPathLineEdit)
        self.pathLabel = QtWidgets.QLabel(CategoryDialog)
        self.pathLabel.setObjectName("pathLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.pathLabel)
        self.pathLineEdit = QtWidgets.QLineEdit(CategoryDialog)
        self.pathLineEdit.setObjectName("pathLineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.pathLineEdit)
        self.positionLabel = QtWidgets.QLabel(CategoryDialog)
        self.positionLabel.setObjectName("positionLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.positionLabel)
        self.positionSpinBox = QtWidgets.QSpinBox(CategoryDialog)
        self.positionSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.positionSpinBox.setMinimum(1)
        self.positionSpinBox.setObjectName("positionSpinBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.positionSpinBox)
        self.typeLabel = QtWidgets.QLabel(CategoryDialog)
        self.typeLabel.setObjectName("typeLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.typeLabel)
        self.typeLineEdit = QtWidgets.QLineEdit(CategoryDialog)
        self.typeLineEdit.setReadOnly(True)
        self.typeLineEdit.setObjectName("typeLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.typeLineEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(CategoryDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(CategoryDialog)
        QtCore.QMetaObject.connectSlotsByName(CategoryDialog)

    def retranslateUi(self, CategoryDialog):
        _translate = QtCore.QCoreApplication.translate
        CategoryDialog.setWindowTitle(_translate("CategoryDialog", "Dialog"))
        self.currentPathLabel.setText(_translate("CategoryDialog", "Current path"))
        self.pathLabel.setText(_translate("CategoryDialog", "Path"))
        self.positionLabel.setText(_translate("CategoryDialog", "Position"))
        self.typeLabel.setText(_translate("CategoryDialog", "Type"))
