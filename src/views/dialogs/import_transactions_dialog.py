import logging
from collections.abc import Collection

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractButton,
    QDialogButtonBox,
    QFileDialog,
    QLineEdit,
    QWidget,
)
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_import_transactions_dialog import (
    Ui_ImportTransactionsDialog,
)
from src.views.utilities.message_box_functions import show_info_box
from src.views.widgets.smart_combo_box import SmartComboBox

FILTER_TRANSACTION_DATA = "CSV Files (*.csv)"
FILTER_COLUMN_MAP = "JSON Files (*.json)"
FILTER_PAYEE_MAP = "JSON Files (*.json)"


class ImportTransactionsDialog(CustomDialog, Ui_ImportTransactionsDialog):
    signal_ok = pyqtSignal()

    def __init__(
        self,
        parent: QWidget,
        cash_account_paths: Collection[str],
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.resize(320, 80)
        self.setWindowIcon(icons.document_import)

        self.cashAccountComboBox = SmartComboBox(parent=self)
        self.cashAccountComboBox.load_items(
            cash_account_paths, icons.cash_account, "Select Cash Account"
        )
        self.gridLayout.addWidget(self.cashAccountComboBox, 0, 1, 1, 1)
        self.setTabOrder(self.cashAccountComboBox, self.transactionDataLineEdit)
        self.cashAccountComboBox.setFocus(Qt.FocusReason.OtherFocusReason)

        self.actionSelect_Transaction_Data_File.setIcon(icons.open_file)
        self.actionSelect_Transaction_Data_File.triggered.connect(
            lambda: self._select_file(
                self.transactionDataLineEdit, FILTER_TRANSACTION_DATA
            )
        )
        self.transactionDataToolButton.setDefaultAction(
            self.actionSelect_Transaction_Data_File
        )

        self.actionSelect_Import_Profile_File.setIcon(icons.open_file)
        self.actionSelect_Import_Profile_File.triggered.connect(
            lambda: self._select_file(self.importProfileLineEdit, FILTER_COLUMN_MAP)
        )
        self.importProfileToolButton.setDefaultAction(
            self.actionSelect_Import_Profile_File
        )

        self.actionSelect_Payee_Mapping_File.setIcon(icons.open_file)
        self.actionSelect_Payee_Mapping_File.triggered.connect(
            lambda: self._select_file(self.payeeMappingLineEdit, FILTER_PAYEE_MAP)
        )
        self.payeeMappingToolButton.setDefaultAction(
            self.actionSelect_Payee_Mapping_File
        )

        self.buttonBox.clicked.connect(self._handle_button_box_click)

    def _select_file(self, line_edit: QLineEdit, file_filter: str) -> str:
        path = QFileDialog.getOpenFileName(self, filter=file_filter)[0]
        line_edit.setText(path)

    @property
    def path_transaction_data(self) -> str:
        return self.transactionDataLineEdit.text()

    @property
    def path_import_profile(self) -> str:
        return self.importProfileLineEdit.text()

    @property
    def path_payee_mapping(self) -> str:
        return self.payeeMappingLineEdit.text()

    @property
    def cash_account(self) -> str:
        return self.cashAccountComboBox.currentText()

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_ok.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.reject()
        elif role == QDialogButtonBox.ButtonRole.HelpRole:
            self._show_help()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")

    def reject(self) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().reject()

    def _show_help(self) -> None:  # TODO: create help text
        text = (
            "<html>"
            "To update quotes, first select the Exchange Rates and Securities you wish "
            "to update, and then click the <b>Download selected</b> button."
            "<br/>"
            "Review the downloaded quotes, deselect the quotes you do not wish to "
            "save, and finally click the <b>Save selected</b> button."
            "<br/>"
            "You can always view, edit or delete the quotes in the <b>Currencies and "
            "Exchange Rates</b> form or in the <b>Securities</b> form respectively."
            "<br/><br/>"
            "Quotes are downloaded from Yahoo Finance."
            "<br/>"
            "If you encounter issues with the quote update, make sure the Exchange "
            "Rates and Securities you selected are available on Yahoo Finance."
            "<br/><br/>"
            "When querying Security prices from Yahoo Finance API, the Security Symbol "
            "strings are used. Securities with empty Symbol string are not eligible "
            "for quote update."
            "<br/><br/>"
            "When querying Exchange Rates, two attempts are made. "
            "<br/>"
            "First, ticker <tt>AAABBB=X</tt> is attempted (where <tt>AAA</tt> is the "
            "primary Currency code and <tt>BBB</tt> is the secondary Currency code). "
            "This ticker format usually works for Exchange Rates between government "
            "issued currencies."
            "<br/>"
            "If the first attempt fails, ticker <tt>AAA-BBB</tt> is attempted. "
            "This ticker format usually works for cryptocurrencies."
            "</html>"
        )
        show_info_box(self, text, "Update Quotes Help")
