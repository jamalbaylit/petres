from __future__ import annotations

import numpy as np
import pytest

from petres.grids import PillarGrid


def test_from_rectilinear_constructs_expected_shapes(rectilinear_vertices):
    x, y, _ = rectilinear_vertices
    grid = PillarGrid.from_rectilinear(x=x, y=y, top=1000.0, base=1100.0)

    assert grid.vertex_shape == (len(y), len(x))
    assert grid.cell_shape == (len(y) - 1, len(x) - 1)
    assert grid.pillar_top.shape == (len(y), len(x), 3)
    assert grid.pillar_bottom.shape == (len(y), len(x), 3)


def test_to_from_eclipse_coord_roundtrip_preserves_values(simple_pillar_grid):
    coord = simple_pillar_grid.to_eclipse_coord()
    rebuilt = PillarGrid.from_eclipse_coord(coord)

    np.testing.assert_allclose(rebuilt.pillar_top, simple_pillar_grid.pillar_top)
    np.testing.assert_allclose(rebuilt.pillar_bottom, simple_pillar_grid.pillar_bottom)


def test_from_eclipse_coord_rejects_invalid_last_dimension():
    bad = np.zeros((3, 3, 5), dtype=float)
    with pytest.raises(ValueError, match="COORD array must have shape"):
        PillarGrid.from_eclipse_coord(bad)


def test_from_rectilinear_rejects_non_monotonic_x():
    x = np.array([0.0, 10.0, 9.0])
    y = np.array([0.0, 10.0, 20.0])
    with pytest.raises(ValueError, match="strictly increasing"):
        PillarGrid.from_rectilinear(x=x, y=y, top=0.0, base=1.0)


def test_from_rectilinear_rejects_non_finite_vertices():
    x = np.array([0.0, np.nan, 20.0])
    y = np.array([0.0, 10.0, 20.0])
    with pytest.raises(ValueError, match="contains NaN or inf"):
        PillarGrid.from_rectilinear(x=x, y=y, top=0.0, base=1.0)


def test_from_rectilinear_rejects_invalid_z_order():
    x = np.array([0.0, 10.0])
    y = np.array([0.0, 10.0])
    with pytest.raises(ValueError, match="base"):
        PillarGrid.from_rectilinear(x=x, y=y, top=10.0, base=10.0)


def test_from_regular_with_step_sizes_creates_expected_extents():
    grid = PillarGrid.from_regular(xlim=(0.0, 100.0), ylim=(0.0, 80.0), dx=25.0, dy=20.0, top=0.0, base=10.0)

    assert grid.ni == 4
    assert grid.nj == 4
    assert grid.pillar_top[0, 0, 0] == pytest.approx(0.0)
    assert grid.pillar_top[-1, -1, 1] == pytest.approx(80.0)


def test_post_init_rejects_mismatched_top_bottom_shapes():
    top = np.zeros((3, 3, 3), dtype=float)
    bottom = np.zeros((3, 4, 3), dtype=float)
    with pytest.raises(ValueError, match="must have the same shape"):
        PillarGrid(pillar_top=top, pillar_bottom=bottom)
