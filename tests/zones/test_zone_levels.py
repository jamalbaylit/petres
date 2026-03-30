from __future__ import annotations

import pytest

from petres.models import Zone


def test_zone_divide_rejects_levels_not_starting_at_zero(horizon_plane_top, horizon_plane_base):
    zone = Zone("Z", top=horizon_plane_top, base=horizon_plane_base)
    with pytest.raises(ValueError, match=r"levels\[0\]"):
        zone.divide(levels=[0.1, 0.5, 1.0])


def test_zone_divide_rejects_levels_not_ending_at_one(horizon_plane_top, horizon_plane_base):
    zone = Zone("Z", top=horizon_plane_top, base=horizon_plane_base)
    with pytest.raises(ValueError, match=r"levels\[-1\]"):
        zone.divide(levels=[0.0, 0.5, 0.9])


def test_zone_divide_rejects_non_positive_fractions(horizon_plane_top, horizon_plane_base):
    zone = Zone("Z", top=horizon_plane_top, base=horizon_plane_base)
    with pytest.raises(ValueError, match="fractions"):
        zone.divide(fractions=[0.5, 0.0, 0.5])
