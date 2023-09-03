import unicodedata
from collections.abc import Collection

from PyQt6.QtCore import QStringListModel
from PyQt6.QtWidgets import QCompleter, QWidget


class SmartCompleter(QCompleter):
    def __init__(self, strings: Collection[str], parent: QWidget | None = None) -> None:
        super().__init__(strings, parent)
        self._strings: tuple[str] = tuple(
            sorted(strings, key=lambda s: unicodedata.normalize("NFD", s).lower())
        )
        self._matches_cache: dict[str, tuple[str]] = {}
        self._model = QStringListModel(strings)
        self.setModel(self._model)

    def popup_from_text(self, text: str) -> None:
        """Custom method (not a QCompleter override) for creating popup from text."""

        lowered_text = text.lower()

        if lowered_text in self._matches_cache:
            matches = self._matches_cache[lowered_text]
        else:
            _strings = self._matches_cache.get(lowered_text[:-1], self._strings)
            matches: list[str] = []
            _not_start_with: list[str] = []
            for string in _strings:
                lowered_string = string.lower()
                if lowered_string.startswith(lowered_text):
                    matches.append(string)
                elif lowered_text in lowered_string:
                    _not_start_with.append(string)
            matches.extend(_not_start_with)
            self._matches_cache[lowered_text] = tuple(matches)

        self._model.setStringList(matches)

        if len(matches) == 1 and matches[0] == text:
            return  # no popup needed when text is exact

        self.complete()
