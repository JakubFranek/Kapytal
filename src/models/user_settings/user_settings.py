import json
import logging

import src.utilities.constants as constants
from src.models.user_settings.user_settings_class import UserSettings

settings: UserSettings = UserSettings()  # this is where the settings are

_json_encoder: type[json.JSONEncoder] = None
_json_decoder: type[json.JSONDecoder] = None


def set_json_encoder(encoder: type[json.JSONEncoder]) -> None:
    global _json_encoder

    if not isinstance(encoder, type(json.JSONEncoder)):
        raise TypeError("Parameter 'encoder' must be a type of JSONEncoder.")

    _json_encoder = encoder


def set_json_decoder(decoder: type[json.JSONDecoder]) -> None:
    global _json_decoder

    if not isinstance(decoder, type(json.JSONEncoder)):
        raise TypeError("Parameter 'decoder' must be a type of JSONDecoder.")

    _json_decoder = decoder


def load() -> None:
    global settings

    with open(constants.settings_path, mode="r", encoding="UTF-8") as file:
        logging.debug(f"Loading UserSettings: {constants.settings_path}")
        settings = json.load(file, cls=_json_decoder)
        logging.info(f"UserSettings loaded: {constants.settings_path}")


def save() -> None:
    with open(constants.settings_path, mode="w", encoding="UTF-8") as file:
        logging.debug(f"Saving UserSettings: {constants.settings_path}")
        json.dump(settings, file, cls=_json_encoder)
        logging.info(f"UserSettings saved: {constants.settings_path}")
