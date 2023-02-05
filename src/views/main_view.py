import logging
import os
import sys

from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR, QDir, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox

from src.views.account_tree import AccountTree
from src.views.ui_files.Ui_main_window import Ui_MainWindow


class MainView(QMainWindow, Ui_MainWindow):
    signal_exit = pyqtSignal()
    signal_open_currency_form = pyqtSignal()
    signal_save = pyqtSignal()
    signal_save_as = pyqtSignal()
    signal_open = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.initial_setup()

    def get_save_path(self) -> str:
        return QFileDialog.getSaveFileName(self, filter="JSON file (*.json)")[0]

    def get_open_path(self) -> str:
        return QFileDialog.getOpenFileName(self, filter="JSON file (*.json)")[0]

    def ask_save_before_quit(self) -> bool | None:
        message_box = QMessageBox(
            QMessageBox.Icon.Question,
            "Save changes before quitting?",
            (
                "The data has been changed since the last save.\n"
                "Do you want to save before quitting?"
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
        self, current_file_path: str | None, unsaved_changes: bool
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
            self.setWindowTitle(f"Kapytal v{version} - " + current_file_path + star_str)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.signal_exit.emit()
        event.ignore()

    def show_about(self) -> None:
        logging.info("Showing About dialog")
        app = QApplication.instance()
        version = app.applicationVersion()
        text = (
            "<html>"
            "<b>Kapytal</b> - a tool for managing personal and household finances<br/>"
            "Source code and documentation available on "
            "<a href=https://github.com/JakubFranek/Kapytal>"
            "Kapytal GitHub repository</a><br/>"
            "Released under <a href=https://www.gnu.org/licenses/gpl-3.0.html>"
            "GNU General Public Licence v3.0</a><br/>"
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
            "Custom icons in <tt>Kapytal/resources/icons/icons-custom</tt> "
            "are modified Fugue Icons.<br/>"
            "</html"
        )
        message_box = QMessageBox(self)
        message_box.setWindowTitle("About Kapytal")
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setTextFormat(Qt.TextFormat.RichText)
        message_box.setText(text)
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        message_box.exec()
        logging.info("Closing About dialog")

    def initial_setup(self) -> None:
        QDir.addSearchPath(
            "icons_24",
            os.path.join(QDir.currentPath(), "resources/icons/icons-24"),
        )
        QDir.addSearchPath(
            "icons_16",
            os.path.join(QDir.currentPath(), "resources/icons/icons-16"),
        )
        QDir.addSearchPath(
            "icons_custom",
            os.path.join(QDir.currentPath(), "resources/icons/icons-custom"),
        )

        self.setupUi(self)
        self.account_tree = AccountTree(self)
        self.verticalLayoutTree.addWidget(self.account_tree)

        app_icon = QIcon()
        app_icon.addFile("icons_custom:coin-k.png", QSize(24, 24))
        app_icon.addFile("icons_custom:coin-k-small.png", QSize(16, 16))
        self.setWindowIcon(app_icon)

        self.actionOpen_File.setIcon(QIcon("icons_16:folder-open-document.png"))
        self.actionSave.setIcon(QIcon("icons_16:disk.png"))
        self.actionSave_As.setIcon(QIcon("icons_16:disks.png"))
        self.actionCurrencies_and_Exchange_Rates.setIcon(QIcon("icons_16:currency.png"))
        self.actionQuit.setIcon(QIcon("icons_16:door-open-out.png"))
        self.actionSecurities.setIcon(QIcon("icons_16:certificate.png"))
        self.actionCategories.setIcon(QIcon("icons_16:category.png"))
        self.actionTags.setIcon(QIcon("icons_16:tag.png"))
        self.actionPayees.setIcon(QIcon("icons_16:user-silhouette.png"))
        self.actionSettings.setIcon(QIcon("icons_16:gear.png"))
        self.actionAbout.setIcon(QIcon("icons_16:information.png"))

        self.actionCurrencies_and_Exchange_Rates.triggered.connect(
            self.signal_open_currency_form.emit
        )
        self.actionSave.triggered.connect(self.signal_save.emit)
        self.actionSave_As.triggered.connect(self.signal_save_as.emit)
        self.actionOpen_File.triggered.connect(self.signal_open.emit)
        self.actionQuit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.show_about)

        self.toolButton_expandAll.setDefaultAction(self.account_tree.actionExpand_All)
        self.toolButton_collapseAll.setDefaultAction(
            self.account_tree.actionCollapse_All
        )
