import sys

from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget
from src.utilities import constants
from src.views import colors
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_about_dialog import Ui_AboutDialog


class AboutDialog(CustomDialog, Ui_AboutDialog):
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

        window = parent.windowHandle()
        dpr = window.devicePixelRatio()
        pixmap = self.pixmap.scaledToWidth(
            int(512 * dpr), Qt.TransformationMode.SmoothTransformation
        )
        pixmap.setDevicePixelRatio(dpr)

        self.imageLabel.setPixmap(pixmap)

        text = (
            "<html>"
            "Source code and documentation available on "
            "<a href=https://github.com/JakubFranek/Kapytal>"
            "Kapytal GitHub repository</a><br/>"
            "Published under <a href=https://www.gnu.org/licenses/gpl-3.0.html>"
            "GNU General Public Licence v3.0</a><br/>"
            "<br/>"
            "<b>Version info</b><br/>"
            f"- Kapytal {constants.VERSION}<br/>"
            f"- Python {sys.version}<br/>"
            f"- Qt {QT_VERSION_STR}<br/>"
            f"- PyQt {PYQT_VERSION_STR}<br/>"
            "<br/>"
            "<b>Icons info</b><br/>"
            "<a href=https://p.yusukekamiyamane.com>Fugue Icons set</a> by "
            "Yusuke Kamiyamane. Upscaled to 32 px by "
            "<a href=https://github.com/chrisjbillington/fugue-2x-icons>Chris Billington"
            "</a>.<br/>"
            "Custom icons located in <tt>Kapytal/resources/icons/icons-custom</tt> "
            "are modifications <br/>"
            "of existing Fugue Icons, or custom icons created by me.<br/><br/>"
            "<em>Dedicated to my wife Soňa</em>"
            "</html>"
        )
        self.aboutLabel.setText(text)

        self.buttonBox.rejected.connect(self.close)
