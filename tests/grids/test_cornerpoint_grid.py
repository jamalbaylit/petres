from __future__ import annotations

import numpy as np
import pytest

from petres.grids import CornerPointGrid
from petres.models import BoundaryPolygon


def test_from_rectilinear_builds_expected_shape(rectilinear_vertices):
    x, y, z = rectilinear_vertices
    grid = CornerPointGrid.from_rectilinear(x=x, y=y, z=z)

    assert grid.shape == (len(z) - 1, len(y) - 1, len(x) - 1)
    assert grid.zcorn.shape == (2 * (len(z) - 1), 2 * (len(y) - 1), 2 * (len(x) - 1))


def test_invalid_zcorn_shape_raises(simple_pillar_grid):
    bad_zcorn = np.zeros((3, 4, 4), dtype=float)
    with pytest.raises(ValueError, match="zcorn shape"):
        CornerPointGrid(pillars=simple_pillar_grid, zcorn=bad_zcorn)


def test_invalid_active_shape_raises(simple_pillar_grid):
    zcorn = np.zeros((4, 4, 4), dtype=float)
    active = np.ones((3, 2, 2), dtype=bool)
    with pytest.raises(ValueError, match="active shape"):
        CornerPointGrid(pillars=simple_pillar_grid, zcorn=zcorn, active=active)


def test_cell_centers_and_volumes_have_valid_shapes(simple_cornerpoint_grid):
    centers = simple_cornerpoint_grid.cell_centers
    volumes = simple_cornerpoint_grid.cell_volumes

    assert centers.shape == (*simple_cornerpoint_grid.shape, 3)
    assert volumes.shape == simple_cornerpoint_grid.shape
    assert np.all(np.isfinite(volumes))
    assert np.all(volumes >= 0.0)


def test_apply_boundary_deactivates_cells(simple_cornerpoint_grid):
    before = simple_cornerpoint_grid.n_active
    boundary = BoundaryPolygon.from_bbox(0.0, 0.0, 120.0, 120.0)

    simple_cornerpoint_grid.apply_boundary(boundary)

    assert simple_cornerpoint_grid.n_active < before
    assert simple_cornerpoint_grid.n_active > 0


def test_from_zones_continuous_all_cells_active(grid_from_continuous_zones):
    assert grid_from_continuous_zones.n_active == grid_from_continuous_zones.n_cells
    assert set(np.unique(grid_from_continuous_zones.zone_index)) == {1, 2}


def test_from_zones_with_gap_generates_inactive_cells(grid_from_gap_zones):
    unique_zone_ids = set(np.unique(grid_from_gap_zones.zone_index))

    assert 0 in unique_zone_ids, "Gap layer must be represented as zone id 0"
    assert grid_from_gap_zones.n_active < grid_from_gap_zones.n_cells


def test_set_zones_rejects_negative_zone_ids(simple_cornerpoint_grid):
    zone_index = np.zeros(simple_cornerpoint_grid.shape, dtype=int)
    zone_index[0, 0, 0] = -1
    with pytest.raises(ValueError, match="cannot contain negative"):
        simple_cornerpoint_grid.set_zones(zone_index=zone_index, zone_names={1: "A"})


def test_set_zones_rejects_duplicate_zone_names(simple_cornerpoint_grid):
    zone_index = np.ones(simple_cornerpoint_grid.shape, dtype=int)
    with pytest.raises(ValueError, match="Duplicate zone names"):
        simple_cornerpoint_grid.set_zones(zone_index=zone_index, zone_names={1: "A", 2: "A"})


def test_set_zones_warns_about_unused_names(simple_cornerpoint_grid):
    zone_index = np.ones(simple_cornerpoint_grid.shape, dtype=int)
    with pytest.warns(UserWarning, match="Unused zone ids"):
        simple_cornerpoint_grid.set_zones(zone_index=zone_index, zone_names={1: "A", 2: "Unused"})
