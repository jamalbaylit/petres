from __future__ import annotations

import numpy as np
import pytest

from petres.models import Zone


def test_zone_thickness_matches_base_minus_top(horizon_plane_top, horizon_plane_base):
    zone = Zone("Reservoir", top=horizon_plane_top, base=horizon_plane_base)
    pts = np.array([[0.0, 0.0], [100.0, 100.0], [50.0, 50.0]])

    th = zone.thickness(pts)

    np.testing.assert_allclose(th, 30.0, atol=1e-6)


def test_divide_with_nk_generates_uniform_levels(horizon_plane_top, horizon_plane_base):
    zone = Zone("Z", top=horizon_plane_top, base=horizon_plane_base).divide(nk=4)

    assert zone.n_layers == 4
    np.testing.assert_allclose(zone.levels, (0.0, 0.25, 0.5, 0.75, 1.0))


def test_divide_with_fractions_normalizes_levels(horizon_plane_top, horizon_plane_base):
    zone = Zone("Z", top=horizon_plane_top, base=horizon_plane_base).divide(fractions=[1, 1, 2])

    np.testing.assert_allclose(zone.levels, (0.0, 0.25, 0.5, 1.0))


def test_divide_with_levels_keeps_strict_monotonicity(horizon_plane_top, horizon_plane_base):
    zone = Zone("Z", top=horizon_plane_top, base=horizon_plane_base).divide(levels=[0.0, 0.2, 1.0])
    assert zone.n_layers == 2


def test_divide_rejects_multiple_methods(horizon_plane_top, horizon_plane_base):
    zone = Zone("Z", top=horizon_plane_top, base=horizon_plane_base)
    with pytest.raises(ValueError, match="provide only one"):
        zone.divide(nk=2, levels=[0.0, 1.0])


def test_divide_rejects_non_increasing_levels(horizon_plane_top, horizon_plane_base):
    zone = Zone("Z", top=horizon_plane_top, base=horizon_plane_base)
    with pytest.raises(ValueError, match="strictly increasing"):
        zone.divide(levels=[0.0, 0.3, 0.3, 1.0])


def test_divide_rejects_invalid_nk(horizon_plane_top, horizon_plane_base):
    zone = Zone("Z", top=horizon_plane_top, base=horizon_plane_base)
    with pytest.raises(ValueError, match="must be >= 2"):
        zone.divide(nk=1)
