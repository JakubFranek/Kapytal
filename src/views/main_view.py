from PyQt6.QtWidgets import QMainWindow

from src.views.ui_files.Ui_mainwindow import Ui_MainWindow


class MainView(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        # TODO: this will be moved to MainPresenter or something
        self.show()
