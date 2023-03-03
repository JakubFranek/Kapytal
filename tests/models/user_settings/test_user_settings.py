import json
import shutil
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given

from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
from tests.models.test_assets.composites import everything_except


def test_user_settings_import() -> None:
    import src.models.user_settings.user_settings as user_settings
    import src.models.user_settings.user_settings_class as user_settings_class

    assert isinstance(user_settings.settings, user_settings_class.UserSettings)
    assert user_settings._json_decoder is None
    assert user_settings._json_encoder is None


def test_user_settings_set_json_encoder() -> None:
    import src.models.user_settings.user_settings as user_settings

    user_settings.set_json_encoder(CustomJSONEncoder)

    assert user_settings._json_encoder == CustomJSONEncoder


@given(encoder=everything_except(type(json.JSONEncoder)))
def test_user_settings_set_json_encoder_invalid_type(encoder: Any) -> None:
    import src.models.user_settings.user_settings as user_settings

    with pytest.raises(TypeError, match="JSONEncoder"):
        user_settings.set_json_encoder(encoder)


def test_user_settings_set_json_decoder() -> None:
    import src.models.user_settings.user_settings as user_settings

    user_settings.set_json_decoder(CustomJSONDecoder)

    assert user_settings._json_decoder == CustomJSONDecoder


@given(decoder=everything_except(type(json.JSONDecoder)))
def test_user_settings_set_json_decoder_invalid_type(decoder: Any) -> None:
    import src.models.user_settings.user_settings as user_settings

    with pytest.raises(TypeError, match="JSONDecoder"):
        user_settings.set_json_decoder(decoder)


def test_user_settings_set_path_save_load() -> None:
    import src.models.user_settings.user_settings as user_settings
    import src.utilities.constants as constants

    this_dir = Path(__file__).resolve().parent
    test_dir = this_dir / "Test Directory"
    test_dir.mkdir(exist_ok=True)
    settings_path = test_dir / "user_settings.json"
    constants.settings_path = settings_path

    user_settings.set_json_encoder(CustomJSONEncoder)
    user_settings.set_json_decoder(CustomJSONDecoder)
    user_settings.save()
    user_settings.load()

    assert settings_path.exists()

    shutil.rmtree(test_dir)
