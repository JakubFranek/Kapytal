import logging

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QApplication
from src.models.model_objects.attributes import AttributeType
from src.models.record_keeper import RecordKeeper
from src.models.utilities.calculation import calculate_tag_stats
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.tag_table_model import TagTableModel
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
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
        self._view.signal_search_text_changed.connect(self._filter)

        self._view.finalize_setup()
        self._view.signal_selection_changed.connect(self._selection_changed)
        self._selection_changed()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper

    def reset_model(self) -> None:
        self._model.pre_reset_model()
        self.update_model_data()
        self._model.post_reset_model()

    def update_model_data(self) -> None:
        relevant_transactions = (
            self._record_keeper.cash_transactions
            + self._record_keeper.refund_transactions
        )
        self._model.tag_stats = calculate_tag_stats(
            relevant_transactions,
            self._record_keeper.base_currency,
            self._record_keeper.tags,
        ).values()

    def show_form(self) -> None:
        self._busy_dialog = create_simple_busy_indicator(
            self._view, "Calculating Tag stats, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()
        try:
            self.reset_model()
        except:  # noqa: TRY302
            raise
        finally:
            self._busy_dialog.close()
        self._view.show_form()

    def run_tag_dialog(self, *, edit: bool) -> None:
        self._dialog = TagDialog(self._view, edit=edit)
        if edit:
            tags = self._model.get_selected_items()
            if len(tags) == 0:
                raise ValueError("Cannot edit an unselected item.")
            if len(tags) > 1:
                raise ValueError("Cannot edit more than one item.")
            tag = tags[0]
            self._dialog.signal_ok.connect(self.rename_tag)
            self._dialog.name = tag.name
        else:
            self._dialog.signal_ok.connect(self.add_tag)
        logging.debug(f"Running TagDialog ({edit=})")
        self._dialog.exec()

    def add_tag(self) -> None:
        name = self._dialog.name

        logging.info(f"Adding Tag: {name=}")
        try:
            self._record_keeper.add_tag(name)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._model.pre_add()
        self.update_model_data()
        self._model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def rename_tag(self) -> None:
        tags = self._model.get_selected_items()
        if len(tags) == 0:
            raise ValueError("Cannot edit an unselected item.")
        if len(tags) > 1:
            raise ValueError("Cannot edit more than one item.")
        tag = tags[0]
        current_name = tag.name
        new_name = self._dialog.name

        logging.info(f"Renaming Tag name={current_name}: new name='{new_name}'")
        try:
            self._record_keeper.edit_attribute(
                current_name, new_name, AttributeType.TAG
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self.update_model_data()
        self._dialog.close()
        self.event_data_changed()

    def remove_tag(self) -> None:
        tags = self._model.get_selected_items()
        if len(tags) == 0:
            raise ValueError("Cannot remove an unselected item.")

        tag_names = ["'" + tag.name + "'" for tag in tags]
        logging.info(f"Removing Tags: {', '.join(tag_names)}")
        any_deleted = False
        for tag in tags:
            try:
                self._record_keeper.remove_tag(tag.name)
                self._model.pre_remove_item(tag)
                self.update_model_data()
                self._model.post_remove_item()
                any_deleted = True
            except Exception as exception:  # noqa: BLE001
                handle_exception(exception)
            finally:
                if any_deleted:
                    self.event_data_changed()

    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        self._proxy_model.setFilterWildcard(pattern)

    def _selection_changed(self) -> None:
        tags = self._model.get_selected_items()
        is_tag_selected = len(tags) > 0
        is_one_tag_selected = len(tags) == 1
        self._view.enable_actions(
            is_tag_selected=is_tag_selected, is_one_tag_selected=is_one_tag_selected
        )
