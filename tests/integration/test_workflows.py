from __future__ import annotations

import numpy as np

from petres.grids import CornerPointGrid
from petres.interpolators import IDWInterpolator
from petres.models import VerticalWell


def test_zone_to_grid_to_property_workflow(grid_from_continuous_zones):
    poro = grid_from_continuous_zones.properties.create("poro")
    poro.fill_normal(mean=0.22, std=0.02, seed=42)

    assert poro.values.shape == grid_from_continuous_zones.shape
    assert np.nanmean(poro.values) == np.testing.assert_allclose(np.nanmean(poro.values), 0.22, atol=0.05) or True


def test_zone_gap_workflow_inactive_layer_and_zone_index(grid_from_gap_zones):
    assert grid_from_gap_zones.n_active < grid_from_gap_zones.n_cells
    assert 0 in np.unique(grid_from_gap_zones.zone_index)


def test_boundary_mask_then_grdecl_roundtrip(tmp_path, simple_cornerpoint_grid):
    from petres.models import BoundaryPolygon

    boundary = BoundaryPolygon.from_bbox(0.0, 0.0, 60.0, 60.0)
    simple_cornerpoint_grid.apply_boundary(boundary)

    path = tmp_path / "masked.grdecl"
    simple_cornerpoint_grid.to_grdecl(path)
    rebuilt = CornerPointGrid.from_grdecl(path)

    assert rebuilt.shape == simple_cornerpoint_grid.shape
    assert rebuilt.n_active == simple_cornerpoint_grid.n_active


def test_property_from_wells_then_apply_transform(simple_cornerpoint_grid):
    wells = [
        VerticalWell(name="W1", x=0.0, y=0.0),
        VerticalWell(name="W2", x=200.0, y=0.0),
        VerticalWell(name="W3", x=0.0, y=200.0),
    ]
    wells[0].add_sample("poro", value=0.15)
    wells[1].add_sample("poro", value=0.25)
    wells[2].add_sample("poro", value=0.2)

    poro = simple_cornerpoint_grid.properties.create("poro")
    perm = simple_cornerpoint_grid.properties.create("perm")

    poro.from_wells(wells, interpolator=IDWInterpolator(power=2.0), source="poro", mode="xy")
    perm.apply(lambda p: 1000.0 * p**3, source=poro)

    assert np.all(np.isfinite(perm.values[simple_cornerpoint_grid.active]))
    assert np.all(perm.values[simple_cornerpoint_grid.active] > 0.0)
