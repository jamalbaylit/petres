from __future__ import annotations

import numpy as np
import pytest

from petres.grids import CornerPointGrid
from petres.interpolators import IDWInterpolator


def test_apply_boundary_handles_broadcast_active_without_write_error(rectilinear_vertices):
    x, y, z = rectilinear_vertices
    grid = CornerPointGrid.from_rectilinear(x=x, y=y, z=z)

    from petres.models import BoundaryPolygon

    boundary = BoundaryPolygon.from_bbox(0.0, 0.0, 50.0, 50.0)
    grid.apply_boundary(boundary)

    assert grid.active.flags.writeable
    assert grid.n_active < grid.n_cells


def test_idw_exact_duplicate_coordinate_query_returns_mean_value():
    interp = IDWInterpolator(power=2.0)
    xy = np.array([[0.0, 0.0], [0.0, 0.0], [1.0, 1.0]])
    values = np.array([10.0, 30.0, 100.0])

    # fit should fail with duplicates only in property code path, but interpolator allows it.
    interp.fit(xy, values)
    pred = interp.predict(np.array([[0.0, 0.0]]))

    np.testing.assert_allclose(pred, [20.0], atol=1e-12)


def test_zone_name_lookup_requires_defined_zones(simple_cornerpoint_grid):
    with pytest.raises(ValueError, match="no zones defined"):
        simple_cornerpoint_grid._zone_mask("Upper")


def test_set_zones_rejects_zone_names_without_index(simple_cornerpoint_grid):
    with pytest.raises(ValueError, match="provided without"):
        simple_cornerpoint_grid.set_zones(zone_index=None, zone_names={1: "A"})
