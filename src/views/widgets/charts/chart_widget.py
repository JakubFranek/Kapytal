from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from src.views import icons
from src.views.widgets.charts.canvas import Canvas


class ChartWidget(QWidget):
    def __init__(self, parent: QWidget | None, *, polar: bool = False) -> None:
        super().__init__(parent)

        self.horizontal_layout = QHBoxLayout()

        self.chart = Canvas(polar=polar)
        self.chart_toolbar = NavigationToolbar2QT(self.chart, None)
        self.vertical_layout = QVBoxLayout(self)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.chart)

        self._initialize_toolbar_buttons()
        self._initialize_toolbar_actions()

    def _initialize_toolbar_buttons(self) -> None:
        self.homeToolButton = QToolButton(self)
        self.backToolButton = QToolButton(self)
        self.forwardToolButton = QToolButton(self)
        self.panToolButton = QToolButton(self)
        self.zoomToolButton = QToolButton(self)
        self.subplotsToolButton = QToolButton(self)
        self.customizeToolButton = QToolButton(self)
        self.saveToolButton = QToolButton(self)

        self.horizontal_spacer = QSpacerItem(
            0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontal_layout.addWidget(self.homeToolButton)
        self.horizontal_layout.addWidget(self.backToolButton)
        self.horizontal_layout.addWidget(self.forwardToolButton)
        self.horizontal_layout.addWidget(self.panToolButton)
        self.horizontal_layout.addWidget(self.zoomToolButton)
        self.horizontal_layout.addWidget(self.subplotsToolButton)
        self.horizontal_layout.addWidget(self.customizeToolButton)
        self.horizontal_layout.addWidget(self.saveToolButton)
        self.horizontal_layout.addItem(self.horizontal_spacer)

        self.layout().setContentsMargins(0, 0, 0, 0)

    def _initialize_toolbar_actions(self) -> None:
        self.actionHome = QAction(icons.home, "Reset Chart", self)
        self.actionBack = QAction(icons.arrow_left, "Back", self)
        self.actionForward = QAction(icons.arrow_right, "Forward", self)
        self.actionPan = QAction(icons.arrow_move, "Pan", self)
        self.actionZoom = QAction(icons.magnifier, "Zoom", self)
        self.actionSubplots = QAction(icons.slider, "Subplots", self)
        self.actionCustomize = QAction(icons.settings, "Customize", self)
        self.actionSave = QAction(icons.disk, "Save", self)
        self.actionHome.triggered.connect(self.chart_toolbar.home)
        self.actionBack.triggered.connect(self.chart_toolbar.back)
        self.actionForward.triggered.connect(self.chart_toolbar.forward)
        self.actionPan.triggered.connect(self._pan_triggered)
        self.actionZoom.triggered.connect(self._zoom_triggered)
        self.actionSubplots.triggered.connect(self.chart_toolbar.configure_subplots)
        self.actionCustomize.triggered.connect(self.chart_toolbar.edit_parameters)
        self.actionSave.triggered.connect(self.chart_toolbar.save_figure)
        self.actionPan.setCheckable(True)
        self.actionZoom.setCheckable(True)
        self.homeToolButton.setDefaultAction(self.actionHome)
        self.backToolButton.setDefaultAction(self.actionBack)
        self.forwardToolButton.setDefaultAction(self.actionForward)
        self.panToolButton.setDefaultAction(self.actionPan)
        self.zoomToolButton.setDefaultAction(self.actionZoom)
        self.subplotsToolButton.setDefaultAction(self.actionSubplots)
        self.customizeToolButton.setDefaultAction(self.actionCustomize)
        self.saveToolButton.setDefaultAction(self.actionSave)

    def _pan_triggered(self) -> None:
        if self.actionZoom.isChecked():
            self.actionZoom.setChecked(False)
        self.chart_toolbar.pan()

    def _zoom_triggered(self) -> None:
        if self.actionPan.isChecked():
            self.actionPan.setChecked(False)
        self.chart_toolbar.zoom()
