from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QGridLayout, QLabel, QPushButton, QWidget
from src.utilities import constants
from src.views import colors, icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_welcome_dialog import Ui_WelcomeDialog


class WelcomeDialog(CustomDialog, Ui_WelcomeDialog):
    signal_new_file = pyqtSignal()
    signal_open_recent_file = pyqtSignal()
    signal_open_file = pyqtSignal()
    signal_open_demo_file = pyqtSignal()
    signal_open_guide = pyqtSignal()
    signal_quit = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)

        if colors.color_scheme == Qt.ColorScheme.Dark:
            self.pixmap = QPixmap(
                str(constants.app_root_path / "resources/images/welcome_dark_mode.png")
            )
        else:
            self.pixmap = QPixmap(
                str(constants.app_root_path / "resources/images/welcome_light_mode.png")
            )
        self.label.setPixmap(self.pixmap)

        self._setup_button(
            self.createNewFilePushButton, icons.document_plus, "Create New File"
        )
        self._setup_button(
            self.openRecentFilePushButton, icons.document_clock, "Open Most Recent File"
        )
        self._setup_button(
            self.openFilePushButton, icons.open_file, "Open File from Browser"
        )
        self._setup_button(
            self.openDemoFilePushButton, icons.document_smiley, "Open Demo File"
        )
        self._setup_button(
            self.openQuickStartGuidePushButton,
            icons.book_question,
            "Open Quick Start Guide",
        )
        self._setup_button(self.quitPushButton, icons.quit_, "Quit")

        self.createNewFilePushButton.clicked.connect(self.signal_new_file)
        self.openFilePushButton.clicked.connect(self.signal_open_file)
        self.openRecentFilePushButton.clicked.connect(self.signal_open_recent_file)
        self.openDemoFilePushButton.clicked.connect(self.signal_open_demo_file)
        self.openQuickStartGuidePushButton.clicked.connect(self.signal_open_guide)
        self.quitPushButton.clicked.connect(self.signal_quit)

        self.openQuickStartGuidePushButton.setEnabled(False)

    def set_open_recent_file_button(self, *, enabled: bool) -> None:
        self.openRecentFilePushButton.setEnabled(enabled)

    @staticmethod
    def _setup_button(button: QPushButton, icon: QIcon, text: str) -> None:
        button.setIcon(icon)
        button.setText("")
        button.setStyleSheet("text-align:left; padding-left:6px")
        button.setLayout(QGridLayout())
        button.setMinimumHeight(34)

        label = QLabel(text=text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        button.layout().addWidget(label)
