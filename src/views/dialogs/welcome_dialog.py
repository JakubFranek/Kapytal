import os
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QCloseEvent, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QMenu,
    QPushButton,
    QWidget,
)
from src.utilities import constants
from src.views import colors, icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_welcome_dialog import Ui_WelcomeDialog

PATH_STRING_MAX_LENGTH = 30


class WelcomeDialog(CustomDialog, Ui_WelcomeDialog):
    signal_new_file = pyqtSignal()
    signal_open_recent_file = pyqtSignal()
    signal_open_file = pyqtSignal()
    signal_open_docs = pyqtSignal()
    signal_quit = pyqtSignal()
    signal_close = pyqtSignal()

    signal_open_demo_basic = pyqtSignal()
    signal_open_demo_mortgage = pyqtSignal()
    signal_open_template_category_en = pyqtSignal()
    signal_open_template_category_cz = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)

        if colors.color_scheme == Qt.ColorScheme.Dark:
            self.pixmap = QPixmap(
                str(constants.app_root_path / "resources/images/welcome_dark_mode.png")
            ).scaledToWidth(512, Qt.TransformationMode.SmoothTransformation)
        else:
            self.pixmap = QPixmap(
                str(constants.app_root_path / "resources/images/welcome_light_mode.png")
            ).scaledToWidth(512, Qt.TransformationMode.SmoothTransformation)

        screen = QApplication.primaryScreen()
        dpr = screen.devicePixelRatio()

        pixmap = self.pixmap.scaledToWidth(
            int(512 * dpr), Qt.TransformationMode.SmoothTransformation
        )
        pixmap.setDevicePixelRatio(dpr)

        self.label.setPixmap(pixmap)

        self._setup_button(
            self.createNewFilePushButton, icons.document_plus, "New File"
        )
        self._setup_button(
            self.openRecentFilePushButton,
            icons.document_clock,
            "Open Most Recent File",
            height=52,
        )
        self._setup_button(self.openFilePushButton, icons.open_file, "Open File")
        self._setup_button(
            self.openDemoFilePushButton, icons.document_smiley, "Open Demo or Template"
        )
        self._setup_button(
            self.openQuickStartGuidePushButton,
            icons.book_question,
            "Open Documentation on GitHub",
            height=52,
        )
        self._setup_button(self.quitPushButton, icons.quit_, "Quit")

        self.createNewFilePushButton.clicked.connect(self.signal_new_file)
        self.openFilePushButton.clicked.connect(self.signal_open_file)
        self.openRecentFilePushButton.clicked.connect(self.signal_open_recent_file)
        self.openDemoFilePushButton.clicked.connect(self._show_menu)
        self.openQuickStartGuidePushButton.clicked.connect(self.signal_open_docs)
        self.quitPushButton.clicked.connect(self.signal_quit)

        self.menu_demo_template = None

    def closeEvent(self, a0: QCloseEvent) -> None:  # noqa: ARG002
        self.signal_close.emit()  # needed to re-enable MainView

    def set_open_recent_file_button(
        self, *, enabled: bool, file_path: Path | None
    ) -> None:
        self.openRecentFilePushButton.setEnabled(enabled)
        self.openRecentFilePushButton.setToolTip(str(file_path))

        label = self.openRecentFilePushButton.layout().itemAt(0).widget()
        if not isinstance(label, QLabel):
            raise TypeError("Unexpected widget in openRecentFilePushButton layout")
        if file_path is not None:
            label.setText(f"Open Most Recent File\n({_shorten_path_string(file_path)})")
        else:
            label.setText("Open Most Recent File")

    @staticmethod
    def _setup_button(
        button: QPushButton, icon: QIcon, text: str, height: int = 34
    ) -> None:
        button.setIcon(icon)
        button.setText("")
        button.setStyleSheet("text-align:left; padding-left:6px")
        button.setLayout(QGridLayout())
        button.setMinimumHeight(height)

        label = QLabel(text=text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        button.layout().addWidget(label)

    def _show_menu(self) -> None:
        if self.menu_demo_template is not None:
            return
        self.menu_demo_template = QMenu(self.openDemoFilePushButton)
        action_demo_basic = QAction("Basic Demo", self)
        action_demo_mortgage = QAction("Mortgage Demo", self)
        action_template_category_en = QAction("Category Template (EN)", self)
        action_template_category_cz = QAction("Category Template (CZ)", self)

        action_demo_basic.triggered.connect(self.signal_open_demo_basic.emit)
        action_demo_mortgage.triggered.connect(self.signal_open_demo_mortgage.emit)
        action_template_category_en.triggered.connect(
            self.signal_open_template_category_en.emit
        )
        action_template_category_cz.triggered.connect(
            self.signal_open_template_category_cz.emit
        )

        self.menu_demo_template.addAction(action_demo_basic)
        self.menu_demo_template.addAction(action_demo_mortgage)
        self.menu_demo_template.addSeparator()
        self.menu_demo_template.addAction(action_template_category_en)
        self.menu_demo_template.addAction(action_template_category_cz)

        self.menu_demo_template.exec(
            self.openDemoFilePushButton.mapToGlobal(
                self.openDemoFilePushButton.rect().bottomLeft()
            )
        )
        self.menu_demo_template = None


def _shorten_path_string(path: Path) -> str:
    """Returns shortened path string limited to 30(+3) characters."""
    str_ = str(path)
    if len(str_) <= PATH_STRING_MAX_LENGTH:
        return str_

    segments = Path(path).parts
    n_segments = len(segments)
    for i in range(1, n_segments):
        path = Path(*segments[i:n_segments])
        str_ = str(path)
        if len(str_) <= PATH_STRING_MAX_LENGTH:
            return f"...{os.sep}{str_}"
    return "mouseover to show full path"
