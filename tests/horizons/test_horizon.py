from __future__ import annotations

import numpy as np
import pytest

from petres.interpolators import IDWInterpolator
from petres.models import Horizon, VerticalWell


def test_horizon_sample_and_to_grid_shapes(horizon_plane_top):
    pts = np.array([[10.0, 20.0], [50.0, 50.0]])
    sampled = horizon_plane_top.sample(pts)
    surface = horizon_plane_top.to_grid(np.linspace(0.0, 100.0, 5), np.linspace(0.0, 100.0, 4))

    assert sampled.shape == (2,)
    assert surface.shape == (4, 5)


def test_horizon_rejects_invalid_xy_shape():
    with pytest.raises(ValueError, match="xy must be shape"):
        Horizon(name="H", xy=np.array([1.0, 2.0]), depth=np.array([1.0]), interpolator=IDWInterpolator())


def test_horizon_rejects_mismatched_z_size():
    xy = np.array([[0.0, 0.0], [1.0, 1.0]])
    z = np.array([1.0])
    with pytest.raises(ValueError, match="matching xy"):
        Horizon(name="H", xy=xy, depth=z, interpolator=IDWInterpolator())


def test_horizon_rejects_invalid_interpolator_type():
    xy = np.array([[0.0, 0.0], [1.0, 1.0]])
    z = np.array([1.0, 2.0])
    with pytest.raises(TypeError, match="BaseInterpolator"):
        Horizon(name="H", xy=xy, depth=z, interpolator=object())


def test_horizon_from_wells_extracts_tops():
    wells = [VerticalWell(name="W1", x=0.0, y=0.0), VerticalWell(name="W2", x=10.0, y=0.0)]
    wells[0].add_top("TopA", 1000.0)
    wells[1].add_top("TopA", 1010.0)

    h = Horizon.from_wells(name="TopA", wells=wells, interpolator=IDWInterpolator())

    assert h.xy.shape == (2, 2)
    assert h.depth.shape == (2,)


def test_horizon_from_wells_raises_when_missing_top():
    wells = [VerticalWell(name="W1", x=0.0, y=0.0), VerticalWell(name="W2", x=10.0, y=0.0)]
    wells[0].add_top("TopA", 1000.0)
    with pytest.raises(ValueError, match="does not have a top"):
        Horizon.from_wells(name="TopA", wells=wells, interpolator=IDWInterpolator())


def test_to_zone_depth_sign_controls_top_and_base(horizon_plane_top):
    deeper = horizon_plane_top.to_zone(name="Z1", depth=10.0)
    shallower = horizon_plane_top.to_zone(name="Z2", depth=-10.0)

    assert deeper.top.name == horizon_plane_top.name
    assert shallower.base.name == horizon_plane_top.name


def test_to_zone_rejects_zero_depth(horizon_plane_top):
    with pytest.raises(ValueError, match="cannot be zero"):
        horizon_plane_top.to_zone(name="Z", depth=0.0)
