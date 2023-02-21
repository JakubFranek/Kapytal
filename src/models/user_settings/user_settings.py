import json
import logging
from pathlib import Path

from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
from src.models.user_settings.user_settings_class import UserSettings

settings: UserSettings = UserSettings()
_settings_path: Path = None


def set_path(path: Path) -> None:
    global _settings_path

    if not isinstance(path, Path):
        raise TypeError("Parameter 'path' must be a Path.")

    _settings_path = path


def load() -> None:
    """Requires settings path (defined via set_settings_path function)"""

    global settings

    with open(_settings_path, mode="r", encoding="UTF-8") as file:
        logging.debug(f"Loading _Settings: '{_settings_path}'")
        settings = json.load(file, cls=CustomJSONDecoder)
        logging.info(f"_Settings loaded: '{_settings_path}'")


def save() -> None:
    """Requires settings path (defined via set_settings_path function)"""

    with open(_settings_path, mode="w", encoding="UTF-8") as file:
        logging.debug(f"Saving _Settings: '{_settings_path}'")
        json.dump(settings, file, cls=CustomJSONEncoder)
        logging.info(f"_Settings saved: '{_settings_path}'")
