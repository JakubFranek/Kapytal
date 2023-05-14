from typing import Any

import pytest
from hypothesis import given
from src.models.mixins.name_mixin import NameMixin
from tests.models.test_assets.composites import everything_except


@given(allow_slash=everything_except(bool))
def test_allow_slash_invalid_type(allow_slash: Any) -> None:
    with pytest.raises(TypeError, match="Parameter 'allow_slash' must be a boolean."):
        NameMixin(name="test", allow_slash=allow_slash)
