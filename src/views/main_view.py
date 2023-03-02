import logging
import sys
from collections.abc import Collection
from pathlib import Path

from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR, QDir, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QCloseEvent, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLineEdit,
    QMainWindow,
    QMessageBox,
)

from src.views.account_tree import AccountTree
from src.views.ui_files.Ui_main_window import Ui_MainWindow

# IDEA: swap QToolButtons for QPushButtons (see how drop down menu works though)
# TODO: open recent file (save in separate file)


class MainView(QMainWindow, Ui_MainWindow):
    signal_exit = pyqtSignal()

    signal_open_currency_form = pyqtSignal()
    signal_open_security_form = pyqtSignal()
    signal_open_payee_form = pyqtSignal()
    signal_open_tag_form = pyqtSignal()
    signal_open_category_form = pyqtSignal()
    signal_open_settings_form = pyqtSignal()

    signal_save_file = pyqtSignal()
    signal_save_file_as = pyqtSignal()
    signal_open_file = pyqtSignal()
    signal_open_recent_file = pyqtSignal(str)
    signal_clear_recent_files = pyqtSignal()
    signal_close_file = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._initial_setup()

    def get_save_path(self) -> str:
        return QFileDialog.getSaveFileName(self, filter="JSON file (*.json)")[0]

    def get_open_path(self) -> str:
        return QFileDialog.getOpenFileName(self, filter="JSON file (*.json)")[0]

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
        message_box.setWindowIcon(QIcon("icons_16:question.png"))
        message_box.setDefaultButton(QMessageBox.StandardButton.Cancel)
        reply = message_box.exec()
        if reply == QMessageBox.StandardButton.Yes:
            return True
        if reply == QMessageBox.StandardButton.No:
            return False
        return None

    def set_save_status(
        self, current_file_path: Path | None, unsaved_changes: bool
    ) -> None:
        if unsaved_changes is True:
            self.actionSave.setIcon(QIcon("icons_16:disk--exclamation.png"))
            star_str = "*"
        else:
            self.actionSave.setIcon(QIcon("icons_16:disk.png"))
            star_str = ""

        app = QApplication.instance()
        version = app.applicationVersion()

        if current_file_path is None:
            self.actionSave.setEnabled(False)
            self.setWindowTitle(f"Kapytal v{version}")
        else:
            self.actionSave.setEnabled(True)
            self.setWindowTitle(
                f"Kapytal v{version} - " + str(current_file_path) + star_str
            )

    def show_status_message(self, message: str, msecs: int) -> None:
        self.statusBar().showMessage(message, msecs)

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
                lambda _, path=path: self.signal_open_recent_file.emit(  # noqa : U101
                    path
                )
            )
            actions = self.menuRecent_Files.actions()
            before_action = actions[0] if actions else None
            self.menuRecent_Files.insertAction(before_action, action)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.signal_exit.emit()
        event.ignore()

    def show_about(self) -> None:
        logging.debug("Showing About dialog")
        app = QApplication.instance()
        version = app.applicationVersion()
        text = (
            "<html>"
            "<b>Kapytal</b> - <em>a tool for managing personal and "
            "household finances</em><br/>"
            "Source code and documentation available on "
            "<a href=https://github.com/JakubFranek/Kapytal>"
            "Kapytal GitHub repository</a>.<br/>"
            "Published under <a href=https://www.gnu.org/licenses/gpl-3.0.html>"
            "GNU General Public Licence v3.0</a>.<br/>"
            "<br/>"
            "<b>Version info</b><br/>"
            f"Kapytal {version}<br/>"
            f"Python {sys.version}<br/>"
            f"Qt {QT_VERSION_STR}<br/>"
            f"PyQt {PYQT_VERSION_STR}<br/>"
            "<br/>"
            "<b>Icons info</b><br/>"
            "<a href=https://p.yusukekamiyamane.com>Fugue Icons set</a> by "
            "Yusuke Kamiyamane.<br/>"
            "Custom icons located in <tt>Kapytal/resources/icons/icons-custom</tt> "
            "are modifications of existing Fugue Icons.<br/>"
            "</html"
        )
        message_box = QMessageBox(self)
        message_box.setWindowTitle("About Kapytal")
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setTextFormat(Qt.TextFormat.RichText)
        message_box.setText(text)
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        message_box.exec()
        logging.debug("Closing About dialog")

    def _initial_setup(self) -> None:
        QDir.addSearchPath(
            "icons_24",
            str(Path(QDir.currentPath() + "/resources/icons/icons-24")),
        )
        QDir.addSearchPath(
            "icons_16",
            str(Path(QDir.currentPath() + "/resources/icons/icons-16")),
        )
        QDir.addSearchPath(
            "icons_custom",
            str(Path(QDir.currentPath() + "/resources/icons/icons-custom")),
        )

        self.setupUi(self)
        self.account_tree = AccountTree(self)
        self.verticalLayoutTree.addWidget(self.account_tree)

        app_icon = QIcon()
        app_icon.addFile("icons_custom:coin-k.png", QSize(24, 24))
        app_icon.addFile("icons_custom:coin-k-small.png", QSize(16, 16))
        self.setWindowIcon(app_icon)

        self.actionFilterTransactions = QAction(self)

        self.actionOpen_File.setIcon(QIcon("icons_16:folder-open-document.png"))
        self.actionSave.setIcon(QIcon("icons_16:disk.png"))
        self.actionSave_As.setIcon(QIcon("icons_16:disks.png"))
        self.actionCurrencies_and_Exchange_Rates.setIcon(
            QIcon("icons_custom:currency.png")
        )
        self.actionQuit.setIcon(QIcon("icons_16:door-open-out.png"))
        self.actionSecurities.setIcon(QIcon("icons_16:certificate.png"))
        self.actionCategories.setIcon(QIcon("icons_custom:category.png"))
        self.actionTags.setIcon(QIcon("icons_16:tag.png"))
        self.actionPayees.setIcon(QIcon("icons_16:user-silhouette.png"))
        self.actionSettings.setIcon(QIcon("icons_16:gear.png"))
        self.actionAbout.setIcon(QIcon("icons_16:information.png"))
        self.actionFilterTransactions.setIcon(QIcon("icons_16:funnel.png"))
        self.actionIncome.setIcon(QIcon("icons_custom:coins-plus.png"))
        self.actionExpense.setIcon(QIcon("icons_custom:coins-minus.png"))
        self.actionBuy.setIcon(QIcon("icons_custom:certificate-plus.png"))
        self.actionSell.setIcon(QIcon("icons_custom:certificate-minus.png"))
        self.actionTransfer.setIcon(QIcon("icons_16:arrow-curve-000-left.png"))
        self.actionCashTransfer.setIcon(QIcon("icons_custom:coins-arrow.png"))
        self.actionSecurityTransfer.setIcon(QIcon("icons_custom:certificate-arrow.png"))
        self.actionRefund.setIcon(QIcon("icons_custom:coins-arrow-back.png"))

        self.actionCurrencies_and_Exchange_Rates.triggered.connect(
            self.signal_open_currency_form.emit
        )
        self.actionSecurities.triggered.connect(self.signal_open_security_form.emit)
        self.actionPayees.triggered.connect(self.signal_open_payee_form.emit)
        self.actionTags.triggered.connect(self.signal_open_tag_form.emit)
        self.actionCategories.triggered.connect(self.signal_open_category_form.emit)
        self.actionSettings.triggered.connect(self.signal_open_settings_form.emit)

        self.actionSave.triggered.connect(self.signal_save_file.emit)
        self.actionSave_As.triggered.connect(self.signal_save_file_as.emit)
        self.actionOpen_File.triggered.connect(self.signal_open_file.emit)
        self.actionClear_Recent_File_Menu.triggered.connect(
            self.signal_clear_recent_files.emit
        )
        self.actionClose_File.triggered.connect(self.signal_close_file.emit)

        self.actionQuit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.show_about)

        self.expandAllToolButton.setDefaultAction(self.account_tree.actionExpand_All)
        self.collapseAllToolButton.setDefaultAction(
            self.account_tree.actionCollapse_All
        )
        self.addAccountGroupToolButton.setDefaultAction(
            self.account_tree.actionAdd_Account_Group
        )
        self.addCashAccountToolButton.setDefaultAction(
            self.account_tree.actionAdd_Cash_Account
        )
        self.addSecurityAccountToolButton.setDefaultAction(
            self.account_tree.actionAdd_Security_Account
        )
        self.filterToolButton.setDefaultAction(self.actionFilterTransactions)
        self.buyToolButton.setDefaultAction(self.actionBuy)
        self.sellToolButton.setDefaultAction(self.actionSell)
        self.incomeToolButton.setDefaultAction(self.actionIncome)
        self.expenseToolButton.setDefaultAction(self.actionExpense)
        self.transferToolButton.setIcon(QIcon("icons_16:arrow-curve-000-left.png"))
        self.transferToolButton.addAction(self.actionCashTransfer)
        self.transferToolButton.addAction(self.actionSecurityTransfer)

        self.searchLineEdit.addAction(
            QIcon("icons_16:magnifier.png"), QLineEdit.ActionPosition.LeadingPosition
        )
        self.searchLineEdit.setToolTip(
            (
                "Special characters:\n"
                "* matches zero or more of any characters\n"
                "? matches any single character\n"
                "[...] matches any character within square brackets"
            )
        )
