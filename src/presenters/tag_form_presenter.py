import logging

from PyQt6.QtCore import QSortFilterProxyModel, Qt

from src.models.model_objects.attributes import AttributeType
from src.models.record_keeper import RecordKeeper
from src.models.utilities.calculation import AttributeStats, get_attribute_stats
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.presenters.view_models.tag_table_model import TagTableModel
from src.views.dialogs.tag_dialog import TagDialog
from src.views.forms.tag_form import TagForm


class TagFormPresenter:
    event_data_changed = Event()

    def __init__(self, view: TagForm, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        self._proxy_model = QSortFilterProxyModel(self._view.tableView)
        self._model = TagTableModel(self._view.tableView, [], self._proxy_model)
        self.update_model_data()
        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._view.tableView.setModel(self._proxy_model)

        self._view.signal_add_tag.connect(lambda: self.run_tag_dialog(edit=False))
        self._view.signal_remove_tag.connect(self.remove_tag)
        self._view.signal_rename_tag.connect(lambda: self.run_tag_dialog(edit=True))
        self._view.signal_select_tag.connect(self.select_tag)
        self._view.signal_search_text_changed.connect(self._filter)

        self._view.finalize_setup()
        self._view.signal_selection_changed.connect(self._selection_changed)
        self._selection_changed()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._model.pre_reset_model()
        self._record_keeper = record_keeper
        self.update_model_data()
        self._model.post_reset_model()

    def update_model_data(self) -> None:
        tag_stats: list[AttributeStats] = []
        for tag in self._record_keeper.tags:
            tag_stats.append(
                get_attribute_stats(
                    tag,
                    self._record_keeper.transactions,
                    self._record_keeper.base_currency,
                )
            )
        self._model.tag_stats = tag_stats

    def show_form(self) -> None:
        self.update_model_data()
        self._view.selectButton.setVisible(False)
        self._view.show_form()

    def run_tag_dialog(self, edit: bool) -> None:
        self._dialog = TagDialog(self._view, edit)
        if edit:
            item = self._model.get_selected_item()
            if item is None:
                raise ValueError("Cannot edit an unselected item.")
            self._dialog.signal_OK.connect(self.rename_tag)
            self._dialog.name = item.name
        else:
            self._dialog.signal_OK.connect(self.add_tag)
        logging.debug(f"Running TagDialog ({edit=})")
        self._dialog.exec()

    def add_tag(self) -> None:
        name = self._dialog.name

        logging.info("Adding Tag")
        try:
            self._record_keeper.add_tag(name)
        except Exception:
            handle_exception()
            return

        self._model.pre_add()
        self.update_model_data()
        self._model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def rename_tag(self) -> None:
        tag = self._model.get_selected_item()
        if tag is None:
            raise ValueError("Cannot edit an unselected item.")
        current_name = tag.name
        new_name = self._dialog.name

        logging.info("Renaming Tag")
        try:
            self._record_keeper.edit_attribute(
                current_name, new_name, AttributeType.TAG
            )
        except Exception:
            handle_exception()
            return

        self.update_model_data()
        self._dialog.close()
        self.event_data_changed()

    def remove_tag(self) -> None:
        tag = self._model.get_selected_item()
        if tag is None:
            return

        logging.info(f"Removing {tag}")
        try:
            self._record_keeper.remove_tag(tag.name)
        except Exception:
            handle_exception()
            return

        self._model.pre_remove_item(tag)
        self.update_model_data()
        self._model.post_remove_item()
        self.event_data_changed()

    def select_tag(self) -> None:
        pass

    def _filter(self) -> None:
        pattern = self._view.search_bar_text
        logging.debug(f"Filtering Tags: {pattern=}")
        self._proxy_model.setFilterWildcard(pattern)

    def _selection_changed(self) -> None:
        item = self._model.get_selected_item()
        is_tag_selected = item is not None
        self._view.set_buttons(is_tag_selected)
