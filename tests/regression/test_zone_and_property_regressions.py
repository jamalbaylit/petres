from __future__ import annotations

import pytest


def test_zone_normalize_name_rejects_unsupported_type(simple_cornerpoint_grid):
    with pytest.raises(TypeError, match="must be str"):
        simple_cornerpoint_grid._normalize_zone_name(123)


def test_property_getitem_raises_clear_error(simple_cornerpoint_grid):
    with pytest.raises(KeyError, match="does not exist"):
        _ = simple_cornerpoint_grid.properties["missing"]
