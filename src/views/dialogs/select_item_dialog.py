from collections.abc import Collection

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QAbstractButton,
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QWidget,
)
from src.view_models.simple_list_model import SimpleListModel
from src.views.ui_files.dialogs.Ui_select_item_dialog import Ui_SelectItemDialog


class SelectItemDialog(QDialog, Ui_SelectItemDialog):
    def __init__(
        self, parent: QWidget, items: Collection[str], title: str, icon: QIcon
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowTitle(title)
        self.setWindowIcon(icon)

        self._proxy = QSortFilterProxyModel(self)
        self._model = SimpleListModel(self.listView, items, self._proxy)
        self._proxy.setSourceModel(self._model)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.listView.setModel(self._proxy)

        self.buttonBox.clicked.connect(self._handle_button_box_click)

        self.searchLineEdit.textChanged.connect(self._filter)
        self.searchLineEdit.addAction(
            QIcon("icons_16:magnifier.png"), QLineEdit.ActionPosition.LeadingPosition
        )

        self.listView.selectionModel().selectionChanged.connect(self._selection_changed)
        self.listView.doubleClicked.connect(self._accept)
        self._selection_changed()

        self.selection = ""

    def _filter(self) -> None:
        pattern = self.searchLineEdit.text()
        self._proxy.setFilterWildcard(pattern)

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self._accept()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.reject()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")

    def _accept(self) -> None:
        self.selection = self._model.get_selected_item()
        if self.selection is None:
            raise ValueError("Cannot accept a SelectItemDialog with no selection.")
        self.accept()

    def _selection_changed(self) -> None:
        selection = self._model.get_selected_item()
        ok_button = self.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(selection is not None)


def ask_user_for_selection(
    parent: QWidget, item_names: Collection[str], title: str, icon: QIcon
) -> str:
    dialog = SelectItemDialog(parent, item_names, title, icon)
    dialog.exec()
    selection = dialog.selection
    dialog.deleteLater()
    return selection
