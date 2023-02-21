import json
import logging
from pathlib import Path

from src.models.user_settings.user_settings_class import UserSettings

settings: UserSettings = UserSettings()
_settings_path: Path = None
_json_encoder: type[json.JSONEncoder] = None
_json_decoder: type[json.JSONDecoder] = None


def set_path(path: Path) -> None:
    global _settings_path

    if not isinstance(path, Path):
        raise TypeError("Parameter 'path' must be a Path.")

    _settings_path = path


def set_json_encoder(encoder: type[json.JSONEncoder]) -> None:
    global _json_encoder
    _json_encoder = encoder


def set_json_decoder(decoder: type[json.JSONDecoder]) -> None:
    global _json_decoder
    _json_decoder = decoder


def load() -> None:
    global settings

    with open(_settings_path, mode="r", encoding="UTF-8") as file:
        logging.debug(f"Loading _Settings: '{_settings_path}'")
        settings = json.load(file, cls=_json_decoder)
        logging.info(f"_Settings loaded: '{_settings_path}'")


def save() -> None:
    with open(_settings_path, mode="w", encoding="UTF-8") as file:
        logging.debug(f"Saving _Settings: '{_settings_path}'")
        json.dump(settings, file, cls=_json_decoder)
        logging.info(f"_Settings saved: '{_settings_path}'")
