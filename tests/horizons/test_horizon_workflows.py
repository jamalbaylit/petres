from __future__ import annotations

import numpy as np
import pytest

from petres.interpolators import IDWInterpolator
from petres.models import Horizon, VerticalWell


def test_horizon_store_picks_false_releases_pick_arrays():
    xy = np.array([[0.0, 0.0], [100.0, 0.0], [0.0, 100.0]])
    z = np.array([1000.0, 1010.0, 1020.0])

    h = Horizon(name="Top", xy=xy, depth=z, interpolator=IDWInterpolator(), store_picks=False)

    assert h.xy.shape == (0, 2)
    assert h.depth.shape == (0,)


def test_horizon_intersect_matches_sample_value(horizon_plane_top):
    w = VerticalWell(name="P1", x=20.0, y=30.0)

    from_intersect = horizon_plane_top.intersect(w)
    from_sample = float(horizon_plane_top.sample(np.array([[20.0, 30.0]]))[0])

    assert from_intersect == pytest.approx(from_sample)


def test_horizon_sample_rejects_wrong_query_shape(horizon_plane_top):
    with pytest.raises(ValueError, match="sample expects xy shape"):
        horizon_plane_top.sample(np.array([10.0, 20.0]))
