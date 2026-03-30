from __future__ import annotations

import numpy as np
import pytest

from petres.errors import UnsupportedGridAttributeError


def test_apply_rejects_callable_returning_wrong_shape(simple_cornerpoint_grid):
    poro = simple_cornerpoint_grid.properties.create("poro")

    with pytest.raises(ValueError, match="must return either a scalar"):
        poro.apply(lambda z: np.column_stack([z, z]), source="z")


def test_apply_rejects_unsupported_source_name(simple_cornerpoint_grid):
    poro = simple_cornerpoint_grid.properties.create("poro")

    with pytest.raises(UnsupportedGridAttributeError):
        poro.apply(lambda x: x, source="bad_source")


def test_fill_uniform_respects_bounds(simple_cornerpoint_grid):
    ntg = simple_cornerpoint_grid.properties.create("ntg")
    ntg.fill_uniform(0.1, 0.3, seed=123)

    assert np.nanmin(ntg.values) >= 0.1
    assert np.nanmax(ntg.values) <= 0.3
