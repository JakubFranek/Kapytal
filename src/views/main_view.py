import logging
from collections.abc import Collection
from pathlib import Path

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QCloseEvent, QIcon, QKeyEvent
from PyQt6.QtWidgets import QDateTimeEdit, QFileDialog, QMainWindow, QMessageBox
from src.utilities import constants
from src.views import icons
from src.views.dialogs.about_dialog import AboutDialog
from src.views.ui_files.Ui_main_window import Ui_MainWindow
from src.views.utilities.helper_functions import overflowing_keyPressEvent
from src.views.widgets.account_tree_widget import AccountTreeWidget
from src.views.widgets.transaction_table_widget import TransactionTableWidget


class MainView(QMainWindow, Ui_MainWindow):
    signal_exit = pyqtSignal()

    signal_show_account_tree = pyqtSignal(bool)
    signal_show_transaction_table = pyqtSignal(bool)

    signal_open_currency_form = pyqtSignal()
    signal_open_security_form = pyqtSignal()
    signal_open_payee_form = pyqtSignal()
    signal_open_tag_form = pyqtSignal()
    signal_open_category_form = pyqtSignal()
    signal_open_settings_form = pyqtSignal()

    signal_update_quotes = pyqtSignal()

    signal_cash_flow_montly_report = pyqtSignal()
    signal_cash_flow_annual_report = pyqtSignal()
    signal_cash_flow_total_report = pyqtSignal()

    signal_tag_monthly_report = pyqtSignal()
    signal_tag_annual_report = pyqtSignal()

    signal_payee_monthly_report = pyqtSignal()
    signal_payee_annual_report = pyqtSignal()

    signal_category_monthly_report = pyqtSignal()
    signal_category_annual_report = pyqtSignal()

    signal_net_worth_accounts_report = pyqtSignal()
    signal_net_worth_asset_type_report = pyqtSignal()
    signal_net_worth_time_report = pyqtSignal()

    signal_save_file = pyqtSignal()
    signal_save_file_as = pyqtSignal()
    signal_open_file = pyqtSignal()
    signal_open_recent_file = pyqtSignal(str)
    signal_clear_recent_files = pyqtSignal()
    signal_new_file = pyqtSignal()

    signal_open_basic_demo = pyqtSignal()
    signal_open_mortgage_demo = pyqtSignal()
    signal_open_category_template_en = pyqtSignal()
    signal_open_category_template_cz = pyqtSignal()

    signal_open_github = pyqtSignal()
    signal_check_updates = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._initial_setup()

    def set_item_view_update_state(self, *, enabled: bool) -> None:
        """Enables or disables view updates of Account Tree and Transaction Table."""
        self.account_tree_widget.treeView.setUpdatesEnabled(enabled)
        self.transaction_table_widget.tableView.setUpdatesEnabled(enabled)

    def get_save_path(self) -> str:
        return QFileDialog.getSaveFileName(
            self, filter="Encrypted JSON file (*.json.enc);;JSON file (*.json)"
        )[0]

    def get_open_path(self) -> str:
        return QFileDialog.getOpenFileName(
            self, filter="All JSON files (*.json *.json.enc)"
        )[0]

    def ask_save_before_close(self) -> bool | None:
        """True: save & close \n False: close \n None: cancel"""

        message_box = QMessageBox(
            QMessageBox.Icon.Question,
            "Save changes before closing?",
            (
                "The data has been changed since the last save.\n"
                "Do you want to save before closing?"
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel
            ),
            self,
        )
        message_box.setWindowIcon(icons.question)
        message_box.setDefaultButton(QMessageBox.StandardButton.Cancel)
        reply = message_box.exec()
        if reply == QMessageBox.StandardButton.Yes:
            return True
        if reply == QMessageBox.StandardButton.No:
            return False
        return None

    def confirm_close(self) -> bool | None:
        """True: close \n False: cancel"""

        message_box = QMessageBox(
            QMessageBox.Icon.Question,
            "Quit?",
            "Do you want to quit Kapytal?",
            (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No),
            self,
        )
        message_box.setWindowIcon(icons.question)
        message_box.setDefaultButton(QMessageBox.StandardButton.No)
        reply = message_box.exec()
        return reply == QMessageBox.StandardButton.Yes

    def set_save_status(self, current_file_path: Path | None, *, unsaved: bool) -> None:
        if unsaved is True:
            self.actionSave.setIcon(icons.disk_warning)
            star_str = "*"
        else:
            self.actionSave.setIcon(icons.disk)
            star_str = ""

        if current_file_path is None:
            self.actionSave.setEnabled(False)
            self.setWindowTitle(f"Kapytal v{constants.VERSION}")
        else:
            self.actionSave.setEnabled(True)
            self.setWindowTitle(
                f"Kapytal v{constants.VERSION} - " + str(current_file_path) + star_str
            )

    def set_recent_files_menu(self, recent_files: Collection[str]) -> None:
        if len(recent_files) == 0:
            self.menuRecent_Files.setEnabled(False)
            return
        self.menuRecent_Files.setEnabled(True)

        # Clear actions
        actions = self.menuRecent_Files.actions()
        for action in actions:
            if action.text() == "Clear Menu" or action.isSeparator():
                continue
            self.menuRecent_Files.removeAction(action)

        # Add actions
        for path in reversed(recent_files):
            action = QAction(path, self)
            action.triggered.connect(
                lambda _, path=path: self.signal_open_recent_file.emit(path)
            )
            actions = self.menuRecent_Files.actions()
            before_action = actions[0] if actions else None
            self.menuRecent_Files.insertAction(before_action, action)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.signal_exit.emit()
        event.ignore()

    def show_about(self) -> None:
        logging.debug("Showing About dialog")
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def _initial_setup(self) -> None:
        QDateTimeEdit.keyPressEvent = overflowing_keyPressEvent
        icons.setup()

        self.setupUi(self)
        self.account_tree_widget = AccountTreeWidget(self)
        self.transaction_table_widget = TransactionTableWidget(self)
        self.horizontalLayout.addWidget(self.account_tree_widget)
        self.horizontalLayout.addWidget(self.transaction_table_widget)

        app_icon = QIcon()
        app_icon.addFile("icons_custom:coin-k.png", QSize(24, 24))
        app_icon.addFile("icons_custom:coin-k-small.png", QSize(16, 16))
        self.setWindowIcon(app_icon)

        self.actionFilterTransactions = QAction(self)

        self.actionShow_Hide_Account_Tree.setCheckable(True)
        self.actionShow_Hide_Account_Tree.setChecked(True)

        self.actionShow_Hide_Transaction_Table.setCheckable(True)
        self.actionShow_Hide_Transaction_Table.setChecked(True)

        self.actionNew_File.setIcon(icons.document_plus)
        self.actionOpen_File.setIcon(icons.open_file)
        self.actionSave.setIcon(icons.disk)
        self.actionSave_As.setIcon(icons.disks)
        self.actionCurrencies.setIcon(icons.currency)
        self.actionQuit.setIcon(icons.quit_)
        self.actionSecurities.setIcon(icons.security)
        self.actionCategories.setIcon(icons.category)
        self.actionTags.setIcon(icons.tag)
        self.actionPayees.setIcon(icons.payee)
        self.actionSettings.setIcon(icons.settings)
        self.actionAbout.setIcon(icons.about)
        self.actionShow_Hide_Account_Tree.setIcon(icons.account_tree)
        self.actionShow_Hide_Transaction_Table.setIcon(icons.table)
        self.actionUpdate_Quotes.setIcon(icons.refresh)

        self.menuNet_Worth.setIcon(icons.pie_chart)
        self.menuCash_Flow.setIcon(icons.bar_chart)
        self.menuCategories.setIcon(icons.category)
        self.menuTags.setIcon(icons.tag)
        self.menuPayees.setIcon(icons.payee)

        self.actionOpen_Kapytal_GitHub_page.setIcon(icons.globe)

        self._connect_actions_to_signals()

    def _connect_actions_to_signals(self) -> None:
        self.actionCurrencies.triggered.connect(self.signal_open_currency_form.emit)
        self.actionSecurities.triggered.connect(self.signal_open_security_form.emit)
        self.actionPayees.triggered.connect(self.signal_open_payee_form.emit)
        self.actionTags.triggered.connect(self.signal_open_tag_form.emit)
        self.actionCategories.triggered.connect(self.signal_open_category_form.emit)
        self.actionSettings.triggered.connect(self.signal_open_settings_form.emit)

        self.actionBasicDemo.triggered.connect(self.signal_open_basic_demo.emit)
        self.actionMortgage_Demo.triggered.connect(self.signal_open_mortgage_demo.emit)
        self.actionCategory_Template_EN.triggered.connect(
            self.signal_open_category_template_en.emit
        )
        self.actionCategory_Template_CZ.triggered.connect(
            self.signal_open_category_template_cz.emit
        )

        self.actionSave.triggered.connect(self.signal_save_file.emit)
        self.actionSave_As.triggered.connect(self.signal_save_file_as.emit)
        self.actionOpen_File.triggered.connect(self.signal_open_file.emit)
        self.actionClear_Recent_File_Menu.triggered.connect(
            self.signal_clear_recent_files.emit
        )
        self.actionNew_File.triggered.connect(self.signal_new_file.emit)

        self.actionShow_Hide_Account_Tree.triggered.connect(
            lambda checked: self.signal_show_account_tree.emit(checked)
        )
        self.actionShow_Hide_Transaction_Table.triggered.connect(
            lambda checked: self.signal_show_transaction_table.emit(checked)
        )
        self.actionQuit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.show_about)

        self.actionCash_Flow_Monthly.triggered.connect(
            self.signal_cash_flow_montly_report.emit
        )
        self.actionCash_Flow_Annual.triggered.connect(
            self.signal_cash_flow_annual_report.emit
        )
        self.actionCash_Flow_Total.triggered.connect(
            self.signal_cash_flow_total_report.emit
        )

        self.actionTag_Report_Monthly.triggered.connect(
            self.signal_tag_monthly_report.emit
        )
        self.actionTag_Report_Annual.triggered.connect(
            self.signal_tag_annual_report.emit
        )

        self.actionPayee_Report_Monthly.triggered.connect(
            self.signal_payee_monthly_report.emit
        )
        self.actionPayee_Report_Annual.triggered.connect(
            self.signal_payee_annual_report.emit
        )

        self.actionCategory_Report_Monthly.triggered.connect(
            self.signal_category_monthly_report.emit
        )
        self.actionCategory_Report_Annual.triggered.connect(
            self.signal_category_annual_report.emit
        )

        self.actionNet_Worth_Accounts_Report.triggered.connect(
            self.signal_net_worth_accounts_report.emit
        )
        self.actionNet_Worth_Asset_Type_Report.triggered.connect(
            self.signal_net_worth_asset_type_report.emit
        )
        self.actionNet_Worth_Time_Report.triggered.connect(
            self.signal_net_worth_time_report.emit
        )

        self.actionUpdate_Quotes.triggered.connect(self.signal_update_quotes.emit)

        self.actionOpen_Kapytal_GitHub_page.triggered.connect(
            self.signal_open_github.emit
        )

        self.actionCheck_for_Updates.triggered.connect(
            lambda: self.signal_check_updates.emit()
        )

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key.Key_Escape:
            logging.debug(f"Closing {self.__class__.__name__}")
            self.close()
        return super().keyPressEvent(a0)
