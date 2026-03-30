from __future__ import annotations

import numpy as np
import pytest

from petres.models import BoundaryPolygon, VerticalWell


def test_boundary_polygon_contains_returns_expected_mask():
    boundary = BoundaryPolygon.from_bbox(0.0, 0.0, 10.0, 10.0)
    pts = np.array([[5.0, 5.0], [11.0, 1.0]])

    mask = boundary.contains(pts)

    assert mask.dtype == np.bool_
    assert mask.tolist() == [True, False]


def test_vertical_well_top_lifecycle():
    well = VerticalWell(name="W1", x=1.0, y=2.0)
    well.add_top("TopA", 1000.0)

    assert well.get_top("TopA") == pytest.approx(1000.0)

    well.remove_top("TopA")
    with pytest.raises(KeyError, match="not found"):
        well.get_top("TopA")


def test_vertical_well_sample_mode_conflict_raises():
    well = VerticalWell(name="W1", x=1.0, y=2.0)
    well.add_sample("poro", value=0.2)

    with pytest.raises(ValueError, match="existing samples"):
        well.add_sample("poro", value=0.25, depth=1050.0)
