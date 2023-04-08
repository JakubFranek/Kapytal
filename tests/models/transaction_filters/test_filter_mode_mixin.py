from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from src.models.transaction_filters.filter_mode_mixin import FilterMode, FilterModeMixin
from tests.models.test_assets.composites import everything_except


class ConcreteFilter(FilterModeMixin):
    def __init__(self, mode: FilterMode) -> None:
        super().__init__(mode=mode)


@given(mode=st.sampled_from(FilterMode))
def test_creation(mode: FilterMode) -> None:
    filter_ = ConcreteFilter(mode)
    assert filter_.mode == mode


@given(mode=everything_except(FilterMode))
def test_invalid_type(mode: Any) -> None:
    with pytest.raises(TypeError, match="Parameter 'mode' must be a FilterMode."):
        ConcreteFilter(mode)
