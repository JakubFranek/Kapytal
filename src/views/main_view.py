import logging
import sys
from collections.abc import Collection
from pathlib import Path

from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QCloseEvent, QIcon, QKeyEvent
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QMessageBox
from src.utilities import constants
from src.views import icons
from src.views.ui_files.Ui_main_window import Ui_MainWindow
from src.views.widgets.account_tree_widget import AccountTreeWidget
from src.views.widgets.transaction_table_widget import TransactionTableWidget


class MainView(QMainWindow, Ui_MainWindow):
    signal_exit = pyqtSignal()

    signal_show_account_tree = pyqtSignal(bool)

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
        message_box.setWindowIcon(icons.question)
        message_box.setDefaultButton(QMessageBox.StandardButton.Cancel)
        reply = message_box.exec()
        if reply == QMessageBox.StandardButton.Yes:
            return True
        if reply == QMessageBox.StandardButton.No:
            return False
        return None

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
                lambda _, path=path: self.signal_open_recent_file.emit(path)
            )
            actions = self.menuRecent_Files.actions()
            before_action = actions[0] if actions else None
            self.menuRecent_Files.insertAction(before_action, action)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self.signal_exit.emit()
        event.ignore()

    def show_about(self) -> None:
        logging.debug("Showing About dialog")
        text = (
            "<html>"
            "<b>Kapytal</b> - <em>a tool for managing personal and "
            "household finances</em><br/>"
            "Source code and documentation available on "
            "<a href=https://github.com/JakubFranek/Kapytal>"
            "Kapytal GitHub repository</a><br/>"
            "Published under <a href=https://www.gnu.org/licenses/gpl-3.0.html>"
            "GNU General Public Licence v3.0</a><br/>"
            "<br/>"
            "<b>Version info</b><br/>"
            f"Kapytal {constants.VERSION}<br/>"
            f"Python {sys.version}<br/>"
            f"Qt {QT_VERSION_STR}<br/>"
            f"PyQt {PYQT_VERSION_STR}<br/>"
            "<br/>"
            "<b>Icons info</b><br/>"
            "<a href=https://p.yusukekamiyamane.com>Fugue Icons set</a> by "
            "Yusuke Kamiyamane.<br/>"
            "Custom icons located in <tt>Kapytal/resources/icons/icons-custom</tt> "
            "are modifications of existing Fugue Icons.<br/><br/>"
            "<em>Dedicated to my wife Soňa</em>"
            "</html>"
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
        icons.setup()

        self.setupUi(self)
        self.account_tree_widget = AccountTreeWidget(self)
        self.transaction_table_widget = TransactionTableWidget(self)
        self.horizontalLayout.addWidget(self.account_tree_widget)
        self.horizontalLayout.addWidget(self.transaction_table_widget)
        self.horizontalLayout.setStretch(1, 1)

        app_icon = QIcon()
        app_icon.addFile("icons_custom:coin-k.png", QSize(24, 24))
        app_icon.addFile("icons_custom:coin-k-small.png", QSize(16, 16))
        self.setWindowIcon(app_icon)

        self.actionFilterTransactions = QAction(self)

        self.actionShow_Hide_Account_Tree.setCheckable(True)
        self.actionShow_Hide_Account_Tree.setChecked(True)

        self.actionOpen_File.setIcon(icons.open_file)
        self.actionSave.setIcon(icons.disk)
        self.actionSave_As.setIcon(icons.disks)
        self.actionCurrencies_and_Exchange_Rates.setIcon(icons.currency)
        self.actionQuit.setIcon(icons.quit_)
        self.actionSecurities.setIcon(icons.security)
        self.actionCategories.setIcon(icons.category)
        self.actionTags.setIcon(icons.tag)
        self.actionPayees.setIcon(icons.payee)
        self.actionSettings.setIcon(icons.settings)
        self.actionAbout.setIcon(icons.about)
        self.actionShow_Hide_Account_Tree.setIcon(icons.account_tree)

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

        self.actionShow_Hide_Account_Tree.triggered.connect(
            lambda checked: self.signal_show_account_tree.emit(checked)
        )
        self.actionQuit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.show_about)

    def keyPressEvent(self, a0: QKeyEvent) -> None:  # noqa: N802
        if a0.key() == Qt.Key.Key_Escape:
            logging.debug(f"Closing {self.__class__.__name__}")
            self.close()
        return super().keyPressEvent(a0)
