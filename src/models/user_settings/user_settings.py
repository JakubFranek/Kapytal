import json
import logging

from src.models.user_settings.user_settings_class import UserSettings
from src.utilities import constants

settings: UserSettings = UserSettings()  # this is where the settings are

_json_encoder: type[json.JSONEncoder] | None = None
_json_decoder: type[json.JSONDecoder] | None = None


def set_json_encoder(encoder: type[json.JSONEncoder]) -> None:
    global _json_encoder  # noqa: PLW0603

    if not isinstance(encoder, type(json.JSONEncoder)):
        raise TypeError("Parameter 'encoder' must be a type of JSONEncoder.")

    _json_encoder = encoder


def set_json_decoder(decoder: type[json.JSONDecoder]) -> None:
    global _json_decoder  # noqa: PLW0603

    if not isinstance(decoder, type(json.JSONEncoder)):
        raise TypeError("Parameter 'decoder' must be a type of JSONDecoder.")

    _json_decoder = decoder


def load() -> None:
    global settings  # noqa: PLW0603

    with constants.settings_path.open(encoding="UTF-8") as file:
        logging.debug(f"Loading UserSettings: {constants.settings_path}")
        settings = json.load(file, cls=_json_decoder)
        logging.info(f"UserSettings loaded: {constants.settings_path}")


def save() -> None:
    with constants.settings_path.open(mode="w", encoding="UTF-8") as file:
        logging.debug(f"Saving UserSettings: {constants.settings_path}")
        json.dump(settings, file, cls=_json_encoder)
        logging.info(f"UserSettings saved: {constants.settings_path}")
